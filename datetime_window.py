from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QFontMetrics

class DateTimeWindow(QWidget):
    def __init__(self, theme, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = theme
        self._setup_ui()
        self.refresh_theme()

    def _setup_ui(self):
        """Set up the user interface components with flexible sizing."""
        self.time_label = QLabel("00:00:00", self)
        self.date_label = QLabel("Date", self)
        self.weekday_label = QLabel("Weekday", self)

        for lbl in [self.time_label, self.date_label, self.weekday_label]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Ignored erlaubt dem Widget, kleiner/größer zu sein als der Text-Hint
            lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.time_label, stretch=4)
        self.layout.addWidget(self.date_label, stretch=1)
        self.layout.addWidget(self.weekday_label, stretch=1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def refresh_theme(self):
        """Refresh colors: Time is darker as requested."""
        base_color = QColor(self.theme.get('text_color', '#FFFFFF'))
        time_color = base_color.darker(130).name() # Deutlich dunkler
        common_color = base_color.name()
        
        self.time_label.setStyleSheet(f"color: {time_color}; background: transparent;")
        self.date_label.setStyleSheet(f"color: {common_color}; background: transparent;")
        self.weekday_label.setStyleSheet(f"color: {common_color}; background: transparent;")

    def sizeHint(self) -> QSize:
        return QSize(400, 250)

    def _apply_scaling(self):
        """Iteratively scale fonts to fit the current window size perfectly."""
        w, h = self.width(), self.height()
        print(f"DEBUG: _apply_scaling called: w={w}, h={h}", file=sys.stderr)
        if w <= 10 or h <= 10: 
            print(f"DEBUG: Early return: w or h too small", file=sys.stderr)
            return

        # Nutze 90% der Fensterhöhe für Text, Rest für Abstände
        target_total_h = h * 0.85
        
        # Start-Schriftgröße für die Zeit (ca. 45% der Fensterhöhe)
        time_fs = max(8, int(h * 0.45))
        print(f"DEBUG: Starting with time_fs={time_fs}", file=sys.stderr)
        
        best_time_fs = time_fs
        best_sub_fs = max(5, int(time_fs * 0.35))
        
        # Iterative search for best fit (shrink if needed)
        while time_fs > 6:
            # Zeit-Font
            f_time = QFont(self.font())
            f_time.setPixelSize(time_fs)
            f_time.setBold(True)
            fm_t = QFontMetrics(f_time)
            
            # Datum/Wochentag ca. 35% der Zeitgröße
            sub_fs = max(5, int(time_fs * 0.35))
            f_sub = QFont(self.font())
            f_sub.setPixelSize(sub_fs)
            fm_s = QFontMetrics(f_sub)
            
            # Messen
            tw = fm_t.horizontalAdvance(self.time_label.text())
            dw = fm_s.horizontalAdvance(self.date_label.text())
            ww = fm_s.horizontalAdvance(self.weekday_label.text())
            
            total_h = fm_t.height() + (fm_s.height() * 2)
            max_w = max(tw, dw, ww)
            
            # Prüfen ob es ins Fenster passt (Breite und Höhe)
            if total_h <= target_total_h and max_w <= w * 0.9:
                best_time_fs = time_fs
                best_sub_fs = sub_fs
                print(f"DEBUG: Found fit: time_fs={best_time_fs}, sub_fs={best_sub_fs}", file=sys.stderr)
                break
            
            time_fs -= 1
        
        print(f"DEBUG: Setting fonts: time_fs={best_time_fs}, sub_fs={best_sub_fs}", file=sys.stderr)
        
        # Fallback: sicherstelle, dass wir immer Fonts setzen (nicht leer)
        f_t = QFont(self.font())
        f_t.setPixelSize(best_time_fs)
        f_t.setBold(True)
        
        f_s = QFont(self.font())
        f_s.setPixelSize(best_sub_fs)
        
        self.time_label.setFont(f_t)
        self.date_label.setFont(f_s)
        self.weekday_label.setFont(f_s)
        
        print(f"DEBUG: Fonts set. time_label font size: {self.time_label.font().pixelSize()}", file=sys.stderr)

        # Dynamische Abstände basierend auf Font-Metriken (nicht nur Fensterhöhe)
        fm_best = QFontMetrics(f_t)
        fm_sub = QFontMetrics(f_s)
        
        # Margins: ca. 30% der Zeitfont-Höhe (kleiner bei kleinen Fenstern)
        margin = max(4, int(fm_best.height() * 0.35))
        # Spacing: ca. 20% der Subfont-Höhe
        spacing = max(2, int(fm_sub.height() * 0.2))
        
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(spacing)

    def resizeEvent(self, event):
        print(f"DEBUG: resizeEvent triggered: {event.oldSize()} -> {event.size()}", file=sys.stderr)
        super().resizeEvent(event)
        self._apply_scaling()

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_scaling()

    def update_time(self, current_time):
        self.time_label.setText(current_time.toString("hh:mm:ss"))
        # Bei Inhaltsänderung Skalierung prüfen (optional, da resize primär ist)
        self._apply_scaling()

    def update_date(self, current_date):
        self.date_label.setText(current_date.toString("dd. MMMM yyyy"))
        self.weekday_label.setText(current_date.toString("dddd").upper())
        self._apply_scaling()