"""
Comprehensive Test Suite for TimeFlow Application
Tests all core functionality including:
- Timer Engine
- Segments Model
- I18n/Localization
- Presets Manager
- UI Components (where possible without display)
- Utils
"""

import pytest
import time
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# ============================================================================
# TIMER ENGINE TESTS
# ============================================================================

class TestTimerEngine:
    """Tests for timeflow/timer_engine.py"""

    def test_timer_engine_import(self):
        """Test that TimerEngine can be imported."""
        from timeflow.timer_engine import TimerEngine, TimerState
        assert TimerEngine is not None
        assert TimerState is not None

    def test_timer_state_dataclass(self):
        """Test TimerState dataclass creation."""
        from timeflow.timer_engine import TimerState
        state = TimerState(running=True, elapsed_s=10.5, total_s=60.0)
        assert state.running == True
        assert state.elapsed_s == 10.5
        assert state.total_s == 60.0

    def test_timer_engine_initialization(self, qtbot):
        """Test TimerEngine initializes with correct defaults."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        assert engine.elapsed_seconds() == 0.0
        assert engine._running == False
        assert engine._total_s == 0.0

    def test_timer_engine_set_total_seconds(self, qtbot):
        """Test setting total seconds."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(120.0)
        assert engine._total_s == 120.0

    def test_timer_engine_set_total_seconds_negative(self, qtbot):
        """Test that negative total seconds are clamped to 0."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(-50.0)
        assert engine._total_s == 0.0

    def test_timer_engine_start_stop(self, qtbot):
        """Test starting and pausing the timer."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(60.0)
        
        # Start
        engine.start()
        assert engine._running == True
        
        # Pause
        engine.pause()
        assert engine._running == False

    def test_timer_engine_reset(self, qtbot):
        """Test resetting the timer."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(60.0)
        engine.start()
        time.sleep(0.15)  # Let it run briefly
        engine.reset()
        assert engine._running == False
        assert engine.elapsed_seconds() == 0.0

    def test_timer_engine_toggle(self, qtbot):
        """Test toggle functionality."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(60.0)
        
        engine.toggle()
        assert engine._running == True
        
        engine.toggle()
        assert engine._running == False

    def test_timer_engine_tick_signal(self, qtbot):
        """Test that tick signal is emitted."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(60.0)
        
        signals_received = []
        engine.tick.connect(lambda state: signals_received.append(state))
        
        engine.start()
        qtbot.wait(200)  # Wait for at least one tick
        engine.pause()
        
        assert len(signals_received) >= 1

    def test_timer_engine_finished_signal(self, qtbot):
        """Test that finished signal is emitted when timer completes."""
        from timeflow.timer_engine import TimerEngine
        engine = TimerEngine()
        engine.set_total_seconds(0.2)  # Very short duration
        
        finished_called = []
        engine.finished.connect(lambda: finished_called.append(True))
        
        engine.start()
        qtbot.wait(500)  # Wait for completion
        
        assert len(finished_called) >= 1


# ============================================================================
# SEGMENTS MODEL TESTS
# ============================================================================

class TestSegmentsModel:
    """Tests for timeflow/segments_model.py"""

    def test_segment_dataclass(self):
        """Test Segment dataclass creation."""
        from timeflow.segments_model import Segment
        seg = Segment(name="Test", minutes=5.0)
        assert seg.name == "Test"
        assert seg.minutes == 5.0

    def test_model_initialization(self):
        """Test SegmentsModel initialization."""
        from timeflow.segments_model import SegmentsModel
        model = SegmentsModel()
        assert model.rowCount() == 0
        assert model.columnCount() == 2

    def test_model_with_initial_segments(self):
        """Test SegmentsModel with initial segments."""
        from timeflow.segments_model import SegmentsModel, Segment
        segs = [Segment("A", 3), Segment("B", 5)]
        model = SegmentsModel(segments=segs)
        assert model.rowCount() == 2

    def test_model_set_segments(self):
        """Test setting segments."""
        from timeflow.segments_model import SegmentsModel, Segment
        model = SegmentsModel()
        model.set_segments([Segment("X", 10), Segment("Y", 20)])
        assert model.rowCount() == 2
        assert model.segments()[0].name == "X"
        assert model.segments()[1].minutes == 20

    def test_model_total_seconds(self):
        """Test total_seconds calculation."""
        from timeflow.segments_model import SegmentsModel, Segment
        model = SegmentsModel(segments=[Segment("A", 1), Segment("B", 2)])
        # 1 + 2 = 3 minutes = 180 seconds
        assert model.total_seconds() == 180.0

    def test_model_total_seconds_empty(self):
        """Test total_seconds with no segments."""
        from timeflow.segments_model import SegmentsModel
        model = SegmentsModel()
        assert model.total_seconds() == 0.0

    def test_model_data_display_role(self):
        """Test data retrieval with DisplayRole."""
        from timeflow.segments_model import SegmentsModel, Segment
        from PySide6.QtCore import Qt
        model = SegmentsModel(segments=[Segment("Test", 5.5)])
        
        name = model.data(model.index(0, 0), Qt.DisplayRole)
        minutes = model.data(model.index(0, 1), Qt.DisplayRole)
        
        assert name == "Test"
        assert minutes == "5.5"

    def test_model_set_data(self):
        """Test editing segment data."""
        from timeflow.segments_model import SegmentsModel, Segment
        from PySide6.QtCore import Qt
        model = SegmentsModel(segments=[Segment("Old", 1)])
        
        # Change name
        result = model.setData(model.index(0, 0), "New", Qt.EditRole)
        assert result == True
        assert model.segments()[0].name == "New"
        
        # Change minutes
        result = model.setData(model.index(0, 1), 10.0, Qt.EditRole)
        assert result == True
        assert model.segments()[0].minutes == 10.0

    def test_model_insert_rows(self):
        """Test inserting new rows."""
        from timeflow.segments_model import SegmentsModel
        model = SegmentsModel()
        
        result = model.insertRows(0, 1)
        assert result == True
        assert model.rowCount() == 1

    def test_model_remove_rows(self):
        """Test removing rows."""
        from timeflow.segments_model import SegmentsModel, Segment
        model = SegmentsModel(segments=[Segment("A", 1), Segment("B", 2)])
        
        result = model.removeRows(0, 1)
        assert result == True
        assert model.rowCount() == 1
        assert model.segments()[0].name == "B"

    def test_model_headers(self):
        """Test header data."""
        from timeflow.segments_model import SegmentsModel
        from PySide6.QtCore import Qt
        model = SegmentsModel(headers=("Name", "Minutes"))
        
        assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Name"
        assert model.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Minutes"

    def test_model_set_headers(self):
        """Test changing headers for localization."""
        from timeflow.segments_model import SegmentsModel
        from PySide6.QtCore import Qt
        model = SegmentsModel()
        model.set_headers("Nombre", "Minutos")
        
        assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Nombre"
        assert model.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Minutos"


# ============================================================================
# I18N/LOCALIZATION TESTS
# ============================================================================

class TestI18n:
    """Tests for timeflow/i18n.py"""

    def test_supported_langs(self):
        """Test that SUPPORTED_LANGS is defined."""
        from timeflow.i18n import SUPPORTED_LANGS
        assert len(SUPPORTED_LANGS) >= 4
        codes = [code for code, label in SUPPORTED_LANGS]
        assert "en" in codes
        assert "de" in codes
        assert "es" in codes
        assert "fr" in codes

    def test_get_strings_english(self):
        """Test English strings."""
        from timeflow.i18n import get_strings
        s = get_strings("en")
        assert s.app_title == "TimeFlow"
        assert s.start == "Start"
        assert s.pause == "Pause"
        assert s.reset == "Reset"

    def test_get_strings_german(self):
        """Test German strings."""
        from timeflow.i18n import get_strings
        s = get_strings("de")
        assert s.app_title == "TimeFlow"
        assert s.language_label == "Sprache"
        assert s.segments_label == "Segmente"

    def test_get_strings_spanish(self):
        """Test Spanish strings."""
        from timeflow.i18n import get_strings
        s = get_strings("es")
        assert s.language_label == "Idioma"
        assert s.segments_label == "Segmentos"

    def test_get_strings_french(self):
        """Test French strings."""
        from timeflow.i18n import get_strings
        s = get_strings("fr")
        assert s.language_label == "Langue"
        assert s.segments_label == "Segments"

    def test_get_strings_unknown_fallback(self):
        """Test that unknown language codes fall back to English."""
        from timeflow.i18n import get_strings
        s = get_strings("xyz")
        assert s.app_title == "TimeFlow"
        assert s.start == "Start"

    def test_strings_have_default_segments(self):
        """Test that all languages have default segments."""
        from timeflow.i18n import get_strings
        for lang in ["en", "de", "es", "fr"]:
            s = get_strings(lang)
            assert len(s.default_segments) >= 3
            for name, minutes in s.default_segments:
                assert isinstance(name, str)
                assert isinstance(minutes, (int, float))

    def test_strings_have_preset_fields(self):
        """Test that preset-related strings exist."""
        from timeflow.i18n import get_strings
        s = get_strings("en")
        assert hasattr(s, 'presets_label')
        assert hasattr(s, 'save_preset')
        assert hasattr(s, 'manage_presets')
        assert hasattr(s, 'preset_saved')
        assert hasattr(s, 'preset_loaded')


# ============================================================================
# UTILS TESTS
# ============================================================================

class TestUtils:
    """Tests for timeflow/utils.py"""

    def test_format_mmss_zero(self):
        """Test formatting zero seconds."""
        from timeflow.utils import format_mmss
        assert format_mmss(0) == "00:00"

    def test_format_mmss_seconds_only(self):
        """Test formatting seconds under a minute."""
        from timeflow.utils import format_mmss
        assert format_mmss(30) == "00:30"
        assert format_mmss(59) == "00:59"

    def test_format_mmss_minutes(self):
        """Test formatting minutes."""
        from timeflow.utils import format_mmss
        assert format_mmss(60) == "01:00"
        assert format_mmss(90) == "01:30"
        assert format_mmss(600) == "10:00"

    def test_format_mmss_large(self):
        """Test formatting large values."""
        from timeflow.utils import format_mmss
        assert format_mmss(3600) == "60:00"  # 1 hour
        assert format_mmss(3661) == "61:01"

    def test_format_mmss_negative(self):
        """Test formatting negative values (should clamp to 0)."""
        from timeflow.utils import format_mmss
        assert format_mmss(-10) == "00:00"

    def test_format_mmss_float(self):
        """Test formatting float values (should round)."""
        from timeflow.utils import format_mmss
        assert format_mmss(30.4) == "00:30"
        assert format_mmss(30.6) == "00:31"

    def test_clamp_within_range(self):
        """Test clamp with value in range."""
        from timeflow.utils import clamp
        assert clamp(5, 0, 10) == 5

    def test_clamp_below_min(self):
        """Test clamp with value below minimum."""
        from timeflow.utils import clamp
        assert clamp(-5, 0, 10) == 0

    def test_clamp_above_max(self):
        """Test clamp with value above maximum."""
        from timeflow.utils import clamp
        assert clamp(15, 0, 10) == 10

    def test_clamp_at_boundaries(self):
        """Test clamp at exact boundaries."""
        from timeflow.utils import clamp
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_resource_path(self):
        """Test resource_path function."""
        from timeflow.utils import resource_path
        import os
        path = resource_path("test.txt")
        assert isinstance(path, str)
        # Should be an absolute path
        assert os.path.isabs(path)


# ============================================================================
# PRESETS MANAGER TESTS
# ============================================================================

class TestPresetsManager:
    """Tests for timeflow/presets_manager.py"""

    @pytest.fixture
    def temp_presets_dir(self, tmp_path):
        """Create a temporary directory for presets."""
        return tmp_path

    @pytest.fixture
    def manager(self, temp_presets_dir):
        """Create a PresetsManager with mocked storage path."""
        from timeflow.presets_manager import PresetsManager
        manager = PresetsManager()
        # Patch the storage path
        manager._get_storage_path = lambda: temp_presets_dir / "presets.json"
        return manager

    def test_presets_manager_import(self):
        """Test that PresetsManager can be imported."""
        from timeflow.presets_manager import PresetsManager
        assert PresetsManager is not None

    def test_load_presets_empty(self, manager):
        """Test loading presets when file doesn't exist."""
        presets = manager.load_presets()
        assert presets == []

    def test_save_preset(self, manager):
        """Test saving a preset."""
        segments = [{"name": "Intro", "minutes": 5}, {"name": "Work", "minutes": 20}]
        result = manager.save_preset("Test Preset", segments)
        assert result == True
        
        # Verify it was saved
        presets = manager.load_presets()
        assert len(presets) == 1
        assert presets[0]["name"] == "Test Preset"

    def test_save_multiple_presets(self, manager):
        """Test saving multiple presets."""
        manager.save_preset("Preset 1", [{"name": "A", "minutes": 1}])
        manager.save_preset("Preset 2", [{"name": "B", "minutes": 2}])
        
        presets = manager.load_presets()
        assert len(presets) == 2

    def test_overwrite_preset(self, manager):
        """Test overwriting an existing preset."""
        manager.save_preset("MyPreset", [{"name": "Old", "minutes": 1}])
        manager.save_preset("MyPreset", [{"name": "New", "minutes": 2}])
        
        presets = manager.load_presets()
        assert len(presets) == 1
        assert presets[0]["segments"][0]["name"] == "New"

    def test_delete_preset(self, manager):
        """Test deleting a preset."""
        manager.save_preset("ToDelete", [{"name": "X", "minutes": 1}])
        manager.save_preset("ToKeep", [{"name": "Y", "minutes": 2}])
        
        result = manager.delete_preset("ToDelete")
        assert result == True
        
        presets = manager.load_presets()
        assert len(presets) == 1
        assert presets[0]["name"] == "ToKeep"

    def test_delete_nonexistent_preset(self, manager):
        """Test deleting a preset that doesn't exist."""
        result = manager.delete_preset("NonExistent")
        assert result == False

    def test_rename_preset(self, manager):
        """Test renaming a preset."""
        manager.save_preset("OldName", [{"name": "X", "minutes": 1}])
        
        result = manager.rename_preset("OldName", "NewName")
        assert result == True
        
        presets = manager.load_presets()
        assert presets[0]["name"] == "NewName"


