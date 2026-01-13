from __future__ import annotations
import time
from dataclasses import dataclass
from PySide6.QtCore import QObject, QTimer, Signal


@dataclass
class TimerState:
    running: bool
    elapsed_s: float
    total_s: float


class TimerEngine(QObject):
    tick = Signal(object)      # emits TimerState
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._timer = QTimer(self)
        self._timer.setInterval(100)  # ms
        self._timer.timeout.connect(self._on_timeout)

        self._running = False
        self._t0 = 0.0
        self._elapsed_before = 0.0
        self._total_s = 0.0

    def set_total_seconds(self, total_s: float) -> None:
        self._total_s = max(0.0, float(total_s))
        self._emit()

    def reset(self) -> None:
        self.pause()
        self._elapsed_before = 0.0
        self._emit()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._t0 = time.monotonic()
        self._timer.start()
        self._emit()

    def pause(self) -> None:
        if not self._running:
            return
        self._running = False
        self._timer.stop()
        self._elapsed_before = self.elapsed_seconds()
        self._emit()

    def toggle(self) -> None:
        if self._running:
            self.pause()
        else:
            self.start()

    def elapsed_seconds(self) -> float:
        if not self._running:
            return float(self._elapsed_before)
        return float(self._elapsed_before + (time.monotonic() - self._t0))

    def _on_timeout(self) -> None:
        if self._total_s > 0 and self.elapsed_seconds() >= self._total_s:
            # clamp, stop, emit finished
            self._elapsed_before = self._total_s
            self._running = False
            self._timer.stop()
            self._emit()
            self.finished.emit()
            return
        self._emit()

    def _emit(self) -> None:
        self.tick.emit(TimerState(self._running, self.elapsed_seconds(), self._total_s))
