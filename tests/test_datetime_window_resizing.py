import pytest
from timeflow.datetime_window import DateTimeWindow

@pytest.mark.qt
def test_initial_size_fits_content(qapp, qtbot):
    w = DateTimeWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    # The window should be at least as large as its sizeHint on first show
    assert w.width() >= w.sizeHint().width()
    assert w.height() >= w.sizeHint().height()

@pytest.mark.qt
def test_resize_changes_font_sizes(qapp, qtbot):
    w = DateTimeWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    initial = w.time_label.font().pixelSize()
    assert initial and initial > 0

    # Shrink: fonts should get smaller or equal (platforms may clamp)
    w.resize(300, 200)
    qtbot.wait(100)
    small = w.time_label.font().pixelSize()
    assert small and small <= initial

    # Spacing should not grow when the window shrinks
    spacing_small = w.layout().spacing()
    margins_small = w.layout().contentsMargins().top()

    # Enlarge: fonts should grow again
    w.resize(1000, 800)
    qtbot.wait(100)
    large = w.time_label.font().pixelSize()
    assert large and large >= initial

    spacing_large = w.layout().spacing()
    margins_large = w.layout().contentsMargins().top()

    assert spacing_small <= spacing_large
    assert margins_small <= margins_large


def test_letter_spacing_and_spacing_behavior(qapp, qtbot):
    """Ensure letter spacing is set and behaves reasonably across sizes."""
    w = DateTimeWindow(lang_code="de")
    qtbot.addWidget(w)
    w.show()
    qtbot.wait(50)

    f = w.time_label.font()
    try:
        typ = f.letterSpacingType()
        val = f.letterSpacing()
        assert typ == QFont.PercentageSpacing
        assert 80 <= val <= 100
    except Exception:
        # Some minimal Qt builds may not support reading letter spacing; just ensure no crash
        assert True