# ============================================================================
# PIE WIDGET TESTS
# ============================================================================

class TestPieWidget:
    """Tests for timeflow/pie_widget.py"""

    def test_pie_widget_import(self):
        """Test that PieWidget can be imported."""
        from timeflow.pie_widget import PieWidget
        assert PieWidget is not None

    def test_pie_widget_creation(self, qtbot):
        """Test creating a PieWidget."""
        from timeflow.pie_widget import PieWidget
        widget = PieWidget()
        qtbot.addWidget(widget)
        assert widget is not None

    def test_pie_widget_set_segments(self, qtbot):
        """Test setting segments on PieWidget."""
        from timeflow.pie_widget import PieWidget
        from timeflow.segments_model import Segment
        widget = PieWidget()
        qtbot.addWidget(widget)
        
        segments = [Segment("A", 10), Segment("B", 20)]
        widget.set_segments(segments)
        assert widget._segments == segments

    def test_pie_widget_set_progress(self, qtbot):
        """Test setting progress on PieWidget."""
        from timeflow.pie_widget import PieWidget
        widget = PieWidget()
        qtbot.addWidget(widget)
        
        widget.set_progress(0.5)
        assert widget._progress == 0.5

    def test_pie_widget_progress_clamped(self, qtbot):
        """Test that progress is clamped to 0-1."""
        from timeflow.pie_widget import PieWidget
        widget = PieWidget()
        qtbot.addWidget(widget)
        
        widget.set_progress(1.5)
        assert widget._progress == 1.0
        
        widget.set_progress(-0.5)
        assert widget._progress == 0.0


