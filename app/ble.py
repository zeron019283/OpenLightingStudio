import asyncio
from bleak import BleakScanner, BleakClient


UUID_L7161 = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_TRIONES = "0000ffd9-0000-1000-8000-00805f9b34fb"


class BLEController:

    def __init__(self):

        self.client = None
        self.write_uuid = None
        self.device = None

    async def scan(self):

        devices = await BleakScanner.discover(timeout=5)

        result = []

        for d in devices:

            name = d.name if d.name else "(Tanpa Nama)"

            if name.startswith("Triones"):

                mode = "TRIONES"

            elif name == "L7161":

                mode = "L7161"

            else:

                mode = "UNKNOWN"

            result.append({
                "name": name,
                "address": d.address,
                "mode": mode
            })

        return result

    async def connect(self, address, mode):

        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass

        self.client = BleakClient(address)

        await self.client.connect()

        if mode == "L7161":
            self.write_uuid = UUID_L7161

        elif mode == "TRIONES":
            self.write_uuid = UUID_TRIONES

        else:
            self.write_uuid = None

        return self.client.is_connected

    async def disconnect(self):

        if self.client:
            await self.client.disconnect()

    async def send(self, data):

        if not self.client:
            return False

        if not self.client.is_connected:
            return False

        await self.client.write_gatt_char(
            self.write_uuid,
            data
        )

        return True

    async def send_hex(self, hex_str):

        data = bytes.fromhex(hex_str.replace(" ", ""))

        return await self.send(data)

    async def on(self):
        return await self.send_hex("55 01 02 01")

    async def off(self):
        return await self.send_hex("55 01 02 00")

    async def red(self):
        return await self.send_hex("55 07 01 FF 00 00")

    async def green(self):
        return await self.send_hex("55 07 01 00 FF 00")

    async def blue(self):
        return await self.send_hex("55 07 01 00 00 FF")