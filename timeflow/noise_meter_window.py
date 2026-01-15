from PySide6.QtCore import Qt, Signal, QRect, QPoint, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSlider, QFrame, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen

from .audio_processor import AudioProcessor
from .i18n import get_strings
from .styles import get_meter_bg_color
from .noise_presets_manager import NoisePresetsManager
from .presets_dialog import SavePresetDialog, ManagePresetsDialog

class LevelMeterWidget(QWidget):
    """
    Ein Custom Widget das einen LED-Balken visualisiert.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._level = 0.0
        self._threshold = 70.0

    def set_level(self, level: float):
        self._level = level
        self.update()

    def set_threshold(self, threshold: float):
        self._threshold = threshold
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        padding = 6
        
        # Hintergrund mit subtilem Glass-Effekt - Theme-aware
        bg_rect = QRect(padding, padding, w - 2*padding, h - 2*padding)
        is_dark = self.palette().window().color().lightness() < 128
        painter.setBrush(get_meter_bg_color(is_dark))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg_rect, 16, 16)

        # Segmente zeichnen
        num_segments = 25 # Etwas weniger Segmente für "blockigeren" Style
        seg_gap = 4
        seg_w = (w - 2*padding - (num_segments + 1) * seg_gap) / num_segments
        seg_h = h - 2*padding - 16
        
        for i in range(num_segments):
            seg_level = (i / num_segments) * 100
            
            # Farbe bestimmen
            if seg_level >= self._threshold:
                color = QColor("#FF3B30") # Rot
            elif seg_level >= self._threshold * 0.7:
                color = QColor("#FFCC00") # Gelb
            else:
                color = QColor("#34C759") # Grün
                
            # Aktiv?
            if seg_level > self._level:
                color.setAlpha(40) # Transparenter statt nur heller
            
            x = padding + seg_gap + i * (seg_w + seg_gap)
            y = padding + 8
            
            painter.setBrush(color)
            painter.drawRoundedRect(x, y, seg_w, seg_h, 4, 4)

        # Threshold Markierung (Stylischer)
        tx = padding + seg_gap + (self._threshold / 100) * (w - 2*padding - 2*seg_gap)
        painter.setPen(QPen(QColor("#5856D6"), 3, Qt.DashLine))
        painter.drawLine(tx, padding - 2, tx, h - padding + 2)

class NoiseMeterWindow(QFrame):
    """
    Hauptfenster für den Lärmwächter.
    """
    def __init__(self, parent=None, lang_code="de"):
        super().__init__(parent)
        self.setObjectName("Card") # Nutzt den Card-Style
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Noise Meter")
        
        self.lang_code = lang_code
        self.presets_manager = NoisePresetsManager()
        self.processor = AudioProcessor(self)
        self.processor.levelUpdated.connect(self._on_level_updated)
        
        self._setup_ui()
        self._load_last_settings()
        self.retranslate(lang_code)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30) # Mehr Padding
        root.setSpacing(18) # Leichter reduziertes Außen-Spacing, damit Meter mehr Raum erhält

        # Header
        header = QHBoxLayout()
        self.title_label = QLabel("🚦 Noise Meter")
        self.title_label.setObjectName("CardTitle")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 800; padding-bottom: 0;")
        header.addWidget(self.title_label)
        header.addStretch()

        self.btn_presets = QPushButton("💾")
        self.btn_presets.setFixedSize(28, 28)
        self.btn_presets.setStyleSheet("""
            QPushButton {
                background: transparent;
                font-size: 18px;
                border: none;
                border-radius: 6px;
                padding: 0;
            }
            QPushButton:hover { background: rgba(0,0,0,0.05); }
        """)
        self.btn_presets.clicked.connect(self._on_presets_clicked)
        header.addWidget(self.btn_presets)
        root.addLayout(header)

        # Meter
        self.meter = LevelMeterWidget()
        root.addWidget(self.meter)

        # Settings
        settings = QVBoxLayout()
        # Weniger Abstand zwischen Sensitivity und Limit, damit die Slider "nebensächlich" wirken
        settings.setSpacing(8)
        
        # Sensitivity
        sens_row = QHBoxLayout()
        self.sens_label = QLabel("Sensitivity")
        # Kleinere Min-Breite, damit das Label nicht dominant ist
        self.sens_label.setStyleSheet("font-size: 16px; font-weight: 600; min-width: 80px;")
        self.sens_slider = QSlider(Qt.Horizontal)
        self.sens_slider.setRange(1, 100) # 0.1x to 10.0x
        self.sens_slider.setValue(40) # Startet bei 4.0x (solider Mittelwert)
        # Flacherer Slider, weniger auffällig
        self.sens_slider.setMinimumHeight(28)
        self.sens_slider.valueChanged.connect(self._on_sens_changed)
        sens_row.addWidget(self.sens_label)
        sens_row.addWidget(self.sens_slider)
        settings.addLayout(sens_row)

        # Threshold (Limit)
        limit_row = QHBoxLayout()
        self.limit_label = QLabel("Limit")
        self.limit_label.setStyleSheet("font-size: 16px; font-weight: 600; min-width: 80px;")
        self.limit_slider = QSlider(Qt.Horizontal)
        self.limit_slider.setRange(10, 95)
        self.limit_slider.setValue(70)
        self.limit_slider.setMinimumHeight(28)
        self.limit_slider.valueChanged.connect(self._on_limit_changed)
        limit_row.addWidget(self.limit_label)
        limit_row.addWidget(self.limit_slider)
        settings.addLayout(limit_row)

        # Gebe dem Meter mehr vertikalen Platz (größere Stretch-Relation)
        root.addWidget(self.meter, 3)
        root.addLayout(settings, 1)

    def retranslate(self, lang_code: str):
        self.lang_code = lang_code
        s = get_strings(lang_code)
        self.title_label.setText(f"🚦 {s.noise_meter}")
        self.sens_label.setText(s.sensitivity)
        self.limit_label.setText(s.limit)
        self.setWindowTitle(s.noise_meter)

    def refresh_theme(self, is_dark: bool):
        """Aktualisiert die Styles des Fensters bei Theme-Wechsel."""
        # Da wir ObjectNames nutzen, wird das Haupt-Stylesheet von MainWindow 
        # das meiste regeln, aber wir können hier spezifische Anpassungen machen.
        self.update() # Triggert Neurechnen des LevelMeterWidget backgrounds

    def _on_level_updated(self, level: float):
        self.meter.set_level(level)
        # Check limit
        if level >= self.limit_slider.value():
            self.setProperty("alarm", True)
        else:
            self.setProperty("alarm", False)
        
        # Style auffrischen wenn sich Properties ändern (für Alarm-Effekt im CSS möglich)
        # (Hier optional, für Blinken/Farbe)

    def _on_sens_changed(self, value):
        self.processor.set_sensitivity(value / 10.0)
        self._save_last_settings()

    def _on_limit_changed(self, value):
        self.meter.set_threshold(float(value))
        self._save_last_settings()

    def _on_presets_clicked(self):
        """Öffnet das Preset-Menü."""
        from PySide6.QtWidgets import QMenu, QMessageBox
        from PySide6.QtGui import QAction
        
        s = get_strings(self.lang_code)
        menu = QMenu(self)
        
        save_action = QAction(f"💾 {s.save_preset}", self)
        save_action.triggered.connect(self._save_preset)
        
        manage_action = QAction(f"📂 {s.manage_presets}", self)
        manage_action.triggered.connect(self._manage_presets)
        
        menu.addAction(save_action)
        menu.addAction(manage_action)
        
        # Position am Button anzeigen
        menu.exec(self.btn_presets.mapToGlobal(QPoint(0, self.btn_presets.height())))

    def _save_preset(self):
        s = get_strings(self.lang_code)
        dlg = SavePresetDialog(self, self.lang_code)
        if dlg.exec():
            name = dlg.preset_name
            if name:
                self.presets_manager.save_preset(
                    name, 
                    self.sens_slider.value(), 
                    self.limit_slider.value()
                )
                QMessageBox.information(self, s.app_title, s.preset_saved)

    def _manage_presets(self):
        s = get_strings(self.lang_code)
        # data_key="sensitivity" -> actually we want the whole object
        dlg = ManagePresetsDialog(self.presets_manager, self, self.lang_code, data_key="none")
        if dlg.exec():
            # dlg.loaded_data contains {name: ..., sensitivity: ..., limit: ...}
            # because we passed data_key="none" (ManagePresetsDialog refactored to handle this)
            data = dlg.loaded_data
            if data and "sensitivity" in data:
                # Blockieren der Signale während des Ladens um doppeltes Speichern zu vermeiden
                self.sens_slider.blockSignals(True)
                self.limit_slider.blockSignals(True)
                
                self.sens_slider.setValue(data["sensitivity"])
                self.limit_slider.setValue(data["limit"])
                self.processor.set_sensitivity(data["sensitivity"] / 10.0)
                self.meter.set_threshold(float(data["limit"]))
                
                self.sens_slider.blockSignals(False)
                self.limit_slider.blockSignals(False)
                
                QMessageBox.information(self, s.app_title, s.preset_loaded)

    def _save_last_settings(self):
        self.presets_manager.save_last_settings(
            self.sens_slider.value(),
            self.limit_slider.value()
        )

    def _load_last_settings(self):
        sens, limit = self.presets_manager.load_last_settings()
        self.sens_slider.setValue(sens)
        self.limit_slider.setValue(limit)
        self.processor.set_sensitivity(sens / 10.0)
        self.meter.set_threshold(float(limit))

    def showEvent(self, event):
        super().showEvent(event)
        self.processor.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.processor.stop()
