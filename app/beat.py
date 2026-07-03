import numpy as np
import time


class BeatDetector:

    def __init__(self):

        self.energy_history = []
        self.history_size = 43  # ~1 detik di 44.1kHz frame kecil

        self.last_beat_time = 0
        self.cooldown = 0.2  # 200ms anti spam beat

    def detect(self, signal_energy):

        self.energy_history.append(signal_energy)

        if len(self.energy_history) > self.history_size:
            self.energy_history.pop(0)

        if len(self.energy_history) < self.history_size:
            return False

        avg_energy = np.mean(self.energy_history)
        variance = np.var(self.energy_history)

        threshold = avg_energy + (np.sqrt(variance) * 1.5)

        now = time.time()

        if signal_energy > threshold and (now - self.last_beat_time) > self.cooldown:
            self.last_beat_time = now
            return True

        return False