# ============================================================================
# STYLES TESTS
# ============================================================================

class TestStyles:
    """Tests for timeflow/styles.py"""

    def test_styles_import(self):
        """Test that styles module can be imported."""
        from timeflow.styles import (
            MARGIN_STD, SPACING_STD, MARGIN_COMPACT, SPACING_COMPACT,
            TINY_WIDTH_LIMIT, TINY_HEIGHT_LIMIT,
            COMPACT_WIDTH_LIMIT, COMPACT_HEIGHT_LIMIT,
            get_stylesheet
        )
        assert MARGIN_STD > 0
        assert SPACING_STD > 0

    def test_get_stylesheet_returns_string(self):
        """Test that get_stylesheet returns a string."""
        from timeflow.styles import get_stylesheet
        css = get_stylesheet()
        assert isinstance(css, str)
        assert len(css) > 0

    def test_stylesheet_contains_main_selectors(self):
        """Test that stylesheet contains expected selectors."""
        from timeflow.styles import get_stylesheet
        css = get_stylesheet()
        assert "QWidget" in css
        assert "QPushButton" in css
        assert "QComboBox" in css
        assert "QTableView" in css

    def test_constants_reasonable_values(self):
        """Test that layout constants have reasonable values."""
        from timeflow.styles import (
            MARGIN_STD, SPACING_STD,
            TINY_WIDTH_LIMIT, COMPACT_WIDTH_LIMIT
        )
        assert MARGIN_STD <= 50
        assert SPACING_STD <= 50
        assert TINY_WIDTH_LIMIT < COMPACT_WIDTH_LIMIT


