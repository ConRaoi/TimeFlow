from PySide6.QtCore import Qt, QTimer, QDateTime, QLocale, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy
from PySide6.QtGui import QFont, QGuiApplication, QFontMetrics
import logging

from .i18n import get_strings
from .styles import PALETTES

logger = logging.getLogger(__name__) 

class DateTimeWindow(QFrame):
    """
    Ein modernes, stylisches Fenster zur Anzeige von Datum, Wochentag und Uhrzeit.
    Hierarchie: Uhrzeit -> Doppellinie -> Datum -> Wochentag

    Hinweis: Dieses Widget skaliert Schriftgrößen dynamisch bei Größenänderungen
    und passt beim ersten Anzeigen die Fenstergröße an, so dass alle Inhalte sauber
    und ohne Abschneiden dargestellt werden.
    """
    def __init__(self, parent=None, lang_code="de"):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        self.lang_code = lang_code
        s = get_strings(lang_code)
        self.setWindowTitle(s.date_time)
        self._setup_ui()
        
        # Timer für die Aktualisierung (jede Minute reicht ohne Sekunden, 
        # aber wir bleiben bei 1s für sofortiges Feedback nach Start)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_display)
        self.timer.start(1000)
        
        self._update_display()
        self.refresh_theme(QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark)

        # Internal initialization helpers for responsive sizing
        self._initialized = False
        self._default_time_fs = 110
        self._default_date_fs = 32
        self._default_weekday_fs = 24

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(0)

        # 1. Uhrzeit (Der Star der Show) - Oben
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        # Prefer the size hint vertically so the layout gives it enough height
        self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Font-size is set dynamically in _apply_scaling; keep weight and visual tweaks via stylesheet
        self.time_label.setStyleSheet("font-weight: 900; letter-spacing: -2px;")
        layout.addWidget(self.time_label, 3)

        # 2. Doppellinie (Subtil & Sauber)
        self.line_container = QWidget()
        self.line_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        line_layout = QVBoxLayout(self.line_container)
        line_layout.setContentsMargins(30, 5, 30, 10)
        line_layout.setSpacing(3)

        self.line1 = QFrame()
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Plain)
        self.line1.setFixedHeight(1)

        self.line2 = QFrame()
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Plain)
        self.line2.setFixedHeight(1)

        line_layout.addWidget(self.line1)
        line_layout.addWidget(self.line2)
        layout.addWidget(self.line_container, 0)

        # 3. Datum (Mitte)
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.date_label.setStyleSheet("font-weight: 500; letter-spacing: 0px;")
        layout.addWidget(self.date_label, 1)

        # 4. Wochentag (Unten)
        self.weekday_label = QLabel()
        self.weekday_label.setAlignment(Qt.AlignCenter)
        self.weekday_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.weekday_label.setStyleSheet("font-weight: 300; text-transform: uppercase;")
        layout.addWidget(self.weekday_label, 1)

        # No top/bottom stretch so widgets receive the vertical space defined by stretches above

    def _get_locale(self) -> QLocale:
        """Mapping von App-Sprachcodes auf spezifische Regionen."""
        if self.lang_code == "en":
            return QLocale(QLocale.English, QLocale.UnitedKingdom)
        elif self.lang_code == "de":
            return QLocale(QLocale.German, QLocale.Germany)
        elif self.lang_code == "es":
            return QLocale(QLocale.Spanish, QLocale.Spain)
        elif self.lang_code == "fr":
            return QLocale(QLocale.French, QLocale.France)
        return QLocale(self.lang_code)

    def _update_display(self):
        now = QDateTime.currentDateTime()
        locale = self._get_locale()

        # Debug-Ausgabe für aktuelle Zeit und Datum
        logger.debug(f"Aktuelle Zeit: {now.toString()}")

        # Uhrzeit: HH:mm (Ohne Sekunden)
        time_str = locale.toString(now.time(), "HH:mm")
        logger.debug(f"Uhrzeit-String: {time_str}")

        # Datum: 14. Januar 2026 / 14 January 2026
        date_str = locale.toString(now.date(), "d. MMMM yyyy") if self.lang_code == "de" else locale.toString(now.date(), "d MMMM yyyy")
        logger.debug(f"Datum-String: {date_str}")

        # Wochentag: Mittwoch / Wednesday
        weekday_str = locale.toString(now.date(), "dddd")
        logger.debug(f"Wochentag-String: {weekday_str}")

        self.time_label.setText(time_str)
        self.date_label.setText(date_str)
        self.weekday_label.setText(weekday_str)

        # Sofort Skalierung prüfen, falls sich die Textlänge ändert
        self._apply_scaling()

    def refresh_theme(self, is_dark: bool):
        p = PALETTES["dark"] if is_dark else PALETTES["light"]
        
        # Keep styling (colors, weight) but avoid fixed letter/margin in CSS — we set those dynamically
        self.time_label.setStyleSheet(f"font-weight: 900; color: {p['btn_primary']};")
        self.date_label.setStyleSheet(f"font-weight: 500; color: {p['text_primary']};")
        self.weekday_label.setStyleSheet(f"font-weight: 400; color: {p['text_secondary']}; text-transform: uppercase;")
        
        line_style = f"background-color: {p['border_std']}; border: none;"
        self.line1.setStyleSheet(line_style)
        self.line2.setStyleSheet(line_style)
        
        # Re-apply scaling because colors/weights may slightly affect metrics
        try:
            self._apply_scaling()
        except Exception:
            pass
        self.update()

    def sizeHint(self) -> QSize:
        """Return a sensible default size based on default font sizes and current texts."""
        # Measure using the default pixel sizes
        f_t = QFont(self.time_label.font())
        f_t.setPixelSize(self._default_time_fs)
        f_t.setBold(True)
        fm_t = QFontMetrics(f_t)

        f_s = QFont(self.date_label.font())
        f_s.setPixelSize(self._default_date_fs)
        fm_s = QFontMetrics(f_s)

        width = max(
            fm_t.horizontalAdvance(self.time_label.text()),
            fm_s.horizontalAdvance(self.date_label.text()),
            fm_s.horizontalAdvance(self.weekday_label.text()),
        )
        # Add generous margins for UI chrome and spacing
        margin_w = 80
        margin_h = 200
        height = fm_t.height() + fm_s.height() * 2 + margin_h
        return QSize(max(320, width + margin_w), height)

    def _apply_scaling(self):
        """Iteratively scale fonts to fit the current window size perfectly."""
        w, h = self.width(), self.height()
        if w <= 10 or h <= 10:
            return

        # Use 85% of the window height for text, leaving the rest for spacing
        target_total_h = h * 0.85

        # Initial font size for the time label (approximately 40% of the window height)
        time_fs = max(1, int(h * 0.4))

        def get_best_fit():
            nonlocal time_fs
            while time_fs > 5:
                # Time font
                f_time = QFont(self.font())
                f_time.setPixelSize(time_fs)
                f_time.setBold(True)
                fm_t = QFontMetrics(f_time)

                # Date/weekday font size is approximately 30% of the time font size
                sub_fs = max(5, int(time_fs * 0.3))
                f_sub = QFont(self.font())
                f_sub.setPixelSize(sub_fs)
                fm_s = QFontMetrics(f_sub)

                # Measure dimensions
                tw = fm_t.horizontalAdvance(self.time_label.text())
                dw = fm_s.horizontalAdvance(self.date_label.text())
                ww = fm_s.horizontalAdvance(self.weekday_label.text())

                total_h = fm_t.height() + (fm_s.height() * 2)
                max_w = max(tw, dw, ww)

                # Check if it fits within the window (width and height)
                if total_h <= target_total_h and max_w <= w * 0.9:
                    return f_time, f_sub

                time_fs -= 1

            return QFont(), QFont()

        f_t, f_s = get_best_fit()
        # Debug: report chosen font sizes
        try:
            chosen_time_fs = f_t.pixelSize()
            chosen_sub_fs = f_s.pixelSize()
        except Exception:
            chosen_time_fs = None
            chosen_sub_fs = None
        logger.debug(f"Gewählte Schriftgrößen - Zeit: {chosen_time_fs}, Datum/Wochentag: {chosen_sub_fs}")

        # Fallback: ensure we have reasonable fonts so labels remain visible
        if not chosen_time_fs or chosen_time_fs < 6:
            fallback_time_fs = min(120, max(24, int(h * 0.2)))
            f_t = QFont(self.time_label.font())
            f_t.setPixelSize(fallback_time_fs)
            f_t.setBold(True)
            logger.debug(f"Fallback Zeit-Schriftgröße verwendet: {fallback_time_fs}")

        if not chosen_sub_fs or chosen_sub_fs < 6:
            fallback_sub = max(10, int((f_t.pixelSize() if f_t.pixelSize() else 24) * 0.35))
            f_s = QFont(self.date_label.font())
            f_s.setPixelSize(fallback_sub)
            logger.debug(f"Fallback Datum/Wochentag-Schriftgröße verwendet: {fallback_sub}")

        self.time_label.setFont(f_t)
        self.date_label.setFont(f_s)
        self.weekday_label.setFont(f_s)

        # Ensure there is a visible color for the labels (avoid white-on-white)
        if 'color:' not in self.time_label.styleSheet().lower():
            self.time_label.setStyleSheet(self.time_label.styleSheet() + "color: #111827;")
        if 'color:' not in self.date_label.styleSheet().lower():
            self.date_label.setStyleSheet(self.date_label.styleSheet() + "color: #111827;")
        if 'color:' not in self.weekday_label.styleSheet().lower():
            self.weekday_label.setStyleSheet(self.weekday_label.styleSheet() + "color: #6B7280;")

        # Ensure labels have enough minimum height for chosen fonts (avoid zero-height)
        fm_t = QFontMetrics(self.time_label.font())
        fm_s = QFontMetrics(self.date_label.font())
        # Add padding to avoid clipping of descenders
        self.time_label.setMinimumHeight(fm_t.height() + 12)
        self.date_label.setMinimumHeight(fm_s.height() + 6)
        self.weekday_label.setMinimumHeight(fm_s.height() + 6)

        # Dynamic margins and spacing (use the widget's layout() safely)
        margin = int(h * 0.05)
        root_layout = self.layout()
        if root_layout:
            root_layout.setContentsMargins(margin, margin, margin, margin)
            root_layout.setSpacing(int(h * 0.02))

        # Force immediate update/repaint
        self.time_label.update()
        self.date_label.update()
        self.weekday_label.update()
        self.update()

        # Debug: report geometries and palette info
        tl_geo = self.time_label.geometry()
        dl_geo = self.date_label.geometry()
        wl_geo = self.weekday_label.geometry()
        logger.debug(f"Geometrien - Zeit: {tl_geo}, Datum: {dl_geo}, Wochentag: {wl_geo}")
        try:
            tl_color = self.time_label.palette().color(self.time_label.foregroundRole()).name()
        except Exception:
            tl_color = None
        logger.debug(f"Zeit-Label-Farbe: {tl_color}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scaling()

        # Ermögliche das Verkleinern unter die zuvor erzwungene `sizeHint()`-Größe,
        # aber lege eine kleine, sinnvolle Untergrenze fest, damit Widgets nicht
        # völlig unbrauchbar werden. Diese Limits sind bewusst klein (z.B. für
        # Docking/kleine Vorschau-Fenster), und sollten das bestehende Verhalten
        # in normalen Größen nicht beeinflussen.
        try:
            self.setMinimumSize(120, 100)
        except Exception:
            # Sicherheitsnetz, falls das Backend keine Größenänderung erlaubt
            pass

    def showEvent(self, event):
        super().showEvent(event)
        # On first show, ensure a reasonable initial size that fits all content
        if not self._initialized:
            try:
                hinted = self.sizeHint()
                # Only enlarge to hint if current size is smaller
                if self.width() < hinted.width() or self.height() < hinted.height():
                    self.resize(hinted)
            except Exception:
                pass
            finally:
                self._initialized = True
        self._apply_scaling()

    def retranslate(self, lang_code: str):
        self.lang_code = lang_code
        s = get_strings(lang_code)
        self.setWindowTitle(s.date_time)
        self._update_display()
