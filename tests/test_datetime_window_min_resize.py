import pytest
from timeflow.datetime_window import DateTimeWindow

@pytest.mark.qt
def test_allow_smaller_than_sizehint(qapp, qtbot):
    w = DateTimeWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    hint = w.sizeHint()
    # Try to shrink below the hint - should be possible now
    w.resize(200, 160)
    qtbot.wait(50)

    assert w.width() == 200
    assert w.height() == 160

    # Fonts should still be valid and > 0
    assert w.time_label.font().pixelSize() and w.time_label.font().pixelSize() > 0
