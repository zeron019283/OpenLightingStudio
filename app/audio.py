import threading
import numpy as np
import soundcard as sc
import queue
import time


class AudioEngine:

    def __init__(self, rgb_queue):

        # queue dari controller (ke BLE)
        self.rgb_queue = rgb_queue

        self.running = False
        self.thread = None

        # audio config
        self.sample_rate = 44100
        self.block_size = 4096

        # mic selection
        self.mics = sc.all_microphones()
        self.selected_mic = None

        # smoothing
        self.last_rgb = (0, 0, 0)

        # throttle
        self.last_time = 0

        # sensitivity
        self.sensitivity = 1.2

    # =========================
    # MICROPHONE LIST
    # =========================

    def list_microphones(self):
        return [m.name for m in sc.all_microphones()]

    def set_microphone(self, index):

        mics = sc.all_microphones()

        if index < 0 or index >= len(mics):
            return False

        self.selected_mic = mics[index]

        print("MIC SELECTED:", self.selected_mic.name)

        return True

    # =========================
    # OUTPUT DEVICE LIST (OPTIONAL UI)
    # =========================

    def get_output_devices(self):
        return [d.name for d in sc.all_speakers()]

    def select_output(self, index):

        speakers = sc.all_speakers()

        if index < 0 or index >= len(speakers):
            return False

        # hanya untuk referensi (tidak dipakai audio capture)
        self.speaker = speakers[index]

        return True

    def get_default_output(self):
        self.speaker = sc.default_speaker()
        return self.speaker.name

    # =========================
    # START / STOP
    # =========================

    def start(self):

        if self.running:
            return

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
    # AUDIO LOOP (MIC INPUT)
    # =========================

    def _loop(self):

        try:

            # pilih mic
            mic = self.selected_mic if self.selected_mic else sc.default_microphone()

            print("USING MIC:", mic.name)

            with mic.recorder(
                samplerate=self.sample_rate,
                channels=2
            ) as rec:

                while self.running:

                    data = rec.record(self.block_size)

                    self.process_audio(data)

        except Exception as e:
            print("AUDIO ERROR:", e)
            self.running = False

    # =========================
    # AUDIO PROCESS (FFT + RGB)
    # =========================

    def process_audio(self, data):

        if data is None or len(data) == 0:
            return

        now = time.time()

        # throttle (anti lag + fix discontinuity)
        if now - self.last_time < 0.03:
            return

        self.last_time = now

        # stereo -> mono
        mono = np.mean(data, axis=1)

        # FFT
        fft = np.abs(np.fft.rfft(mono))
        freqs = np.fft.rfftfreq(len(mono), 1 / self.sample_rate)

        bass = self._band(freqs, fft, 20, 250)
        mid = self._band(freqs, fft, 250, 4000)
        treble = self._band(freqs, fft, 4000, 16000)

        r, g, b = self._map_rgb(bass, mid, treble)

        # smoothing (anti flicker)
        r = int(self.last_rgb[0] * 0.7 + r * 0.3)
        g = int(self.last_rgb[1] * 0.7 + g * 0.3)
        b = int(self.last_rgb[2] * 0.7 + b * 0.3)

        self.last_rgb = (r, g, b)

        # push ke queue (NON-BLOCKING)
        try:
            self.rgb_queue.put_nowait((r, g, b))
        except:
            pass

    # =========================
    # FREQUENCY BAND
    # =========================

    def _band(self, freqs, fft, low, high):

        idx = np.where((freqs >= low) & (freqs <= high))[0]

        if len(idx) == 0:
            return 0

        return np.mean(fft[idx])

    # =========================
    # RGB MAPPING
    # =========================

    def _map_rgb(self, bass, mid, treble):

        bass = min(bass * self.sensitivity / 1000, 1.0)
        mid = min(mid * self.sensitivity / 1000, 1.0)
        treble = min(treble * self.sensitivity / 1000, 1.0)

        r = int(bass * 255)
        g = int(mid * 255)
        b = int(treble * 255)

        return r, g, b