import asyncio
from app.ble import BLEController


class LightingController:

    def __init__(self):
        self.ble = BLEController()
        self.devices = []
        self.selected = None

    # =========================
    # SCAN
    # =========================
    async def scan(self):
        self.devices = await self.ble.scan()
        return self.devices

    # =========================
    # CONNECT (FIXED SAFETY)
    # =========================
    async def connect(self, index):

        try:
            if not self.devices:
                return False

            if index < 0 or index >= len(self.devices):
                return False

            self.selected = self.devices[index]

            return await self.ble.connect(
                self.selected["address"],
                self.selected["mode"]
            )

        except Exception as e:
            print("CONNECT CONTROLLER ERROR:", e)
            return False

    # =========================
    # DISCONNECT
    # =========================
    async def disconnect(self):
        return await self.ble.disconnect()

    # =========================
    # BASIC COMMANDS (FIX RETURN)
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

    # =========================
    # RGB (PASS THROUGH + SAFE)
    # =========================
    async def set_rgb(self, r, g, b):
        return await self.ble.set_rgb(r, g, b)