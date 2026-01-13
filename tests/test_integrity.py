import os
import sys
import pytest
from PySide6.QtWidgets import QApplication

# Pfad erweitern: Das Root-Verzeichnis (eins über 'tests') zum Python-Pfad hinzufügen
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

@pytest.fixture(scope="session")
def qapp():
    # Wir brauchen eine Instanz von QApplication für GUI Tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_imports():
    """Prüft, ob alle Module sauber importiert werden können."""
    try:
        # app.py liegt im Root, daher direkt importieren
        import app
        # Die anderen Module liegen im Package timeflow
        from timeflow import main_window
        from timeflow import views
        from timeflow import styles
        from timeflow import delegates
    except ImportError as e:
        pytest.fail(f"Import fehlgeschlagen: {e}")
    except SyntaxError as e:
        pytest.fail(f"Syntaxfehler im Code: {e}")

def test_styles_constants():
    """Prüft, ob kritische Konstanten in styles.py existieren."""
    from timeflow import styles
    required_constants = [
        "TINY_WIDTH_LIMIT", "COMPACT_WIDTH_LIMIT", 
        "MARGIN_STD", "FONT_FAMILY"
    ]
    for const in required_constants:
        assert hasattr(styles, const), f"Fehlende Konstante in styles.py: {const}"

def test_assets_exist():
    """Prüft, ob Icon und Sound da sind."""
    assets_dir = os.path.join(ROOT_DIR, "timeflow_assets")
    
    # Debugging-Hilfe falls Ordner fehlt
    if not os.path.exists(assets_dir):
        found_files = os.listdir(ROOT_DIR)
        pytest.fail(f"Assets Ordner 'timeflow_assets' nicht gefunden in {ROOT_DIR}.\nGefunden wurde: {found_files}")

    assert os.path.exists(os.path.join(assets_dir, "TimeFlowIcon.png")), "TimeFlowIcon.png fehlt in timeflow_assets!"
    
    # Sound ist optional, aber wir prüfen es mal
    if not os.path.exists(os.path.join(assets_dir, "alert.wav")):
        print("\nHINWEIS: alert.wav fehlt (System-Beep wird genutzt)")

def test_app_launch(qapp):
    """Smoke Test: Lässt sich das Hauptfenster instanziieren?"""
    # Wir importieren hier lokal, um sicherzugehen, dass vorherige Tests liefen
    from timeflow.main_window import MainWindow
    try:
        w = MainWindow()
        assert w is not None
        # Wir prüfen kurz die Startgröße
        assert w.width() >= 200
        w.close()
    except Exception as e:
        pytest.fail(f"App Start gecrasht: {e}")