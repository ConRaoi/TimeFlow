import pytest
import time
from unittest.mock import patch
from timeflow.timer_engine import TimerEngine
from timeflow.segments_model import SegmentsModel, Segment
from timeflow.main_window import MainWindow

class TestTimerEngineImprovements:
    def test_seek_clamping(self, qtbot):
        engine = TimerEngine()
        engine.set_total_seconds(100)
        
        # Seek beyond max
        engine.seek(150)
        assert engine.elapsed_seconds() == 100
        
        # Seek below min
        engine.seek(-10)
        assert engine.elapsed_seconds() == 0

    def test_seek_while_running(self, qtbot):
        engine = TimerEngine()
        engine.set_total_seconds(100)
        engine.start()
        
        initial_elapsed = engine.elapsed_seconds()
        engine.seek(50)
        
        assert engine._running is True
        assert engine.elapsed_seconds() >= 50
        assert engine.elapsed_seconds() < 51

    def test_pause_persistence_logic(self, qtbot):
        """
        Regression test for the bug where pause() would reset time or use stale data.
        """
        engine = TimerEngine()
        engine.set_total_seconds(10)
        engine.start()
        
        qtbot.wait(200) # Wait 0.2s
        engine.pause()
        elapsed1 = engine.elapsed_seconds()
        assert elapsed1 >= 0.15
        
        qtbot.wait(100)
        # Should NOT have changed while paused
        assert engine.elapsed_seconds() == elapsed1
        
        engine.start()
        qtbot.wait(200)
        engine.pause()
        elapsed2 = engine.elapsed_seconds()
        assert elapsed2 >= elapsed1 + 0.15

class TestSkipLogic:
    @pytest.fixture
    def app(self, qtbot):
        # Mock the updater to prevent network requests and thread issues
        with patch("timeflow.updater.UpdateWorker.check_updates"):
            window = MainWindow()
            qtbot.addWidget(window)
            yield window
            window.close()
            qtbot.wait(100) # Give it a moment to clean up threads

    def test_skip_next_logic(self, app, qtbot):
        # Setup 2 segments: 1 min, 1 min
        app.segments_model.set_segments([
            Segment("S1", 1),
            Segment("S2", 1)
        ])
        app.engine.set_total_seconds(120)
        
        # Start at 0
        assert app.engine.elapsed_seconds() == 0
        
        # Skip next -> should jump to 60s
        app.on_skip_next()
        assert app.engine.elapsed_seconds() == 60
        
        # Skip next again -> should jump to 120s (end)
        app.on_skip_next()
        assert app.engine.elapsed_seconds() == 120

    def test_skip_prev_restart_logic(self, app, qtbot):
        app.segments_model.set_segments([
            Segment("S1", 1)
        ])
        app.engine.set_total_seconds(60)
        
        # Seek to 10s (> 2s threshold)
        app.engine.seek(10)
        
        # Skip prev -> should restart current segment (0s)
        app.on_skip_prev()
        assert app.engine.elapsed_seconds() == 0

    def test_skip_prev_back_logic(self, app, qtbot):
        app.segments_model.set_segments([
            Segment("S1", 1),
            Segment("S2", 1)
        ])
        app.engine.set_total_seconds(120)
        
        # Seek to 61s (1s into segment 2, so < 2s threshold)
        app.engine.seek(61)
        
        # Skip prev -> should go to start of segment 1 (0s)
        app.on_skip_prev()
        assert app.engine.elapsed_seconds() == 0
        
    def test_skip_prev_boundary_logic(self, app, qtbot):
        app.segments_model.set_segments([
            Segment("S1", 1),
            Segment("S2", 1)
        ])
        app.engine.set_total_seconds(120)
        
        # Seek to 70s (> 2s into segment 2)
        app.engine.seek(70)
        
        # Skip prev -> should go to 60s (start of S2)
        app.on_skip_prev()
        assert app.engine.elapsed_seconds() == 60
