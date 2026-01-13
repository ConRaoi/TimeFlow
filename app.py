import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from timeflow.utils import resource_path
from timeflow.styles import get_stylesheet

def main() -> int:
    app = QApplication(sys.argv)
    
    # Style laden
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())
    
    # Icon Setup
    icon_path = resource_path(os.path.join("timeflow_assets", "TimeFlowIcon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from timeflow.main_window import MainWindow
    w = MainWindow()
    w.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())