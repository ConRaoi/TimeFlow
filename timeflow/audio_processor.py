import math
import array
import sys
from PySide6.QtCore import QObject, Signal, QByteArray
from PySide6.QtMultimedia import (
    QAudioSource, QAudioFormat, QMediaDevices, QAudioInput,
    QMediaCaptureSession
)

class AudioProcessor(QObject):
    """
    Erfasst Audio-Daten vom Mikrofon und berechnet den RMS-Pegel.
    Nutzt QMediaCaptureSession, um macOS-Berechtigungen zu erzwingen.
    """
    levelUpdated = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = QMediaCaptureSession(self)
        self.audio_input = QAudioInput(self)
        self.audio_input.setVolume(1.0)
        self.audio_input.setMuted(False)
        self.session.setAudioInput(self.audio_input)
        
        self.audio_source = None
        self.io_device = None
        self.sensitivity = 1.0

    def start(self):
        # 1. Device check
        device = QMediaDevices.defaultAudioInput()
        if not device.isNull():
            self.audio_input.setDevice(device)
        else:
            return

        # 2. Format Negotiation
        format = device.preferredFormat()
        
        # Fallback setup if preferred format is invalid
        if format.sampleRate() < 0:
            format.setSampleRate(44100)
        if format.channelCount() <= 0:
            format.setChannelCount(1)
        
        # We prefer Float for simpler processing, but accept Int16
        if QAudioFormat.SampleFormat.Float not in device.supportedSampleFormats():
             format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        else:
             format.setSampleFormat(QAudioFormat.SampleFormat.Float)

        # 3. Source setup
        self.audio_source = QAudioSource(device, format, self)
        self.audio_source.setBufferSize(16384) # 16k buffer is usually enough for responsiveness
        
        self.io_device = self.audio_source.start()
        
        if self.io_device:
            self.io_device.readyRead.connect(self._process_data)
        else:
            # Fallback for errors
            pass

    def stop(self):
        if self.audio_source:
            self.audio_source.stop()
            self.audio_source = None
        self.io_device = None

    def set_sensitivity(self, value: float):
        self.sensitivity = value

    def _process_data(self):
        if not self.io_device:
            return
            
        q_data = self.io_device.readAll()
        if q_data.isEmpty():
            return

        raw_bytes = bytes(q_data.data())
        
        fmt = self.audio_source.format()
        samples = []
        max_val = 1.0

        try:
            sample_fmt = fmt.sampleFormat()
            if sample_fmt == QAudioFormat.SampleFormat.Float:
                samples = array.array('f', raw_bytes)
                max_val = 1.0
            elif sample_fmt == QAudioFormat.SampleFormat.Int16:
                samples = array.array('h', raw_bytes)
                max_val = 32768.0
            elif sample_fmt == QAudioFormat.SampleFormat.Int32:
                samples = array.array('i', raw_bytes)
                max_val = 2147483648.0
            elif sample_fmt == QAudioFormat.SampleFormat.UInt8:
                raw_ptr = array.array('B', raw_bytes)
                samples = [float(x) - 128.0 for x in raw_ptr]
                max_val = 128.0
        except Exception:
            return

        if not samples:
            return

        # RMS Calculation
        try:
            sum_sq = sum(float(s)**2 for s in samples)
            rms = math.sqrt(sum_sq / len(samples))
            
            # Subtiler Boost und Skalierung
            # rms / max_val liegt bei normaler Sprache oft nur bei 0.01 - 0.05
            # Wir nutzen einen Multiplikator der die Sensitivity stärker gewichtet
            level = (rms / max_val) * 150.0 * self.sensitivity # Mittelweg
            self.levelUpdated.emit(min(100.0, float(level)))
        except Exception:
            pass

