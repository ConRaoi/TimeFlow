from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QStyledItemDelegate, QDoubleSpinBox, QAbstractSpinBox

class MinutesDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        spin = QDoubleSpinBox(parent)
        spin.setDecimals(1)
        spin.setRange(0.1, 999.0)
        spin.setSingleStep(0.5)
        spin.setAlignment(Qt.AlignCenter)
        
        # Native Look behalten (kein setStyleSheet), damit OS-Pfeile sichtbar sind.
        spin.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        spin.setKeyboardTracking(False) 
        
        # Nur Font anpassen für Lesbarkeit, Rest bleibt Systemstandard
        font = spin.font()
        font.setBold(True)
        spin.setFont(font)

        QTimer.singleShot(0, spin.selectAll)
        return spin

    def setEditorData(self, editor, index):
        try:
            value = float(index.model().data(index, Qt.EditRole))
        except Exception:
            value = 0.0
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model.setData(index, float(editor.value()), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        r = option.rect
        editor.setGeometry(r.adjusted(2, 2, -2, -2))