from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableView, QAbstractItemView, QComboBox, QSizePolicy, QHeaderView,
    QMessageBox
)
from PySide6.QtGui import QFont, QResizeEvent

from .pie_widget import PieWidget
from .delegates import MinutesDelegate
from .i18n import SUPPORTED_LANGS, get_strings
from .utils import format_mmss, clamp
from .styles import *
from .presets_manager import PresetsManager
from .presets_dialog import SavePresetDialog, ManagePresetsDialog

class Card(QFrame):
    def __init__(self, title: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")
        # WICHTIG: Standardmäßig immer "Box-Look" (Weiß mit Rand). 
        # Das verhindert Glitches beim Umschalten.
        self.setProperty("compact", False) 
        
        self._title = QLabel(title)
        self._title.setObjectName("CardTitle")

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(20, 20, 20, 20)
        self._root.setSpacing(16)
        
        if title:
            self._root.addWidget(self._title)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def body_layout(self) -> QVBoxLayout:
        return self._root
    
    def set_compact_mode(self, is_compact: bool):
        # Wir nutzen diese Funktion nur noch für CSS-Logik, falls nötig.
        # Aber wir vermeiden das flackernde Umschalten des Hintergrunds.
        self.setProperty("compact", is_compact)
        self.style().unpolish(self)
        self.style().polish(self)

class SegmentsView(Card):
    def __init__(self, model):
        super().__init__("Segments")
        self.model = model
        self.presets_manager = PresetsManager()

        # Setup Container (Sprache/Modus)
        self.setup_container = QWidget()
        self.setup_layout = QGridLayout(self.setup_container)
        self.setup_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_layout.setSpacing(12)

        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        for code, label in SUPPORTED_LANGS:
            self.language_combo.addItem(label, userData=code)

        self.mode_label = QLabel()
        self.mode_combo = QComboBox()
        self.mode_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.mode_combo.addItem("Count down", userData="countdown")
        self.mode_combo.addItem("Count up", userData="countup")

        self.setup_layout.addWidget(self.language_label, 0, 0)
        self.setup_layout.addWidget(self.language_combo, 0, 1)
        self.setup_layout.addWidget(self.mode_label, 0, 2)
        self.setup_layout.addWidget(self.mode_combo, 0, 3)
        
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setDragEnabled(True)
        self.view.setAcceptDrops(True)
        self.view.setDragDropMode(QAbstractItemView.InternalMove)
        self.view.setDropIndicatorShown(True)
        self.view.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.view.verticalHeader().setVisible(False)
        self.view.setObjectName("SegmentsTable")
        self.view.setItemDelegateForColumn(1, MinutesDelegate(self.view))
        self.view.setShowGrid(False)
        self.view.setAlternatingRowColors(False)

        self.btn_add = QPushButton()
        self.btn_remove = QPushButton()
        self.btn_save = QPushButton()
        self.btn_load = QPushButton()
        
        text_btn_style = """
            QPushButton { 
                font-size: 13px; 
                font-weight: 600; 
                border-radius: 8px; 
                padding: 6px 16px; 
            }
        """
        self.btn_add.setStyleSheet(text_btn_style)
        self.btn_remove.setStyleSheet(text_btn_style)
        self.btn_save.setStyleSheet(text_btn_style)
        self.btn_load.setStyleSheet(text_btn_style)
        
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_remove)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_load)

        # Connect Preset Buttons
        self.btn_save.clicked.connect(self.save_preset)
        self.btn_load.clicked.connect(self.load_presets)

        self.body_layout().addWidget(self.setup_container)
        self.body_layout().addWidget(self.view, 1)
        self.body_layout().addLayout(btn_row)

    def retranslate(self, lang_code: str):
        s = get_strings(lang_code)
        self._title.setText(s.segments_label)
        self.language_label.setText(f"{s.language_label}:")
        self.mode_label.setText(f"{s.mode_label}:")
        self.mode_combo.setItemText(0, s.mode_countdown)
        self.mode_combo.setItemText(1, s.mode_countup)
        
        self.btn_add.setText(f"➕ {s.add_segment}")
        self.btn_remove.setText(f"➖ {s.remove_segment}")
        self.btn_save.setText(f"💾 {s.save_preset}")
        self.btn_load.setText(f"📂 {s.presets_label}")
        
        self.btn_save.setToolTip(s.save_preset)
        self.btn_load.setToolTip(s.manage_presets)
        
        self.model.set_headers(s.col_name, s.col_minutes)

    def save_preset(self):
        lang_code = self.language_combo.currentData()
        s = get_strings(lang_code)
        dlg = SavePresetDialog(self, lang_code)
        if dlg.exec():
            name = dlg.preset_name
            if name:
                segments = self.model.segments()
                data = [{"name": seg.name, "minutes": seg.minutes} for seg in segments]
                self.presets_manager.save_preset(name, data)
                QMessageBox.information(self, s.app_title, s.preset_saved)

    def load_presets(self):
        lang_code = self.language_combo.currentData()
        s = get_strings(lang_code)
        dlg = ManagePresetsDialog(self.presets_manager, self, lang_code)
        if dlg.exec():
            loaded = dlg.loaded_segments
            if loaded:
                from .segments_model import Segment
                new_segs = []
                for d in loaded:
                    if isinstance(d, dict):
                        new_segs.append(Segment(d["name"], d["minutes"]))
                    elif isinstance(d, (list, tuple)) and len(d) >= 2:
                        new_segs.append(Segment(d[0], d[1]))
                if new_segs:
                    self.model.set_segments(new_segs)
                    QMessageBox.information(self, s.app_title, s.preset_loaded)

    def update_layout_sizing(self, compact: bool):
        # SegmentsView schalten wir optisch um (Header kleiner etc.)
        self.set_compact_mode(compact)
        
        if compact:
            self.language_label.setVisible(False)
            self.mode_label.setVisible(False)
            self.view.verticalHeader().setDefaultSectionSize(40)
            self.view.setColumnWidth(1, 80)
        else:
            self.language_label.setVisible(True)
            self.mode_label.setVisible(True)
            self.view.verticalHeader().setDefaultSectionSize(46)
            self.view.setColumnWidth(1, 100)
            
        hh = self.view.horizontalHeader()
        hh.setStretchLastSection(False)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.Fixed)


