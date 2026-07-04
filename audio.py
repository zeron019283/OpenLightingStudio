# audio.py
import soundcard as sc

class AudioCapture:
    def __init__(self):
        self.mic = None
        
    def get_audio_devices(self):
        """Mendapatkan daftar mikrofon dan speaker loopback Windows"""
        mics = sc.all_microphones(include_loopback=True)
        devices = {}
        for m in mics:
            devices[m.name] = m
        return devices

    def set_device(self, device_obj):
        """Menentukan sumber audio aktif"""
        self.mic = device_obj