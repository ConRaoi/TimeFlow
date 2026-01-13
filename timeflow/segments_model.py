from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QMimeData

@dataclass
class Segment:
    name: str
    minutes: float

class SegmentsModel(QAbstractTableModel):
    COL_NAME = 0
    COL_MIN = 1

    def __init__(
        self,
        segments: Optional[List[Segment]] = None,
        headers: Tuple[str, str] = ("Name", "Minutes"),
    ) -> None:
        super().__init__()
        self._segments: List[Segment] = segments or []
        self._headers = list(headers)

    def segments(self) -> List[Segment]:
        return list(self._segments)

    def set_segments(self, segments: List[Segment]) -> None:
        self.beginResetModel()
        self._segments = list(segments)
        self.endResetModel()

    def set_headers(self, name_header: str, minutes_header: str) -> None:
        self._headers = [name_header, minutes_header]
        self.headerDataChanged.emit(Qt.Horizontal, 0, 1)

    def total_seconds(self) -> float:
        return max(0.0, sum(max(0.0, s.minutes) for s in self._segments) * 60.0)

    # --- Qt Model API ---
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._segments)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else 2

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return self._headers[section]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        seg = self._segments[index.row()]

        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() == self.COL_NAME:
                return seg.name
            if index.column() == self.COL_MIN:
                return f"{seg.minutes:g}" if role == Qt.DisplayRole else seg.minutes

        if role == Qt.TextAlignmentRole and index.column() == self.COL_MIN:
            return int(Qt.AlignCenter) # Zentriert sieht bei Zahlen oft besser aus

        return None

    # --- DRAG & DROP & EDITING ---
    def flags(self, index: QModelIndex):
        if not index.isValid():
            # Erlaubt Drop zwischen Zeilen
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled 
        
        return (Qt.ItemIsEnabled | 
                Qt.ItemIsSelectable | 
                Qt.ItemIsEditable | 
                Qt.ItemIsDragEnabled)

    def supportedDropActions(self):
        return Qt.MoveAction

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid():
            return False
        seg = self._segments[index.row()]
        if index.column() == self.COL_NAME:
            seg.name = str(value).strip() or "Segment"
        elif index.column() == self.COL_MIN:
            try:
                v = float(value)
            except Exception:
                return False
            seg.minutes = max(0.0, v)
        else:
            return False
        
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return True

    # --- Drag & Drop Internals ---
    # Da wir nur interne Moves erlauben wollen, nutzen wir eine einfache Implementierung
    # Wir überschreiben moveRows nicht direkt, da QAbstractTableModel das komplex macht.
    # Stattdessen nutzen wir mimeData und dropMimeData nicht, sondern
    # setzen im View "InternalMove". Das erfordert aber, dass wir dropMimeData implementieren.

    def mimeData(self, indexes: List[QModelIndex]) -> QMimeData:
        mime = QMimeData()
        # Wir speichern nur den Row-Index als Payload
        if indexes:
            row = indexes[0].row()
            mime.setData("application/x-timeflow-row", str(row).encode())
        return mime

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if not data.hasFormat("application/x-timeflow-row"):
            return False
        
        if action == Qt.IgnoreAction:
            return True

        source_row = int(data.data("application/x-timeflow-row").data().decode())
        
        # Ziel-Index berechnen
        if row != -1:
            target_row = row
        elif parent.isValid():
            target_row = parent.row()
        else:
            target_row = len(self._segments)

        # Move logic
        if source_row == target_row:
            return False
        
        # Adjust target if moving downwards
        if source_row < target_row:
            target_row -= 1

        if self.beginMoveRows(QModelIndex(), source_row, source_row, QModelIndex(), target_row + (1 if target_row > source_row else 0)):
            item = self._segments.pop(source_row)
            self._segments.insert(target_row, item)
            self.endMoveRows()
            return True
            
        return False

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        row = max(0, min(row, len(self._segments)))
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        for _ in range(count):
            self._segments.insert(row, Segment("New segment", 5))
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        if row < 0 or row >= len(self._segments):
            return False
        end = min(len(self._segments) - 1, row + count - 1)
        self.beginRemoveRows(QModelIndex(), row, end)
        del self._segments[row : end + 1]
        self.endRemoveRows()
        return True