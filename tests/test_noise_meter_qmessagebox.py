import pytest
from timeflow.noise_meter_window import NoiseMeterWindow

class DummySaveDialog:
    def __init__(self, parent, lang_code):
        self.preset_name = "x"
    def exec(self):
        return True

class DummyManageDialog:
    def __init__(self, presets_manager, parent, lang_code, data_key="none"):
        self.loaded_data = {"sensitivity": 40, "limit": 60}
    def exec(self):
        return True

@pytest.mark.qt
def test_save_and_manage_call_qmessagebox(qapp, qtbot, monkeypatch):
    w = NoiseMeterWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    # Replace dialogs with dummies so we exercise the code paths till QMessageBox
    monkeypatch.setattr('timeflow.noise_meter_window.SavePresetDialog', DummySaveDialog)
    monkeypatch.setattr('timeflow.noise_meter_window.ManagePresetsDialog', DummyManageDialog)

    called = {'info': False}
    def fake_info(parent, title, text):
        called['info'] = True

    monkeypatch.setattr('timeflow.noise_meter_window.QMessageBox.information', fake_info)

    # Trigger save -> should call QMessageBox.information via our fake
    w._save_preset()
    assert called['info'] is True

    called['info'] = False
    w._manage_presets()
    assert called['info'] is True
