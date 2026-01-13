from __future__ import annotations
from typing import List
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import QWidget, QSizePolicy

from .segments_model import Segment

def _clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return max(a, min(b, x))

def _lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))

def _progress_color(t: float) -> QColor:
    t = _clamp(t)
    g = (46, 204, 113)
    r = (231, 76, 60)
    return QColor(_lerp(g[0], r[0], t), _lerp(g[1], r[1], t), _lerp(g[2], r[2], t))

class PieWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._segments: List[Segment] = []
        self._progress: float = 0.0 
        self.setMinimumSize(40, 40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_segments(self, segments: List[Segment]) -> None:
        self._segments = list(segments)
        self.update()

    def set_progress(self, progress_0_1: float) -> None:
        self._progress = _clamp(progress_0_1)
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), QColor(0, 0, 0, 0))

        w = self.width()
        h = self.height()
        margin = 10 
        side = min(w, h) - (margin * 2)
        if side <= 0: return

        cx = w / 2
        cy = h / 2
        
        outer_rect = QRectF(cx - side/2, cy - side/2, side, side)
        inner_scale = 0.55 
        inner_side = side * inner_scale
        inner_rect = QRectF(cx - inner_side/2, cy - inner_side/2, inner_side, inner_side)

        total_s = sum(max(0.0, s.minutes) for s in self._segments)
        
        path_bg = QPainterPath()
        path_bg.addEllipse(outer_rect)
        path_inner = QPainterPath()
        path_inner.addEllipse(inner_rect)
        path_ring = path_bg.subtracted(path_inner)
        
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(242, 242, 247)) 
        p.drawPath(path_ring)

        if total_s > 0:
            start_angle = 90.0
            current_angle = start_angle
            for seg in self._segments:
                frac = (max(0.0, seg.minutes) / total_s)
                span = -360.0 * frac
                if abs(span) < 0.1: continue

                path_seg = QPainterPath()
                path_seg.arcMoveTo(outer_rect, current_angle)
                path_seg.arcTo(outer_rect, current_angle, span)
                path_seg.arcTo(inner_rect, current_angle + span, -span)
                path_seg.closeSubpath()
                
                p.setBrush(QColor(229, 229, 234)) 
                p.drawPath(path_seg)
                
                # Weiße Trennlinien
                p.setPen(QPen(Qt.white, 2))
                p.setBrush(Qt.NoBrush)
                p.drawPath(path_seg)
                p.setPen(Qt.NoPen)

                current_angle += span

            # Progress
            prog_span = -360.0 * self._progress
            if abs(prog_span) >= 0.1:
                prog_path = QPainterPath()
                prog_path.arcMoveTo(outer_rect, 90.0)
                prog_path.arcTo(outer_rect, 90.0, prog_span)
                prog_path.arcTo(inner_rect, 90.0 + prog_span, -prog_span)
                prog_path.closeSubpath()
                
                p.setBrush(_progress_color(self._progress))
                p.drawPath(prog_path)