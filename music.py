# music.py
import numpy as np

class AudioProcessor:
    def __init__(self):
        self.smoothed_volume = 0.0
        
    def calculate_brightness(self, audio_data, sensitivity):
        """Mengolah gelombang audio mentah menjadi intensitas cahaya dengan kontras tinggi"""
        if len(audio_data.shape) > 1:
            mono_data = np.mean(audio_data, axis=1)
        else:
            mono_data = audio_data

        # Hitung Root Mean Square (Volume bising suara)
        rms = np.sqrt(np.mean(mono_data**2))
        raw_volume = rms * sensitivity
        
        # Kurva Kuadrat: Menekan mid-tone/suara pelan, mendongkrak beat kencang
        raw_volume = raw_volume ** 2.0 
        raw_volume = min(1.0, raw_volume)
        
        # Pemisah Logika Transisi (Attack & Decay)
        if raw_volume > self.smoothed_volume:
            # ATTACK: Beat masuk kencang -> Lampu langsung meledak terang (reaktif)
            self.smoothed_volume = (self.smoothed_volume * 0.05) + (raw_volume * 0.95)
        else:
            # DECAY: Selesai hentakan -> Lampu meredup bertahap secara halus
            self.smoothed_volume = (self.smoothed_volume * 0.5) + (raw_volume * 0.5)
        
        # Noise Gate: Memaksa lampu padam total di jeda hening lagu
        if self.smoothed_volume < 0.02:
            self.smoothed_volume = 0.0
            
        return self.smoothed_volume