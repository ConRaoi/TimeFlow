import pytest
from timeflow.noise_meter_window import NoiseMeterWindow
from PySide6.QtWidgets import QVBoxLayout

@pytest.mark.qt
def test_noise_meter_layout_emphasis(qapp, qtbot):
    w = NoiseMeterWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    root = w.layout()
    assert isinstance(root, QVBoxLayout)

    # Settings spacing reduced to make sliders less prominent
    # Find settings layout - it's the last item
    settings_item = root.itemAt(root.count()-1)
    settings = settings_item.layout()
    assert settings.spacing() <= 8

    # Labels and sliders are less dominant
    assert w.sens_label.minimumWidth() <= 100
    assert w.limit_label.minimumWidth() <= 100
    assert w.sens_slider.minimumHeight() <= 32
    assert w.limit_slider.minimumHeight() <= 32

    # Meter should have larger stretch than settings
    # Index 1 is meter, last is settings; check stretch values
    meter_stretch = root.stretch(1)
    settings_stretch = root.stretch(root.count()-1)
    assert meter_stretch >= settings_stretch * 2