class TimerView(Card):
    def __init__(self):
        super().__init__("") 
        
        self.time_label = QLabel("00:00")
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        # FIX: Korrekter Name ist "Ignored", nicht "Ignoring"
        self.time_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        self.time_caption = QLabel()
        self.time_caption.setObjectName("TimeCaption")
        self.time_caption.setAlignment(Qt.AlignCenter)

        self.current_segment_label = QLabel("")
        self.current_segment_label.setObjectName("CurrentSegment")
        self.current_segment_label.setAlignment(Qt.AlignCenter)
        self.current_segment_label.setWordWrap(True)

        self.next_segment_label = QLabel("")
        self.next_segment_label.setObjectName("NextSegment")
        self.next_segment_label.setAlignment(Qt.AlignCenter)
        self.next_segment_label.setWordWrap(True)

        self.pie = PieWidget()
        self.pie.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.btn_start = QPushButton("▶️")
        self.btn_pause = QPushButton("⏸️")
        self.btn_reset = QPushButton("🔄")
        self.btn_prev = QPushButton("⏮️")
        self.btn_next = QPushButton("⏭️")

        self.ctrl_row = QHBoxLayout()
        self.ctrl_row.setSpacing(12)
        self.ctrl_row.addWidget(self.btn_prev)
        self.ctrl_row.addWidget(self.btn_start)
        self.ctrl_row.addWidget(self.btn_pause)
        self.ctrl_row.addWidget(self.btn_next)
        self.ctrl_row.addWidget(self.btn_reset)

        # Layout Aufbau mit Stretch Factors
        self.body_layout().addStretch(1)
        self.body_layout().addWidget(self.time_label)
        self.body_layout().addWidget(self.time_caption)
        self.body_layout().addSpacing(10)
        self.body_layout().addWidget(self.current_segment_label)
        self.body_layout().addWidget(self.next_segment_label)
        self.body_layout().addSpacing(10)
        self.body_layout().addWidget(self.pie, 10) 
        self.body_layout().addSpacing(10)
        self.body_layout().addLayout(self.ctrl_row)
        self.body_layout().addStretch(1)

    def update_display(self, text_time: str, text_caption: str, text_current: str, text_next: str):
        self.time_label.setText(text_time)
        self.time_caption.setText(text_caption)
        self.current_segment_label.setText(text_current)
        self.next_segment_label.setText(text_next)
        
        # Nur anzeigen, wenn Text da ist UND wir nicht im Tiny-Mode sind
        if self.next_segment_label.isVisible():
            self.next_segment_label.setVisible(bool(text_next))

    def set_tiny_mode(self, tiny: bool, lang_code: str):
        s = get_strings(lang_code)
        
        self.btn_start.setToolTip(s.start)
        self.btn_pause.setToolTip(s.pause)
        self.btn_reset.setToolTip(s.reset)
        self.btn_prev.setToolTip(s.prev_segment if hasattr(s, 'prev_segment') else "Previous")
        self.btn_next.setToolTip(s.next_segment if hasattr(s, 'next_segment') else "Next")

        # Wir blenden nur Elemente aus, ändern aber nicht den Card-Style
        if tiny:
            self.time_caption.hide()
            self.current_segment_label.hide()
            self.next_segment_label.hide()
        else:
            self.time_caption.show()
            self.current_segment_label.show()
            if self.next_segment_label.text():
                self.next_segment_label.show()
        
        self.updateGeometry()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        
        # Dynamische Berechnung basierend auf EIGENER Höhe
        h = self.height()
        
        # Typografie-Regeln
        time_px = int(clamp(h * 0.18, 40, 110))
        caption_px = int(clamp(h * 0.035, 11, 16))
        current_px = int(clamp(h * 0.045, 13, 24))
        next_px = int(clamp(h * 0.035, 11, 16))

        # Fonts anwenden
        f = QFont()
        f.setPixelSize(time_px)
        f.setWeight(QFont.Weight.Bold)
        self.time_label.setFont(f)

        fc = QFont()
        fc.setPixelSize(caption_px)
        fc.setWeight(QFont.Weight.Medium)
        self.time_caption.setFont(fc)

        fcur = QFont()
        fcur.setPixelSize(current_px)
        fcur.setWeight(QFont.Weight.Bold)
        self.current_segment_label.setFont(fcur)

        fnext = QFont()
        fnext.setPixelSize(next_px)
        self.next_segment_label.setFont(fnext)