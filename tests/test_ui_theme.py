import pytest
from PySide6.QtCore import Qt, QSize
from timeflow.main_window import MainWindow
from timeflow.styles import TINY_WIDTH_LIMIT

@pytest.mark.qt
def test_theme_awareness(qapp, qtbot):
    """Test if the app correctly identifies and applies themes."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Check is_dark_mode helper (depends on system but should not crash)
    is_dark = window.is_dark_mode()
    assert isinstance(is_dark, bool)
    
    # Manual refresh check
    window.refresh_theme()
    # No crash and stylesheet is applied
    assert window.styleSheet() != ""

@pytest.mark.qt
def test_focus_mode_button_visibility(qapp, qtbot):
    """Test if optional buttons are hidden in focus mode."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show() # Ensure layouts are processed
    
    # Normal Mode (Default)
    window.focus_btn.setChecked(False)
    # Trigger responsive update
    window._apply_responsive()
    
    assert window.date_btn.isVisible()
    assert window.noise_btn.isVisible()
    assert window.readme_btn.isVisible()
    
    # Focus Mode
    window.focus_btn.setChecked(True)
    window._apply_responsive()
    
    # Optional buttons should be hidden
    assert not window.date_btn.isVisible()
    assert not window.noise_btn.isVisible()
    assert not window.readme_btn.isVisible()
    assert not window.bug_btn.isVisible()
    
    # Essential buttons should still be visible
    assert window.pin_btn.isVisible()
    assert window.focus_btn.isVisible()

@pytest.mark.qt
def test_tiny_mode_visibility(qapp, qtbot):
    """Test button visibility in extremely small sizes (Tiny Mode)."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Resize to tiny
    window.resize(TINY_WIDTH_LIMIT - 10, 300)
    window._apply_responsive()
    
    # In tiny mode, almost everything except timer is hidden
    assert not window.date_btn.isVisible()
    assert not window.noise_btn.isVisible()
    assert not window.pin_btn.isVisible()
    assert not window.focus_btn.isVisible()
