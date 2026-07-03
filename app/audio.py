import threading
import numpy as np
import soundcard as sc


class AudioEngine:

    def __init__(self, callback=None):

        self.callback = callback

        self.running = False
        self.thread = None

        self.speaker = None
        self.devices = []

        self.sample_rate = 48000
        self.block_size = 1024

        self.sensitivity = 1.2

        self.last_rgb = (0, 0, 0)

    # =========================
    # DEVICE LIST
    # =========================

    def get_output_devices(self):

        self.devices = sc.all_speakers()
        return [d.name for d in self.devices]

    def get_default_output(self):

        self.speaker = sc.default_speaker()
        return self.speaker.name

    def select_output(self, index):

        self.devices = sc.all_speakers()

        if index < 0 or index >= len(self.devices):
            return False

        self.speaker = self.devices[index]
        return True

    # =========================
    # START / STOP
    # =========================

    def start(self):

        if self.running:
            return

        if self.speaker is None:
            self.speaker = sc.default_speaker()

        self.running = True

        self.thread = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self.thread.start()

    def stop(self):

        self.running = False

        if self.thread:
            self.thread.join(timeout=1)

    # =========================
    # AUDIO LOOP (WASAPI LOOPBACK)
    # =========================

    def _loop(self):

        try:

            with self.speaker.recorder(
                samplerate=self.sample_rate,
                channels=2,
                include_loopback=True
            ) as rec:

                while self.running:

                    data = rec.record(self.block_size)
                    self.process_audio(data)

        except Exception as e:
            print("AUDIO ERROR:", e)
            self.running = False

    # =========================
    # PROCESS AUDIO
    # =========================

    def process_audio(self, data):

        if data is None or len(data) == 0:
            return

        # stereo -> mono
        mono = np.mean(data, axis=1)

        # FFT
        fft = np.abs(np.fft.rfft(mono))
        freqs = np.fft.rfftfreq(len(mono), 1 / self.sample_rate)

        bass = self._band_energy(freqs, fft, 20, 250)
        mid = self._band_energy(freqs, fft, 250, 4000)
        treble = self._band_energy(freqs, fft, 4000, 16000)

        r, g, b = self.map_to_rgb(bass, mid, treble)

        rgb = (r, g, b)

        # anti spam
        if rgb == self.last_rgb:
            return

        self.last_rgb = rgb

        if self.callback:
            self.callback(r, g, b)

    # =========================
    # FREQUENCY BANDS
    # =========================

    def _band_energy(self, freqs, fft, low, high):

        idx = np.where((freqs >= low) & (freqs <= high))[0]

        if len(idx) == 0:
            return 0

        value = np.mean(fft[idx])

        return value

    # =========================
    # RGB MAPPING
    # =========================

    def map_to_rgb(self, bass, mid, treble):

        # normalize
        bass = min(bass * self.sensitivity / 1000, 1.0)
        mid = min(mid * self.sensitivity / 1000, 1.0)
        treble = min(treble * self.sensitivity / 1000, 1.0)

        r = int(bass * 255)
        g = int(mid * 255)
        b = int(treble * 255)

        return r, g, b

    # =========================
    # SETTINGS
    # =========================

    def set_sensitivity(self, value):

        self.sensitivity = value