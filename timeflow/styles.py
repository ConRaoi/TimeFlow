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

SCALE_BASE_W = 400.0
SCALE_BASE_H = 400.0

COLOR_START = (46, 204, 113)
COLOR_END = (231, 76, 60)

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

def get_stylesheet():
    return f"""
        /* Hintergrund nur auf Hauptfenster anwenden */
        QWidget#TimeFlowMain {{
            background: #F6F7FB; 
            color: #111827;
            font-family: {FONT_FAMILY};
        }}
        
        QWidget {{
            font-family: {FONT_FAMILY};
            color: #111827;
        }}

        /* --- INTELLIGENTE KARTEN --- */
        QFrame#Card[compact="false"] {{
            background: #FFFFFF;
            border: 1px solid #E6E8F0;
            border-radius: 20px;
        }}

        QFrame#Card[compact="true"] {{
            background: transparent;
            border: none;
        }}

        QLabel#CardTitle {{
            font-size: 15px;
            font-weight: 700;
            color: #111827;
            padding-bottom: 8px;
            background: transparent;
        }}

        QLabel#TimeLabel {{
            font-weight: 700;
            letter-spacing: -2px;
            color: #111827;
            background: transparent;
        }}

        QLabel#TimeCaption, QLabel#NextSegment {{
            color: #8E8E93;
            font-weight: 500;
            background: transparent;
        }}

        QLabel#CurrentSegment {{
            color: #1C1C1E;
            font-weight: 600;
            background: transparent;
        }}

        /* --- Action Buttons (Icons) --- */
        QPushButton {{
            background: #007AFF;
            color: white;
            border: none;
            border-radius: 14px;
            font-weight: 700;
            font-size: 18px; 
            padding: 10px 0;
        }}
        QPushButton:hover {{
            background: #0062CC;
        }}
        QPushButton:pressed {{
            background: #0051A8;
        }}
        QPushButton:disabled {{
            background: #E5E5EA;
            color: #999;
        }}

        /* --- Header Icons (Pin/Focus) --- */
        QPushButton#FocusBtn, QPushButton#PinBtn {{
            background: transparent;
            color: #636366;
            font-size: 20px;      
            border-radius: 8px;
            padding: 4px;
        }}
        QPushButton#FocusBtn:hover, QPushButton#PinBtn:hover {{
            background: rgba(0,0,0,0.05);
            color: #000;
        }}
        QPushButton#FocusBtn:checked, QPushButton#PinBtn:checked {{
            background: #E1F0FF;
            color: #007AFF;
        }}

        /* --- Inputs (Modern & Stylisch) --- */
        QComboBox {{
            background: #FFFFFF;
            border: 1px solid #D1D1D6;
            border-radius: 12px;
            padding: 6px 12px;
            /* FIX: min-width verkleinert, damit AdjustToContents arbeiten kann */
            min-width: 60px; 
            color: #1C1C1E;
            font-weight: 600;
        }}
        
        QComboBox:hover {{
            border: 1px solid #007AFF;
            background: #EBF5FF; 
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
            gridline-color: #E5E5EA; 
            font-size: 14px;
            font-weight: 500;
            selection-background-color: #F2F2F7;
            selection-color: #000000;
        }}
        QHeaderView::section {{
            background: transparent;
            border: none;
            border-bottom: 2px solid #E5E5EA;
            padding: 6px 4px;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            color: #8E8E93;
        }}
        QTableView::item {{
            padding: 6px 4px;
            border: none;
            border-bottom: 1px solid #F2F2F7;
            background: transparent;
        }}
    """