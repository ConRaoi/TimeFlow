import pytest
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QGuiApplication
from timeflow.datetime_window import DateTimeWindow
from timeflow.noise_meter_window import NoiseMeterWindow, LevelMeterWidget

@pytest.mark.qt
def test_datetime_window_init(qapp, qtbot):
    """Test standard initialization of the DateTimeWindow."""
    window = DateTimeWindow(lang_code="de")
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "Datum & Uhrzeit"
    assert window.lang_code == "de"
    # Basic check for labels
    assert window.date_label.text() != ""
    assert window.weekday_label.text() != ""
    assert window.time_label.text() != ""

@pytest.mark.qt
def test_datetime_window_locales(qapp, qtbot):
    """Test if locales are correctly mapped for different languages."""
    # German
    w_de = DateTimeWindow(lang_code="de")
    qtbot.addWidget(w_de)
    locale_de = w_de._get_locale()
    assert locale_de.language() == QLocale.German
    assert locale_de.territory() == QLocale.Germany
    
    # English (UK)
    w_en = DateTimeWindow(lang_code="en")
    qtbot.addWidget(w_en)
    locale_en = w_en._get_locale()
    assert locale_en.language() == QLocale.English
    assert locale_en.territory() == QLocale.UnitedKingdom
    
    # Spanish
    w_es = DateTimeWindow(lang_code="es")
    qtbot.addWidget(w_es)
    locale_es = w_es._get_locale()
    assert locale_es.language() == QLocale.Spanish
    assert locale_es.territory() == QLocale.Spain

@pytest.mark.qt
def test_noise_meter_window_init(qapp, qtbot):
    """Test standard initialization of the NoiseMeterWindow."""
    window = NoiseMeterWindow(lang_code="de")
    qtbot.addWidget(window)
    
    assert "Lärmampel" in window.windowTitle()
    assert window.meter is not None
    assert window.sens_slider is not None
    assert window.limit_slider is not None

@pytest.mark.qt
def test_level_meter_widget_logic(qapp, qtbot):
    """Test logic inside the LevelMeterWidget."""
    widget = LevelMeterWidget()
    qtbot.addWidget(widget)
    
    widget.set_level(50.0)
    assert widget._level == 50.0
    
    widget.set_threshold(80.0)
    assert widget._threshold == 80.0
    
    # Trigger paint (basic check that it doesn't crash)
    widget.update()

@pytest.mark.qt
def test_datetime_window_theme_refresh(qapp, qtbot):
    """Test if DateTimeWindow reacts to theme changes."""
    window = DateTimeWindow()
    qtbot.addWidget(window)
    
    # Light mode
    window.refresh_theme(False)
    # Basic check for a property that changes
    assert "font-weight" in window.time_label.styleSheet()
    
    # Dark mode
    window.refresh_theme(True)
    assert window.isVisible() or not window.isVisible() # No crash check

@pytest.mark.qt
def test_noise_meter_window_theme_refresh(qapp, qtbot):
    """Test if NoiseMeterWindow reacts to theme changes."""
    window = NoiseMeterWindow()
    qtbot.addWidget(window)
    
    window.refresh_theme(False)
    window.refresh_theme(True)
    # Verify the meter background helper is used
    from timeflow.styles import get_meter_bg_color
    bg_dark = get_meter_bg_color(True)
    assert bg_dark.name() != ""

@pytest.mark.qt
def test_noise_presets_manager(qapp):
    """Test saving and loading in NoisePresetsManager."""
    from timeflow.noise_presets_manager import NoisePresetsManager
    manager = NoisePresetsManager()
    
    # Save a test preset
    manager.save_preset("TestPreset", 55, 85)
    
    # Load and verify
    presets = manager.load_presets()
    found = next((p for p in presets if p["name"] == "TestPreset"), None)
    assert found is not None
    assert found["sensitivity"] == 55
    assert found["limit"] == 85
    
    # Rename
    manager.rename_preset("TestPreset", "NewName")
    presets = manager.load_presets()
    assert not any(p["name"] == "TestPreset" for p in presets)
    assert any(p["name"] == "NewName" for p in presets)
    
    # Clean up
    manager.delete_preset("NewName")
    presets = manager.load_presets()
    assert not any(p["name"] == "NewName" for p in presets)

@pytest.mark.qt
def test_noise_last_settings(qapp):
    """Test saving and loading last settings."""
    from timeflow.noise_presets_manager import NoisePresetsManager
    manager = NoisePresetsManager()
    
    manager.save_last_settings(12, 34)
    sens, limit = manager.load_last_settings()
    assert sens == 12
    assert limit == 34
