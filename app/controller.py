import asyncio
import threading
import queue

from app.ble import BLEController
from app.audio import AudioEngine


class LightingController:

    def __init__(self):

        self.ble = BLEController()

        # audio system
        self.audio = None
        self.rgb_queue = None

        self.music_running = False

        # BLE devices
        self.devices = []
        self.selected = None

    # =========================
    # BLE SCAN
    # =========================

    async def scan(self):

        self.devices = await self.ble.scan()
        return self.devices

    # =========================
    # BLE CONNECT
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
    # BLE CONTROL
    # =========================

    async def disconnect(self):
        return await self.ble.disconnect()

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
    # 🔥 IMPORTANT FIX: BRIGHTNESS
    # =========================

    async def set_brightness(self, value):
        return await self.ble.set_brightness(value)

    # =========================
    # AUDIO DEVICES (OUTPUT LIST UI)
    # =========================

    def get_audio_devices(self):

        if not self.audio:
            self.rgb_queue = queue.Queue()
            self.audio = AudioEngine(self.rgb_queue)

        return self.audio.get_output_devices()

    def set_audio_device(self, index):

        if not self.audio:
            self.rgb_queue = queue.Queue()
            self.audio = AudioEngine(self.rgb_queue)

        return self.audio.select_output(index)

    # =========================
    # MICROPHONE CONTROL
    # =========================

    def get_microphones(self):

        if not self.audio:
            self.rgb_queue = queue.Queue()
            self.audio = AudioEngine(self.rgb_queue)

        return self.audio.list_microphones()

    def set_microphone(self, index):

        if not self.audio:
            self.rgb_queue = queue.Queue()
            self.audio = AudioEngine(self.rgb_queue)

        return self.audio.set_microphone(index)

    # =========================
    # MUSIC WORKER (QUEUE → BLE)
    # =========================

    def _music_worker(self):

        while True:

            try:
                r, g, b = self.rgb_queue.get(timeout=1)

                if self.music_running:
                    asyncio.run(self.ble.set_rgb(r, g, b))

            except:
                continue

    # =========================
    # MUSIC MODE START
    # =========================

    def start_music_mode(self):

        if self.music_running:
            return

        self.music_running = True

        self.rgb_queue = queue.Queue()

        self.audio = AudioEngine(self.rgb_queue)

        # default mic
        self.audio.set_microphone(0)

        self.audio.start()

        # BLE sender thread
        threading.Thread(
            target=self._music_worker,
            daemon=True
        ).start()

        print("MUSIC MODE STARTED")

    # =========================
    # MUSIC MODE STOP
    # =========================

    def stop_music_mode(self):

        self.music_running = False

        if self.audio:
            self.audio.stop()

        print("MUSIC MODE STOPPED")