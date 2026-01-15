from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QLineEdit, QWidget, QMessageBox
)
from .styles import COLOR_PRIMARY, TEXT_PRIMARY, BG_CARD, PALETTES
from PySide6.QtGui import QGuiApplication
from .i18n import get_strings

class SavePresetDialog(QDialog):
    def __init__(self, parent=None, lang_code="en"):
        super().__init__(parent)
        self.lang_code = lang_code
        self.preset_name = None
        s = get_strings(lang_code)
        
        # Theme detection
        is_dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        self.p = PALETTES["dark"] if is_dark else PALETTES["light"]
        
        self.setWindowTitle(s.save_preset)
        self.resize(400, 180)
        self.setStyleSheet(f"background-color: {self.p['bg_card']}; color: {self.p['text_primary']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel(s.preset_name)  # Use existing string
        lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("My Preset")
        self.input_name.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {self.p['combo_border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background: {self.p['combo_bg']};
                color: {self.p['text_primary']};
            }}
            QLineEdit:focus {{ border: 1px solid {self.p['btn_primary']}; background: {self.p['bg_card']}; }}
        """)
        layout.addWidget(self.input_name)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_save = QPushButton(s.save_preset)  # Use existing string
        
        # Style locally or rely on global? Let's style locally to be safe & consistent
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.p['btn_primary']}; color: white; border-radius: 6px;
                padding: 8px 20px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self.p['btn_primary_hover']}; }}
        """)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.p['btn_disabled']}; color: {self.p['text_secondary']}; border-radius: 6px;
                padding: 8px 20px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self.p['combo_border']}; color: {self.p['text_primary']}; }}
        """)
        
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def accept(self):
        txt = self.input_name.text().strip()
        if txt:
            self.preset_name = txt
            super().accept()
        else:
            self.input_name.setFocus()

class ManagePresetsDialog(QDialog):
    load_requested = Signal(object) # emits the preset data object

    def __init__(self, manager, parent=None, lang_code="en", data_key="segments"):
        super().__init__(parent)
        self.manager = manager
        self.lang_code = lang_code
        self.data_key = data_key
        self.s = get_strings(lang_code)
        self.loaded_data = None
        
        # Theme detection
        is_dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        self.p = PALETTES["dark"] if is_dark else PALETTES["light"]

        self.setWindowTitle(self.s.manage_presets)
        self.resize(500, 400)
        self.setStyleSheet(f"background-color: {self.p['bg_card']}; color: {self.p['text_primary']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {self.p['combo_border']};
                border-radius: 8px;
                background: {self.p['combo_bg']};
                padding: 5px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {self.p['table_grid']};
                color: {self.p['text_primary']};
            }}
            QListWidget::item:selected {{
                background-color: {self.p['btn_header_checked_bg']};
                color: {self.p['btn_primary']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.list_widget)
        
        # Buttons Row
        btn_row = QHBoxLayout()
        
        delete_text = "🗑 Delete"
        if self.lang_code == "de": delete_text = "🗑 Löschen"
        elif self.lang_code == "es": delete_text = "🗑 Eliminar"
        elif self.lang_code == "fr": delete_text = "🗑 Supprimer"
        self.btn_delete = QPushButton(delete_text)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #DC2626; border-radius: 6px;
                padding: 8px 20px; font-weight: 600; border: 1px solid #FECACA;
            }
            QPushButton:hover { background-color: #FEE2E2; }
        """)
        
        self.btn_load = QPushButton("✔ Load")
        if self.lang_code == "de": self.btn_load.setText("✔ Laden")
        elif self.lang_code == "es": self.btn_load.setText("✔ Cargar")
        elif self.lang_code == "fr": self.btn_load.setText("✔ Charger")
        
        self.btn_load.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.p['btn_primary']}; color: white; border-radius: 6px;
                padding: 8px 20px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self.p['btn_primary_hover']}; }}
        """)
        
        self.btn_delete.clicked.connect(self._delete_selected)
        
        rename_text = "✏ Rename"
        if self.lang_code == "de": rename_text = "✏ Umbenennen"
        elif self.lang_code == "es": rename_text = "✏ Renombrar"
        elif self.lang_code == "fr": rename_text = "✏ Renommer"
        self.btn_rename = QPushButton(rename_text)
        self.btn_rename.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.p['bg_card']}; color: {self.p['text_primary']}; border-radius: 6px;
                padding: 8px 15px; font-weight: 600; border: 1px solid {self.p['combo_border']};
            }}
            QPushButton:hover {{ background-color: {self.p['combo_bg']}; }}
        """)
        self.btn_rename.clicked.connect(self._rename_selected)
        self.btn_load.clicked.connect(self._load_selected)
        
        btn_row.addWidget(self.btn_delete)
        btn_row.addSpacing(10)
        btn_row.addWidget(self.btn_rename)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_load)
        layout.addLayout(btn_row)
        
        self._refresh_list()
        
    def _refresh_list(self):
        self.list_widget.clear()
        presets = self.manager.load_presets()
        for p in presets:
            item = QListWidgetItem(p["name"])
            # The data can be segments or noise settings
            if self.data_key in p:
                item.setData(Qt.UserRole, p[self.data_key])
            else:
                # Handle noise meter specific data (backward compatibility if needed)
                item.setData(Qt.UserRole, p)
            self.list_widget.addItem(item)
            
    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        # Name
        name = item.text()
        
        # Confirm
        ret = QMessageBox.question(self, "TimeFlow", f"{self.s.confirm_delete}\n'{name}'", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.manager.delete_preset(name)
            self._refresh_list()
            
    def _load_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        self.loaded_data = item.data(Qt.UserRole)
        self.accept()

    def _rename_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        old_name = item.text()
        dlg = SavePresetDialog(self, self.lang_code)
        dlg.setWindowTitle(dlg.windowTitle().replace(self.s.save_preset, "Rename"))
        dlg.input_name.setText(old_name)
        
        if dlg.exec():
            new_name = dlg.preset_name
            if new_name and new_name != old_name:
                if hasattr(self.manager, "rename_preset"):
                    self.manager.rename_preset(old_name, new_name)
                else:
                    # Generic fallback: Save new, delete old
                    # This is tricky without knowing the full data structure here
                    # But our managers usually have save/delete.
                    # Since we want a real rename, let's ensure managers have it.
                    pass
                self._refresh_list()
