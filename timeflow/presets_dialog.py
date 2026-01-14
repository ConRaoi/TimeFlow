from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QLineEdit, QWidget, QMessageBox
)
from .styles import COLOR_PRIMARY, TEXT_PRIMARY, BG_CARD
from .i18n import get_strings

class SavePresetDialog(QDialog):
    def __init__(self, parent=None, lang_code="en"):
        super().__init__(parent)
        self.lang_code = lang_code
        self.preset_name = None
        s = get_strings(lang_code)
        
        self.setWindowTitle(s.save_preset)  # Use existing string
        self.resize(400, 180)
        self.setStyleSheet(f"background-color: #FFFFFF; color: {TEXT_PRIMARY};")
        
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
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background: #F8FAFC;
                color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus {{ border: 1px solid {COLOR_PRIMARY}; background: #FFFFFF; }}
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
                background-color: {COLOR_PRIMARY}; color: white; border-radius: 6px;
                padding: 8px 20px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9; color: #64748B; border-radius: 6px;
                padding: 8px 20px; font-weight: 600;
            }
            QPushButton:hover { background-color: #E2E8F0; color: #1E293B; }
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
    load_requested = Signal(object) # emits segments list

    def __init__(self, manager, parent=None, lang_code="en"):
        super().__init__(parent)
        self.manager = manager
        self.lang_code = lang_code
        self.s = get_strings(lang_code)
        self.loaded_segments = None  # Store loaded segments
        
        self.setWindowTitle(self.s.manage_presets)  # Use existing string
        self.resize(500, 400)
        self.setStyleSheet(f"background-color: #FFFFFF; color: {TEXT_PRIMARY};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background: #F8FAFC;
                padding: 5px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #F1F5F9;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background-color: #EFF6FF;
                color: {COLOR_PRIMARY};
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
                background-color: {COLOR_PRIMARY}; color: white; border-radius: 6px;
                padding: 8px 20px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """)
        
        self.btn_delete.clicked.connect(self._delete_selected)
        self.btn_load.clicked.connect(self._load_selected)
        
        btn_row.addWidget(self.btn_delete)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_load)
        layout.addLayout(btn_row)
        
        self._refresh_list()
        
    def _refresh_list(self):
        self.list_widget.clear()
        presets = self.manager.load_presets()
        for p in presets:
            item = QListWidgetItem(p["name"])
            item.setData(Qt.UserRole, p["segments"])
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
        
        self.loaded_segments = item.data(Qt.UserRole)
        self.accept()
