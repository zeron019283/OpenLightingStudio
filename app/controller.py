import asyncio
import threading

from app.ble import BLEController
from app.audio import AudioEngine


class LightingController:

    def __init__(self):

        self.ble = BLEController()
        self.devices = []
        self.selected = None

        # AUDIO ENGINE
        self.audio = None
        self.music_running = False

    # =========================
    # SCAN
    # =========================

    async def scan(self):
        self.devices = await self.ble.scan()
        return self.devices

    # =========================
    # CONNECT
    # =========================

    async def connect(self, index):

        if not self.devices:
            return False

        if index < 0 or index >= len(self.devices):
            return False

        self.selected = self.devices[index]

        return await self.ble.connect(
            self.selected["address"],
            self.selected["mode"]
        )

    # =========================
    # DISCONNECT
    # =========================

    async def disconnect(self):
        return await self.ble.disconnect()

    # =========================
    # BASIC CONTROL
    # =========================

    async def on(self):
        return await self.ble.on()

    async def off(self):
        return await self.ble.off()

    async def red(self):
        return await self.ble.red()

    async def green(self):
        return await self.ble.green()

    async def blue(self):
        return await self.ble.blue()

    async def set_rgb(self, r, g, b):
        return await self.ble.set_rgb(r, g, b)

    # =========================
    # AUDIO CALLBACK
    # =========================

    def _on_audio(self, r, g, b):

        if not self.music_running:
            return

        asyncio.run(self.ble.set_rgb(r, g, b))

    # =========================
    # MUSIC MODE
    # =========================

    def start_music_mode(self):

        if self.music_running:
            return

        self.music_running = True

        self.audio = AudioEngine(self._on_audio)

        # optional: set default device
        self.audio.get_default_output()

        self.audio.start()

        print("Music Mode Started")

    def stop_music_mode(self):

        self.music_running = False

        if self.audio:
            self.audio.stop()
            self.audio = None

        print("Music Mode Stopped")

    # =========================
    # OUTPUT DEVICE CONTROL
    # =========================

    def get_audio_devices(self):
        if not self.audio:
            self.audio = AudioEngine(self._on_audio)

        return self.audio.get_output_devices()

    def set_audio_device(self, index):

        if not self.audio:
            self.audio = AudioEngine(self._on_audio)

        return self.audio.select_output(index)