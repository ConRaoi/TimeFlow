"""
Pytest configuration and fixtures for TimeFlow tests.
Enables headless Qt testing without a display.
"""

import pytest
import os
import sys
import warnings

# Suppress urllib3 OpenSSL warning
try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.simplefilter('ignore', NotOpenSSLWarning)
except ImportError:
    pass
warnings.filterwarnings("ignore", message=".*OpenSSL.*")
warnings.filterwarnings("ignore", message=".*urllib3.*")


# Set Qt to use offscreen rendering (headless mode)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
# Disable background threads for stability in tests
os.environ["TIMEFLOW_SKIP_UPDATER"] = "1"

# Optional pytest-qt support
try:
    import pytest_qt
    HAS_PYTEST_QT = True
except ImportError:
    HAS_PYTEST_QT = False
    print("Note: pytest-qt not installed. Install with: pip install pytest-qt")


@pytest.fixture(scope="session")
def qapp():
    """
    Create a QApplication instance for the entire test session.
    This is required for any Qt widget testing.
    """
    from PySide6.QtWidgets import QApplication
    
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    yield app
    
    # Don't quit - let pytest handle cleanup


@pytest.fixture
def qtbot(qapp):
    """
    Provide a qtbot-like fixture for basic Qt testing without pytest-qt.
    If pytest-qt is available, it will be used instead.
    """
    if HAS_PYTEST_QT:
        from pytestqt.qtbot import QtBot
        return QtBot(qapp)
    else:
        # Minimal implementation for basic testing
        class MinimalQtBot:
            def __init__(self, app):
                self._app = app
                self._widgets = []
            
            def addWidget(self, widget):
                """Register a widget for cleanup."""
                self._widgets.append(widget)
            
            def wait(self, ms):
                """Wait for specified milliseconds."""
                from PySide6.QtCore import QEventLoop, QTimer
                loop = QEventLoop()
                QTimer.singleShot(ms, loop.quit)
                loop.exec()
            
            def waitSignal(self, signal, timeout=5000):
                """Wait for a signal with timeout."""
                from PySide6.QtCore import QEventLoop, QTimer
                loop = QEventLoop()
                received = [False]
                
                def on_signal(*args):
                    received[0] = True
                    loop.quit()
                
                signal.connect(on_signal)
                QTimer.singleShot(timeout, loop.quit)
                loop.exec()
                return received[0]
        
        return MinimalQtBot(qapp)


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "qt: marks tests as requiring Qt"
    )