# ============================================================================
# VERSION TESTS
# ============================================================================

class TestVersion:
    """Tests for timeflow/version.py"""

    def test_version_import(self):
        """Test that version can be imported."""
        from timeflow.version import __version__
        assert __version__ is not None

    def test_version_format(self):
        """Test that version has expected format."""
        from timeflow.version import __version__
        parts = __version__.split(".")
        assert len(parts) >= 2
        # All parts should be numeric
        for part in parts:
            assert part.isdigit() or part.replace(".", "").isdigit()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""

    def test_timer_with_segments(self, qtbot):
        """Test timer engine with segments model."""
        from timeflow.timer_engine import TimerEngine
        from timeflow.segments_model import SegmentsModel, Segment
        
        model = SegmentsModel(segments=[
            Segment("Intro", 1),  # 1 minute = 60 seconds
            Segment("Work", 2),  # 2 minutes = 120 seconds
        ])
        
        engine = TimerEngine()
        engine.set_total_seconds(model.total_seconds())
        
        assert engine._total_s == 180.0  # 3 minutes total

    def test_localization_flow(self):
        """Test switching between languages."""
        from timeflow.i18n import get_strings
        from timeflow.segments_model import SegmentsModel, Segment
        
        model = SegmentsModel()
        
        # Set English headers
        s_en = get_strings("en")
        model.set_headers(s_en.col_name, s_en.col_minutes)
        
        from PySide6.QtCore import Qt
        assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Name"
        
        # Switch to German
        s_de = get_strings("de")
        model.set_headers(s_de.col_name, s_de.col_minutes)
        assert model.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Minuten"


# ============================================================================
# CONFTEST / FIXTURES
# ============================================================================

@pytest.fixture
def qtbot(qtbot):
    """Enhanced qtbot fixture."""
    return qtbot


# Run with: pytest tests/test_timeflow.py -v
