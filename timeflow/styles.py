from PySide6.QtGui import QColor

# --- KONSTANTEN ---
COMPACT_WIDTH_LIMIT = 700
COMPACT_HEIGHT_LIMIT = 580

TINY_WIDTH_LIMIT = 320
TINY_HEIGHT_LIMIT = 320

MARGIN_STD = 24
SPACING_STD = 20
MARGIN_COMPACT = 12
SPACING_COMPACT = 8

COLOR_START = (46, 204, 113)
COLOR_END = (231, 76, 60)

# Legacy / Compatibility Constants (Static fallbacks)
COLOR_PRIMARY = "#007AFF"
TEXT_PRIMARY = "#111827"
BG_CARD = "#FFFFFF"

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

# --- THEME PALETTES ---
PALETTES = {
    "light": {
        "bg_main": "#F6F7FB",
        "bg_card": "#FFFFFF",
        "text_primary": "#111827",
        "text_secondary": "#6B7280",
        "text_tertiary": "#8E8E93",
        "border_std": "#E6E8F0",
        "btn_primary": "#007AFF",
        "btn_primary_hover": "#0062CC",
        "btn_primary_pressed": "#0051A8",
        "btn_disabled": "#E5E5EA",
        "btn_header": "#636366",
        "btn_header_hover_bg": "rgba(0,0,0,0.05)",
        "btn_header_checked_bg": "#E1F0FF",
        "combo_bg": "#FFFFFF",
        "combo_border": "#D1D1D6",
        "combo_hover_bg": "#EBF5FF",
        "table_grid": "#E5E5EA",
        "table_selection_bg": "#F2F2F7",
        "meter_bg": "#F2F2F7"
    },
    "dark": {
        "bg_main": "#1C1C1E",
        "bg_card": "#2C2C2E",
        "text_primary": "#F2F2F7",
        "text_secondary": "#AEAEB2",
        "text_tertiary": "#8E8E93",
        "border_std": "#3A3A3C",
        "btn_primary": "#0A84FF",
        "btn_primary_hover": "#409CFF",
        "btn_primary_pressed": "#0062CC",
        "btn_disabled": "#3A3A3C",
        "btn_header": "#AEAEB2",
        "btn_header_hover_bg": "rgba(255,255,255,0.1)",
        "btn_header_checked_bg": "#004080",
        "combo_bg": "#3A3A3C",
        "combo_border": "#48484A",
        "combo_hover_bg": "#48484A",
        "table_grid": "#3A3A3C",
        "table_selection_bg": "#3A3A3C",
        "meter_bg": "#3A3A3C"
    }
}

def get_stylesheet(arrow_path: str = "", is_dark: bool = False):
    p = PALETTES["dark"] if is_dark else PALETTES["light"]
    
    return f"""
        /* Hintergrund nur auf Hauptfenster anwenden */
        QWidget#TimeFlowMain {{
            background: {p['bg_main']}; 
            color: {p['text_primary']};
            font-family: {FONT_FAMILY};
        }}
        
        QWidget {{
            font-family: {FONT_FAMILY};
            color: {p['text_primary']};
        }}

        /* --- INTELLIGENTE KARTEN --- */
        QFrame#Card[compact="false"] {{
            background: {p['bg_card']};
            border: 1px solid {p['border_std']};
            border-radius: 20px;
        }}

        QFrame#Card[compact="true"] {{
            background: transparent;
            border: none;
        }}

        QLabel#CardTitle {{
            font-size: 15px;
            font-weight: 700;
            color: {p['text_primary']};
            padding-bottom: 8px;
            background: transparent;
        }}

        QLabel#TimeLabel {{
            font-weight: 700;
            letter-spacing: -2px;
            color: {p['text_primary']};
            background: transparent;
        }}

        QLabel#NextSegment {{
            color: {p['text_tertiary']};
            font-weight: 500;
            background: transparent;
            padding: 2px 0;
        }}

        QLabel#CurrentSegment {{
            color: {p['text_primary']};
            font-weight: 600;
            background: transparent;
            padding: 4px 0;
        }}

        /* --- Action Buttons (Icons) --- */
        QPushButton {{
            background: {p['btn_primary']};
            color: white;
            border: none;
            border-radius: 14px;
            font-weight: 700;
            font-size: 18px; 
            padding: 10px 0;
        }}
        QPushButton:hover {{
            background: {p['btn_primary_hover']};
        }}
        QPushButton:pressed {{
            background: {p['btn_primary_pressed']};
        }}
        QPushButton:disabled {{
            background: {p['btn_disabled']};
            color: #8E8E93;
        }}

        /* --- Header Icons (Pin/Focus) --- */
        QPushButton#FocusBtn, QPushButton#PinBtn, QPushButton#HeaderBtn {{
            background: transparent;
            color: {p['btn_header']};
            font-size: 20px;      
            border-radius: 8px;
            padding: 4px;
        }}
        QPushButton#FocusBtn:hover, QPushButton#PinBtn:hover, QPushButton#HeaderBtn:hover {{
            background: {p['btn_header_hover_bg']};
            color: {p['text_primary']};
        }}
        QPushButton#FocusBtn:checked, QPushButton#PinBtn:checked {{
            background: {p['btn_header_checked_bg']};
            color: {p['btn_primary']};
        }}

        /* --- Inputs --- */
        QComboBox {{
            background: {p['combo_bg']};
            border: 1px solid {p['combo_border']};
            border-radius: 12px;
            padding: 6px 12px;
            min-width: 60px; 
            color: {p['text_primary']};
            font-weight: 600;
        }}
        
        QComboBox:hover {{
            border: 1px solid {p['btn_primary']};
            background: {p['combo_hover_bg']}; 
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
        }}

        /* --- Table View --- */
        QTableView#SegmentsTable {{
            background: transparent;
            border: none;
            gridline-color: {p['table_grid']}; 
            font-size: 14px;
            font-weight: 500;
            selection-background-color: {p['table_selection_bg']};
            selection-color: {p['text_primary']};
        }}
        QHeaderView::section {{
            background: transparent;
            border: none;
            border-bottom: 2px solid {p['table_grid']};
            padding: 6px 4px;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            color: {p['text_tertiary']};
        }}
        QTableView::item {{
            padding: 6px 4px;
            border: none;
            border-bottom: 1px solid {p['table_grid']};
            background: transparent;
        }}
    """

def get_meter_bg_color(is_dark: bool = False):
    return QColor(PALETTES["dark"]["meter_bg"] if is_dark else PALETTES["light"]["meter_bg"])