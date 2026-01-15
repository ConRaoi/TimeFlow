import pytest
from timeflow.datetime_window import DateTimeWindow

@pytest.mark.qt
def test_no_prints_after_logging(qapp, qtbot, capsys):
    w = DateTimeWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    # Call update and ensure previous debug prints are not on stdout
    w._update_display()
    captured = capsys.readouterr()
    assert "Aktuelle Zeit:" not in captured.out
    assert "Uhrzeit-String:" not in captured.out
    assert "Datum-String:" not in captured.out
    assert "Wochentag-String:" not in captured.out
    assert "Gewählte Schriftgrößen" not in captured.out
    assert "Geometrien - Zeit" not in captured.out
