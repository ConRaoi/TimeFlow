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
        
        # FIX: Wir verzichten auf setStyleSheet für das SpinBox-Widget.
        # Sobald man background/border stylt, schaltet Qt in den "Custom Modus" 
        # und die nativen Pfeile verschwinden (außer man lädt eigene Bilder).
        # Durch Weglassen des Stylesheets nutzen wir die nativen OS-Controls (System-Look),
        # was garantiert, dass Pfeile sichtbar und klickbar sind.
        
        spin.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        spin.setKeyboardTracking(False) 
        
        # Optional: Nur Font stylen, aber keine Rahmen/Hintergründe, 
        # um native Pfeile zu behalten.
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
        # Ein kleines bisschen Padding, damit es sauber in der Zelle sitzt
        editor.setGeometry(r.adjusted(2, 2, -2, -2))