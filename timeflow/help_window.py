from __future__ import annotations
import os
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices, QFont, QTextCursor, QFontDatabase, QTextDocument
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout, QWidget

from .utils import resource_path

class HelpWindow(QDialog):
    """
    Zeigt die README.md an und nutzt 'Block-Walking' statt HTML-Ankern für die Navigation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TimeFlow – Hilfe / Readme")
        self.resize(850, 750)
        self.setStyleSheet("background-color: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Header ---
        header = QWidget()
        header.setStyleSheet("background-color: #F6F7FB; border-bottom: 1px solid #E6E8F0;")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        
        title_lbl = QPushButton("📑 Dokumentation")
        title_lbl.setStyleSheet("border: none; font-weight: bold; font-size: 14px; color: #111827; text-align: left;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("""
            QPushButton { border: none; font-weight: bold; font-size: 16px; color: #6B7280; border-radius: 4px; }
            QPushButton:hover { background-color: #E5E7EB; color: #111827; }
        """)

        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        layout.addWidget(header)

        # --- Browser ---
        self.browser = QTextBrowser()
        # Wir lassen Qt das Markdown rendern (sieht am besten aus)
        self.browser.setOpenExternalLinks(False)
        self.browser.setOpenLinks(False) 
        self.browser.anchorClicked.connect(self._on_anchor_clicked)
        
        # Style
        self.browser.setStyleSheet("border: none; padding: 20px; color: #374151;")
        
        # Font-Wahl
        available = set(QFontDatabase.families())
        font_name = "Arial"
        for cand in ["Segoe UI", "Helvetica Neue", "Arial"]:
            if cand in available:
                font_name = cand
                break
        self.browser.setFont(QFont(font_name, 13))

        layout.addWidget(self.browser)
        self._load_readme()

    def _load_readme(self) -> None:
        """Lädt die Datei und setzt sie als natives Markdown."""
        paths = [
            os.path.join(os.getcwd(), "README.md"),
            resource_path("README.md")
        ]
        
        content = ""
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        content = f.read()
                    break
                except: pass
        
        if not content:
            content = "# Fehler\nREADME.md konnte nicht geladen werden."

        # NATIVES RENDERING - Kein HTML-Gebastel
        self.browser.setMarkdown(content)

    def _on_anchor_clicked(self, url: QUrl) -> None:
        """
        Der Kern der Lösung: Wir fangen den Klick ab.
        """
        link = url.toString()
        
        # 1. Externe Links (Web/Mail) -> System
        if link.startswith("http") or link.startswith("mailto"):
            QDesktopServices.openUrl(url)
            return

        # 2. Interne Links (Inhaltsverzeichnis)
        # Wir extrahieren das Ziel, z.B. "#-deutsch" -> "deutsch"
        fragment = url.fragment()
        if not fragment and "#" in link:
            fragment = link.split("#")[-1]
        
        if fragment:
            self._jump_to_header_by_content(fragment)

    def _jump_to_header_by_content(self, anchor_text: str) -> None:
        """
        Die "Outside-the-Box" Lösung:
        Wir ignorieren HTML-Anker. Wir laufen durch die Dokument-Struktur (Blöcke)
        und suchen nach einer Überschrift, deren Text zum Link passt.
        """
        
        # Suchbegriff reinigen: "-deutsch" -> "deutsch"
        target_clean = self._clean_text(anchor_text)
        
        doc = self.browser.document()
        block = doc.begin()
        
        while block.isValid():
            # Wir prüfen: Ist dieser Block eine Überschrift?
            # Qt markiert Header intern mit headingLevel > 0
            fmt = block.blockFormat()
            
            if fmt.headingLevel() > 0:
                # Text der Überschrift holen, z.B. "🇩🇪 Deutsch"
                header_text = block.text()
                header_clean = self._clean_text(header_text)
                
                # Vergleich: Ist unser Suchziel in der Überschrift enthalten?
                # "deutsch" ist in "de deutsch" enthalten -> Treffer!
                if target_clean and (target_clean == header_clean or target_clean in header_clean):
                    self._scroll_to_block(block)
                    return

            block = block.next()

    def _scroll_to_block(self, block):
        """
        Scrollt das Fenster exakt so, dass der gefundene Block oben steht.
        """
        # 1. Cursor setzen (setzt den Fokus intern an die Stelle)
        cursor = QTextCursor(block)
        self.browser.setTextCursor(cursor)
        
        # 2. Scrollbar manuell justieren (für visuelle Position)
        scrollbar = self.browser.verticalScrollBar()
        if scrollbar:
            # Wir fragen das Layout: Wo genau (Pixel Y) liegt dieser Block?
            layout = self.browser.document().documentLayout()
            rect = layout.blockBoundingRect(block)
            
            # Scrollen, mit 10px Abstand nach oben für die Optik
            scrollbar.setValue(int(rect.y()) - 10)

    def _clean_text(self, text: str) -> str:
        """
        Macht den Text vergleichbar: Alles klein, nur Buchstaben/Zahlen.
        Filtert Emojis, Bindestriche, Punkte etc. raus.
        """
        text = text.lower()
        # Behalte nur alphanumerische Zeichen
        return "".join(c for c in text if c.isalnum())