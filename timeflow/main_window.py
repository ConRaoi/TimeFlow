from __future__ import annotations
import os

from PySide6.QtCore import QSettings, Qt, QSignalBlocker, QUrl, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QBoxLayout, 
    QAbstractItemView, QApplication
)
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from .i18n import get_strings
from .timer_engine import TimerEngine, TimerState
from .segments_model import SegmentsModel, Segment
from .utils import format_mmss, clamp, resource_path
from .views import SegmentsView, TimerView

# FIX: Importiert jetzt die korrekten Konstanten aus styles.py
from .styles import (
    TINY_WIDTH_LIMIT, TINY_HEIGHT_LIMIT, 
    COMPACT_WIDTH_LIMIT, COMPACT_HEIGHT_LIMIT,
    MARGIN_STD, MARGIN_COMPACT, 
    SPACING_STD, SPACING_COMPACT,
    SCALE_BASE_W, SCALE_BASE_H
)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # FIX: ObjectName setzen für CSS-Targeting (verhindert graue Hintergründe in Child-Widgets)
        self.setObjectName("TimeFlowMain")

        self.settings = QSettings("TimeFlow", "TimeFlow")
        self.engine = TimerEngine()
        self.segments_model = SegmentsModel()
        
        self._last_focus_size = QSize(TINY_WIDTH_LIMIT, 450) 

        # --- Sound Setup ---
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        wav_path = resource_path(os.path.join("timeflow_assets", "alert.wav"))
        self.wav_path = os.path.normpath(wav_path)
        self.player.setSource(QUrl.fromLocalFile(self.wav_path))
        self.audio_output.setVolume(1.0)
        self.engine.finished.connect(self.play_alarm)

        # --- UI Setup ---
        self.pin_btn = QPushButton("📍")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setObjectName("PinBtn")
        self.pin_btn.setToolTip("Always on Top")
        self.pin_btn.setFixedWidth(40)

        self.focus_btn = QPushButton()
        self.focus_btn.setCheckable(True)
        self.focus_btn.setObjectName("FocusBtn") 
        
        top_row = QHBoxLayout()
        top_row.addStretch(1)
        top_row.addWidget(self.pin_btn)
        top_row.addSpacing(10)
        top_row.addWidget(self.focus_btn)
        top_row.setContentsMargins(0, 0, 4, 0) 

        self.segments_view = SegmentsView(self.segments_model)
        self.timer_view = TimerView()

        self.cards_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.cards_layout.setSpacing(SPACING_STD) 
        self.cards_layout.addWidget(self.segments_view, 1)
        self.cards_layout.addWidget(self.timer_view, 1)

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(MARGIN_STD, MARGIN_STD, MARGIN_STD, MARGIN_STD)
        self.root.setSpacing(SPACING_STD)
        self.root.addLayout(top_row)
        self.root.addLayout(self.cards_layout, 1)

        # --- Load Settings ---
        saved_lang = self.settings.value("language", "de")
        self._set_combo_to_lang(saved_lang)

        saved_mode = self.settings.value("mode", "countdown")
        self._set_combo_to_mode(saved_mode)

        focus_only = str(self.settings.value("focus_only", "true")).lower() == "true"
        self.focus_btn.setChecked(focus_only)

        pin_checked = str(self.settings.value("always_on_top", "false")).lower() == "true"
        self.pin_btn.setChecked(pin_checked)
        self.on_pin_toggled(pin_checked)

        # --- Connect Signals ---
        self.segments_view.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.segments_view.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        self.segments_view.btn_add.clicked.connect(self.add_segment)
        self.segments_view.btn_remove.clicked.connect(self.remove_selected_segment)

        self.timer_view.btn_start.clicked.connect(self.engine.start)
        self.timer_view.btn_pause.clicked.connect(self.engine.pause)
        self.timer_view.btn_reset.clicked.connect(self.on_reset)

        self.focus_btn.toggled.connect(self.on_focus_toggled)
        self.pin_btn.toggled.connect(self.on_pin_toggled)

        self.engine.tick.connect(self.on_tick)
        self.segments_model.dataChanged.connect(lambda *_: self.on_segments_changed())
        self.segments_model.rowsInserted.connect(lambda *_: self.on_segments_changed())
        self.segments_model.rowsRemoved.connect(lambda *_: self.on_segments_changed())
        self.segments_model.rowsMoved.connect(lambda *_: self.on_segments_changed())

        # --- Init ---
        self._ensure_localized_defaults(saved_lang)
        self.apply_language(saved_lang, initial=True)
        
        self.on_segments_changed()
        self.on_tick(self._make_state_for_ui())
        
        if focus_only:
            self.segments_view.setVisible(False)
            self.setMinimumSize(300, 400)
            self.resize(350, 500)
        else:
            self.segments_view.setVisible(True)
            self.setMinimumSize(600, 500)
            self.resize(900, 600)

        QTimer.singleShot(50, self._apply_responsive)

    def play_alarm(self):
        self.player.setPosition(0)
        self.player.play()
        if not os.path.exists(self.wav_path):
            QApplication.beep()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._apply_responsive()

    def _apply_responsive(self) -> None:
        w = self.width()
        h = self.height()
        
        is_tiny = (w < TINY_WIDTH_LIMIT) or (h < TINY_HEIGHT_LIMIT)
        # FIX: Nutzung der korrekten Konstante
        compact_mode = (w < COMPACT_WIDTH_LIMIT) 
        focus_active = self.focus_btn.isChecked()

        # 1. Sichtbarkeit
        if is_tiny:
            self.segments_view.setVisible(False)
            self.focus_btn.setVisible(False)
            self.pin_btn.setVisible(False)
        else:
            self.segments_view.setVisible(not focus_active)
            self.focus_btn.setVisible(True)
            self.pin_btn.setVisible(True)

        # 2. Layout Richtung
        if self.segments_view.isVisible() and compact_mode:
            self.cards_layout.setDirection(QBoxLayout.TopToBottom)
        else:
            self.cards_layout.setDirection(QBoxLayout.LeftToRight)

        # 3. Margins
        margin = MARGIN_COMPACT if is_tiny else MARGIN_STD
        spacing = SPACING_COMPACT if is_tiny else SPACING_STD
        self.root.setContentsMargins(margin, margin, margin, margin)
        self.root.setSpacing(spacing)

        # 4. Updates
        scale = clamp(h / 600.0, 0.6, 1.3)
        self.timer_view.set_tiny_mode(is_tiny, self.current_lang())
        self.timer_view.update_typography(w, h, scale)
        self.segments_view.update_layout_sizing(compact_mode)
        self._update_focus_button_text()

    def on_pin_toggled(self, checked: bool) -> None:
        self.settings.setValue("always_on_top", "true" if checked else "false")
        flag = Qt.WindowStaysOnTopHint
        self.setWindowFlag(flag, checked)
        self.show()

    def on_focus_toggled(self, checked: bool) -> None:
        self.settings.setValue("focus_only", "true" if checked else "false")
        
        if not checked:
            self._last_focus_size = self.size()
            self.segments_view.setVisible(True)
            self.setMinimumSize(600, 500)
            self.resize(900, 600)
        else:
            self.segments_view.setVisible(False)
            self.setMinimumSize(250, 250)
            target = self._last_focus_size if self._last_focus_size.isValid() else QSize(350, 500)
            self.resize(target)
            
        QTimer.singleShot(10, self._apply_responsive)

    def current_lang(self) -> str: return self.segments_view.language_combo.currentData()
    def current_mode(self) -> str: return self.segments_view.mode_combo.currentData()
    
    def _set_combo_to_lang(self, code: str):
        c = self.segments_view.language_combo
        for i in range(c.count()):
            if c.itemData(i) == code: 
                c.setCurrentIndex(i)
                return
        if c.count(): c.setCurrentIndex(0)

    def _set_combo_to_mode(self, mode: str):
        c = self.segments_view.mode_combo
        for i in range(c.count()):
            if c.itemData(i) == mode: 
                c.setCurrentIndex(i)
                return

    def on_language_changed(self):
        # FIX: Alte Sprache merken, um Segmente intelligent zu übersetzen
        old_lang = self.settings.value("language", "de")
        new_lang = self.current_lang()
        
        self.settings.setValue("language", new_lang)
        
        # Segmente übersetzen, wenn sie noch Originalzustand haben
        self._translate_segments_if_defaults(old_lang, new_lang)

        self.apply_language(new_lang, False)
        self.on_segments_changed()
        self.on_tick(self._make_state_for_ui())

    def on_mode_changed(self):
        self.settings.setValue("mode", self.current_mode())
        self.on_tick(self._make_state_for_ui())

    def apply_language(self, lang_code, initial):
        s = get_strings(lang_code)
        self.setWindowTitle(s.app_title)
        self.segments_view.retranslate(lang_code)
        self.timer_view.set_tiny_mode(False, lang_code)
        self._ensure_localized_defaults(lang_code)
        self._apply_responsive()

    def _update_focus_button_text(self):
        if self.focus_btn.isChecked():
            self.focus_btn.setText("🗂️")
            self.focus_btn.setToolTip("Show Segments")
        else:
            self.focus_btn.setText("⏱️")
            self.focus_btn.setToolTip("Focus Timer")

    def _ensure_localized_defaults(self, lang_code):
        if self.segments_model.rowCount() == 0:
            s = get_strings(lang_code)
            self.segments_model.set_segments([Segment(n, m) for (n, m) in s.default_segments])

    # FIX: Neue Logik für Segment-Übersetzung beim Sprachwechsel
    def _translate_segments_if_defaults(self, old_lang: str, new_lang: str):
        if old_lang == new_lang:
            return

        current_segments = self.segments_model.segments()
        old_defaults = get_strings(old_lang).default_segments
        
        if len(current_segments) != len(old_defaults):
            return

        is_identical = True
        for i, (name, minutes) in enumerate(old_defaults):
            seg = current_segments[i]
            if seg.name != name or abs(seg.minutes - minutes) > 0.001:
                is_identical = False
                break
        
        if is_identical:
            new_defaults = get_strings(new_lang).default_segments
            self.segments_model.set_segments([Segment(n, m) for (n, m) in new_defaults])

    def add_segment(self):
        row = self.segments_model.rowCount()
        self.segments_model.insertRows(row, 1)
        s = get_strings(self.current_lang())
        self.segments_model.setData(self.segments_model.index(row, 0), "Segment", Qt.EditRole)
        self.segments_view.view.selectRow(row)

    def remove_selected_segment(self):
        sel = self.segments_view.view.selectionModel()
        if sel and sel.hasSelection():
            self.segments_model.removeRows(sel.selectedRows()[0].row(), 1)

    def on_segments_changed(self):
        total_s = self.segments_model.total_seconds()
        self.engine.set_total_seconds(total_s)
        self.timer_view.pie.set_segments(self.segments_model.segments())
        self.on_tick(self._make_state_for_ui())

    def on_reset(self):
        self.engine.reset()
        self.on_tick(self._make_state_for_ui())

    def _make_state_for_ui(self):
        return TimerState(False, self.engine.elapsed_seconds(), self.segments_model.total_seconds())

    def on_tick(self, state):
        total = max(0.0, state.total_s)
        elapsed = max(0.0, state.elapsed_s)
        if total > 0: elapsed = min(elapsed, total)
        
        progress = (elapsed / total) if total > 0 else 0.0
        self.timer_view.pie.set_progress(progress)

        s = get_strings(self.current_lang())
        mode = self.current_mode()
        
        text_time = format_mmss(max(0.0, total - elapsed) if mode == "countdown" else elapsed)
        text_caption = s.time_remaining if mode == "countdown" else s.time_elapsed
        
        segs = self.segments_model.segments()
        current_idx = -1
        t = 0.0
        
        for i, seg in enumerate(segs):
            dur = max(0.0, seg.minutes) * 60.0
            if elapsed < t + dur or i == len(segs) - 1:
                current_idx = i
                break
            t += dur
        
        text_current = ""
        text_next = ""
        if 0 <= current_idx < len(segs):
            text_current = f"{s.current_segment} {segs[current_idx].name}"
            if current_idx + 1 < len(segs):
                text_next = f"{s.next_segment} {segs[current_idx+1].name}"
            else:
                text_next = ""
            
            if not self.segments_view.view.state() == QAbstractItemView.EditingState:
                with QSignalBlocker(self.segments_view.view.selectionModel()):
                    self.segments_view.view.selectRow(current_idx)

        self.timer_view.update_display(text_time, text_caption, text_current, text_next)