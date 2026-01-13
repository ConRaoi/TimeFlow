import sys
import os

def format_mmss(seconds: float) -> str:
    s = int(round(max(0.0, seconds)))
    m = s // 60
    s = s % 60
    return f"{m:02d}:{s:02d}"

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)