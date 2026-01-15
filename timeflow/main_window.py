from __future__ import annotations
import os

from PySide6.QtCore import QSettings, Qt, QSignalBlocker, QUrl, QSize, QTimer, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QBoxLayout, 
    QAbstractItemView, QApplication, QMessageBox
)
from .i18n import get_strings
from .timer_engine import TimerEngine, TimerState
from .segments_model import SegmentsModel, Segment
from .utils import format_mmss, clamp, resource_path
from .views import SegmentsView, TimerView
from .updater import UpdateWorker
from .help_window import HelpWindow
from .noise_meter_window import NoiseMeterWindow
from .datetime_window import DateTimeWindow
from .styles import (
    TINY_WIDTH_LIMIT, TINY_HEIGHT_LIMIT, 
    COMPACT_WIDTH_LIMIT, COMPACT_HEIGHT_LIMIT,
    MARGIN_STD, MARGIN_COMPACT, 
    SPACING_STD, SPACING_COMPACT,
    get_stylesheet
)
from PySide6.QtGui import QFont, QDesktopServices, QGuiApplication, QPalette
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class MainWindow(QWidget):
    start_download_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("TimeFlowMain")

        self.settings = QSettings("TimeFlow", "TimeFlow")
        self.engine = TimerEngine()
        self.segments_model = SegmentsModel()
        
        self._last_focus_size = QSize(TINY_WIDTH_LIMIT, 450) 
        self.help_window = None 
        self.noise_window = None 
        self.date_window = None

        # --- Sound Setup ---
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        wav_path = resource_path(os.path.join("timeflow_assets", "alert.wav"))
        self.wav_path = os.path.normpath(wav_path)
        self.player.setSource(QUrl.fromLocalFile(self.wav_path))
        self.audio_output.setVolume(1.0)
        self.engine.finished.connect(self.play_alarm)

        # --- Updater Setup ---
        if os.environ.get("TIMEFLOW_SKIP_UPDATER") != "1":
            self._setup_updater()
        else:
            self.update_thread = None

        # --- UI Setup ---
        self._setup_theme()
        
        # 1. Update Button (Links)
        self.update_btn = QPushButton("🚀")
        self.update_btn.setVisible(False) 
        self.update_btn.setToolTip("Update verfügbar!")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                border: 1px solid #059669;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 6px 10px;
                min-width: 30px;
                margin-right: 5px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.update_btn.clicked.connect(self.on_update_clicked)
        self._pending_update_url = None

        # 2. Readme Button (Links)
        self.readme_btn = QPushButton("📑")
        self.readme_btn.setToolTip("Hilfe / Anleitung")
        self.readme_btn.setFixedWidth(40)
        self.readme_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: #636366;
                font-size: 20px; 
                border: none;
                border-radius: 8px; 
            }
            QPushButton:hover { 
                background: rgba(0,0,0,0.05); 
                color: #000;
            }
        """)
        self.readme_btn.clicked.connect(self.on_readme_clicked)

        # 3. Bug Report Button (Links)
        self.bug_btn = QPushButton("🐞")
        self.bug_btn.setToolTip("Fehler melden")
        self.bug_btn.setFixedWidth(40)
        self.bug_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: #636366;
                font-size: 20px; 
                border: none;
                border-radius: 8px; 
            }
            QPushButton:hover { 
                background: rgba(0,0,0,0.05); 
                color: #000;
            }
        """)
        self.bug_btn.clicked.connect(self.on_bug_report_clicked)

        # 4. Date & Time Button (Neu)
        self.date_btn = QPushButton("📅")
        self.date_btn.setToolTip("Datum & Uhrzeit")
        self.date_btn.setFixedWidth(40)
        self.date_btn.setObjectName("HeaderBtn")
        self.date_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: #636366;
                font-size: 20px; 
                border: none;
                border-radius: 8px; 
            }
            QPushButton:hover { 
                background: rgba(0,0,0,0.05); 
                color: #000;
            }
        """)
        self.date_btn.clicked.connect(self.on_date_clicked)

        # 5. Noise Meter Button
        self.noise_btn = QPushButton("🎤")
        self.noise_btn.setToolTip("Lärmampel")
        self.noise_btn.setFixedWidth(40)
        self.noise_btn.setObjectName("HeaderBtn")
        self.noise_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: #636366;
                font-size: 20px; 
                border: none;
                border-radius: 8px; 
            }
            QPushButton:hover { 
                background: rgba(0,0,0,0.05); 
                color: #000;
            }
        """)
        self.noise_btn.clicked.connect(self.on_noise_clicked)

        # 5. Pin & Focus Buttons (Rechts)
        self.pin_btn = QPushButton("📍")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setObjectName("PinBtn")
        self.pin_btn.setFixedWidth(40)

        self.focus_btn = QPushButton()
        self.focus_btn.setCheckable(True)
        self.focus_btn.setObjectName("FocusBtn") 
        
        # Top Row Layout - Extras Links | Tools & Window Controls Rechts
        top_row = QHBoxLayout()
        top_row.addWidget(self.update_btn) # Ganz links 
        top_row.addWidget(self.readme_btn)
        top_row.addWidget(self.bug_btn)
        top_row.addStretch(1)              # Platzhalter in der Mitte
        
        # Tools (Rechts gruppiert)
        top_row.addWidget(self.date_btn)   # Rechts 0
        top_row.addWidget(self.noise_btn)  # Rechts 1
        top_row.addWidget(self.pin_btn)    # Rechts 2
        top_row.addSpacing(10)
        top_row.addWidget(self.focus_btn)  # Rechts 3
        top_row.setContentsMargins(0, 0, 4, 0)

        self.segments_view = SegmentsView(self.segments_model)
        self.timer_view = TimerView()

        self.cards_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.cards_layout.setSpacing(SPACING_STD) 
        self.cards_layout.addWidget(self.segments_view, 1)
        self.cards_layout.addWidget(self.timer_view, 1)

        self.root = QVBoxLayout(self)
        # Reduced margins: top=2, sides=10, bottom=10, spacing=6
        self.root.setContentsMargins(10, 2, 10, 10)
        self.root.setSpacing(6)
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
        self.timer_view.btn_prev.clicked.connect(self.on_skip_prev)
        self.timer_view.btn_next.clicked.connect(self.on_skip_next)

        self.focus_btn.toggled.connect(self.on_focus_toggled)
        self.pin_btn.toggled.connect(self.on_pin_toggled)

        self.engine.tick.connect(self.on_tick)
        self.segments_model.dataChanged.connect(lambda *_: self.on_segments_changed())
        self.segments_model.modelReset.connect(lambda: self.on_segments_changed())
        self.segments_model.rowsInserted.connect(lambda *_: self.on_segments_changed())
        self.segments_model.rowsRemoved.connect(lambda *_: self.on_segments_changed())
        self.segments_model.rowsMoved.connect(lambda *_: self.on_segments_changed())

        # --- Init ---
        self._ensure_localized_defaults(saved_lang)
        self.apply_language(saved_lang, initial=True)
        
        # Load Stylesheet with Asset Path and Theme
        self.refresh_theme()

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

    # --- Readme / Help ---
    def on_readme_clicked(self):
        """Öffnet das integrierte Hilfe-Fenster (Dialog)."""
        if self.help_window is None:
            self.help_window = HelpWindow(self)
        
        # Fenster neu laden und anzeigen
        # Da wir jetzt die robuste Klasse verwenden, ist das Laden in __init__ passiert,
        # aber wir können es bei Bedarf refreshen.
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    def on_bug_report_clicked(self):
        """Öffnet den Google Docs Link zum Melden von Fehlern."""
        url = "https://docs.google.com/document/d/1_tjE5-Xp1QtiKLHuTwQOFggJ29PdfzfS1wc3SaLrjCs/edit?tab=t.0"
        QDesktopServices.openUrl(QUrl(url))

    def on_noise_clicked(self):
        """Öffnet das Fenster für den Lärmwächter."""
        if self.noise_window is None:
            self.noise_window = NoiseMeterWindow(self, self.current_lang())
            # Initiales Theme setzen
            self.noise_window.refresh_theme(self.is_dark_mode())
        
        self._toggle_window(self.noise_window)

    def on_date_clicked(self):
        """Öffnet das Fenster für Datum & Uhrzeit."""
        if self.date_window is None:
            self.date_window = DateTimeWindow(None, self.current_lang())
            self.date_window.refresh_theme(self.is_dark_mode())
        
        self._toggle_window(self.date_window)

    def _toggle_window(self, window):
        """Hilfsmethode zum Umschalten von Zusatzfenstern."""
        if window.isVisible():
            window.hide()
        else:
            window.show()
            window.raise_()
            window.activateWindow()

    # --- Theme Logic ---
    def _setup_theme(self):
        """Initialisiert die Theme-Überwachung."""
        hints = QGuiApplication.styleHints()
        hints.colorSchemeChanged.connect(self.refresh_theme)

    def is_dark_mode(self) -> bool:
        """Prüft ob das System im Dark Mode ist."""
        return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark

    def refresh_theme(self):
        """Aktualisiert das Stylesheet basierend auf dem aktuellen System-Theme."""
        is_dark = self.is_dark_mode()
        arrow_path = resource_path(os.path.join("timeflow_assets", "arrow_down.svg"))
        self.setStyleSheet(get_stylesheet(arrow_path, is_dark))
        
        if self.noise_window:
            self.noise_window.refresh_theme(is_dark)
        
        if self.date_window:
            self.date_window.refresh_theme(is_dark)
        
        if self.help_window:
            # Das Hilfe-Fenster nutzt Standard-HTML, wir könnten es hier auch updaten
            pass

    # --- Updater Logic ---
    def _setup_updater(self):
        self.update_thread = QThread()
        self.worker = UpdateWorker()
        self.worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.worker.check_updates)
        self.worker.updateAvailable.connect(self.on_update_available)
        self.worker.downloadProgress.connect(self.on_download_progress)
        self.worker.downloadFinished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_updater_error)
        self.start_download_signal.connect(self.worker.start_download)
        self.update_thread.start()

    def on_update_available(self, version_tag, url, notes):
        self._pending_update_url = url
        self.update_btn.setText(f"🚀 Update {version_tag}")
        self.update_btn.setVisible(True)

    def on_update_clicked(self):
        if self._pending_update_url:
            self.update_btn.setEnabled(False)
            self.update_btn.setText("0%")
            self.start_download_signal.emit(self._pending_update_url)

    def on_download_progress(self, percent):
        self.update_btn.setText(f"{percent}%")

    def on_download_finished(self, path):
        self.update_btn.setText("✅")
        QMessageBox.information(self, "Download fertig", f"Datei gespeichert unter:\n{path}")
        folder = os.path.dirname(path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
        self.update_btn.setVisible(False)

    def on_updater_error(self, msg):
        if not self.update_btn.isEnabled(): 
            self.update_btn.setEnabled(True)
            self.update_btn.setText("❌ Retry")
            print(f"Update Fehler: {msg}")

    def closeEvent(self, event):
        if self.update_thread:
            self.update_thread.quit()
            self.update_thread.wait()
        if self.help_window:
            self.help_window.close()
        super().closeEvent(event)

    # --- Standard Methods ---
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
        compact_mode = (w < COMPACT_WIDTH_LIMIT) 
        focus_active = self.focus_btn.isChecked()

        if is_tiny:
            self.segments_view.setVisible(False)
            self.focus_btn.setVisible(False)
            self.pin_btn.setVisible(False)
            self.readme_btn.setVisible(False) 
            self.bug_btn.setVisible(False)
            self.update_btn.setVisible(False)
            self.noise_btn.setVisible(False)
        else:
            self.segments_view.setVisible(not focus_active)
            self.focus_btn.setVisible(True)
            self.pin_btn.setVisible(True)
            
            # Optionale Buttons nur anzeigen, wenn NICHT im Fokus-Modus
            extras_visible = not focus_active
            self.date_btn.setVisible(extras_visible)
            self.readme_btn.setVisible(extras_visible)
            self.bug_btn.setVisible(extras_visible)
            self.noise_btn.setVisible(extras_visible)
            self.update_btn.setVisible(extras_visible and bool(self._pending_update_url))

        if self.segments_view.isVisible() and compact_mode:
            self.cards_layout.setDirection(QBoxLayout.TopToBottom)
        else:
            self.cards_layout.setDirection(QBoxLayout.LeftToRight)

        margin = MARGIN_COMPACT if is_tiny else 10  # Reduced side margins
        spacing = SPACING_COMPACT if is_tiny else 6  # Reduced spacing
        self.root.setContentsMargins(margin, 2, margin, margin)  # Reduced top margin
        self.root.setSpacing(spacing)

        self.timer_view.set_tiny_mode(is_tiny, self.current_lang())
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
        old_lang = self.settings.value("language", "de")
        new_lang = self.current_lang()
        self.settings.setValue("language", new_lang)
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
        
        if self.noise_window:
            self.noise_window.retranslate(lang_code)
        if self.date_window:
            self.date_window.retranslate(lang_code)
            
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
        self.segments_model.setData(self.segments_model.index(row, 0), s.new_segment, Qt.EditRole)
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

    def on_skip_prev(self):
        elapsed = self.engine.elapsed_seconds()
        segs = self.segments_model.segments()
        t = 0.0
        target = 0.0
        for i, seg in enumerate(segs):
            dur = max(0.0, seg.minutes) * 60.0
            if elapsed < t + dur + 0.1: # Current segment
                # If more than 2 seconds passed in current segment, go to start of current
                if (elapsed - t) > 2.0:
                    target = t
                elif i > 0:
                    # Go to previous segment start
                    prev_dur = max(0.0, segs[i-1].minutes) * 60.0
                    target = max(0.0, t - prev_dur)
                else:
                    target = 0.0
                break
            t += dur
        self.engine.seek(target)

    def on_skip_next(self):
        elapsed = self.engine.elapsed_seconds()
        segs = self.segments_model.segments()
        t = 0.0
        target = self.segments_model.total_seconds()
        for i, seg in enumerate(segs):
            dur = max(0.0, seg.minutes) * 60.0
            if elapsed < t + dur - 0.1:
                # Target is the start of the next segment
                target = t + dur
                break
            t += dur
        self.engine.seek(target)

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