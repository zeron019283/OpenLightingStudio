import asyncio

from app.ble import BLEController


class LightingController:

    def __init__(self):
        self.ble = BLEController()
        self.devices = []
        self.selected = None

    async def scan(self):
        self.devices = await self.ble.scan()
        return self.devices

    async def connect(self, index):
        self.selected = self.devices[index]
        return await self.ble.connect(
            self.selected["address"],
            self.selected["mode"]
        )

    async def disconnect(self):
        await self.ble.disconnect()

    # ===== FIXED NAMES =====
    async def on(self):
        await self.ble.on()

    async def off(self):
        await self.ble.off()

    async def red(self):
        await self.ble.red()

    async def green(self):
        await self.ble.green()

    async def blue(self):
        await self.ble.blue()