from PySide6.QtCore import Qt, Signal, QRect, QPoint, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSlider, QFrame, QSizePolicy
)
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen

from .audio_processor import AudioProcessor
from .i18n import get_strings

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
        
        # Hintergrund mit subtilem Glass-Effekt
        bg_rect = QRect(padding, padding, w - 2*padding, h - 2*padding)
        painter.setBrush(QColor("#F2F2F7"))
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
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Noise Meter")
        
        self.lang_code = lang_code
        self.processor = AudioProcessor(self)
        self.processor.levelUpdated.connect(self._on_level_updated)
        
        self._setup_ui()
        self.retranslate(lang_code)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30) # Mehr Padding
        root.setSpacing(24) # Mehr Spacing

        # Header
        header = QHBoxLayout()
        self.title_label = QLabel("🎤 Noise Meter")
        self.title_label.setObjectName("CardTitle")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 800; padding-bottom: 0;")
        header.addWidget(self.title_label)
        header.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32) # Größerer Button
        self.close_btn.setStyleSheet("""
            QPushButton {
                border-radius: 16px; 
                font-weight: bold; 
                background: #F2F2F7; 
                color: #8E8E93;
                font-size: 14px;
                padding: 0;
            }
            QPushButton:hover {
                background: #E5E5EA;
                color: #1C1C1E;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        header.addWidget(self.close_btn)
        root.addLayout(header)

        # Meter
        self.meter = LevelMeterWidget()
        root.addWidget(self.meter)

        # Settings
        settings = QVBoxLayout()
        settings.setSpacing(12)
        
        # Sensitivity
        sens_row = QHBoxLayout()
        self.sens_label = QLabel("Sensitivity")
        self.sens_label.setStyleSheet("font-size: 16px; font-weight: 600; min-width: 120px;")
        self.sens_slider = QSlider(Qt.Horizontal)
        self.sens_slider.setRange(1, 100) # 0.1x to 10.0x
        self.sens_slider.setValue(40) # Startet bei 4.0x (solider Mittelwert)
        self.sens_slider.setMinimumHeight(40)
        self.sens_slider.valueChanged.connect(self._on_sens_changed)
        sens_row.addWidget(self.sens_label)
        sens_row.addWidget(self.sens_slider)
        settings.addLayout(sens_row)

        # Threshold (Limit)
        limit_row = QHBoxLayout()
        self.limit_label = QLabel("Limit")
        self.limit_label.setStyleSheet("font-size: 16px; font-weight: 600; min-width: 120px;")
        self.limit_slider = QSlider(Qt.Horizontal)
        self.limit_slider.setRange(10, 95)
        self.limit_slider.setValue(70)
        self.limit_slider.setMinimumHeight(40)
        self.limit_slider.valueChanged.connect(self._on_limit_changed)
        limit_row.addWidget(self.limit_label)
        limit_row.addWidget(self.limit_slider)
        settings.addLayout(limit_row)

        root.addLayout(settings)

    def retranslate(self, lang_code: str):
        self.lang_code = lang_code
        s = get_strings(lang_code)
        self.title_label.setText(f"🎤 {s.noise_meter}")
        self.sens_label.setText(s.sensitivity)
        self.limit_label.setText(s.limit)
        self.setWindowTitle(s.noise_meter)

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

    def _on_limit_changed(self, value):
        self.meter.set_threshold(float(value))

    def showEvent(self, event):
        super().showEvent(event)
        self.processor.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.processor.stop()
