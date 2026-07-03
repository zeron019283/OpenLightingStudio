import asyncio
from bleak import BleakScanner, BleakClient


# UUID umum lampu BLE (HiLighting / Triones)
UUID_L7161 = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_TRIONES = "0000ffd9-0000-1000-8000-00805f9b34fb"


class BLEController:

    def __init__(self):

        self.client = None
        self.write_uuid = None
        self.address = None
        self.mode = None

        self.last_rgb = (-1, -1, -1)

    # =========================
    # SCAN DEVICE
    # =========================

    async def scan(self):

        devices = await BleakScanner.discover(timeout=5)

        result = []

        for d in devices:

            name = d.name if d.name else "(Unknown)"

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

    # =========================
    # CONNECT DEVICE
    # =========================

    async def connect(self, address, mode):

        try:

            if self.client and self.client.is_connected:
                await self.client.disconnect()

            self.address = address
            self.mode = mode

            self.client = BleakClient(address)
            await self.client.connect()

            # pilih UUID write
            if mode == "L7161":
                self.write_uuid = UUID_L7161
            else:
                self.write_uuid = UUID_TRIONES

            print("CONNECTED:", address)
            print("MODE:", mode)
            print("WRITE UUID:", self.write_uuid)

            return self.client.is_connected

        except Exception as e:
            print("CONNECT ERROR:", e)
            return False

    # =========================
    # DISCONNECT
    # =========================

    async def disconnect(self):

        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass

        self.client = None
        self.write_uuid = None

    # =========================
    # RAW SEND
    # =========================

    async def send(self, data: bytes):

        if not self.client or not self.client.is_connected:
            return False

        if not self.write_uuid:
            return False

        try:

            print("SEND:", data.hex(" "))

            await self.client.write_gatt_char(self.write_uuid, data)

            return True

        except Exception as e:
            print("SEND ERROR:", e)
            return False

    # =========================
    # ON / OFF (WORKING)
    # =========================

    async def on(self):
        return await self.send(bytes([0x55, 0x01, 0x02, 0x01]))

    async def off(self):
        return await self.send(bytes([0x55, 0x01, 0x02, 0x00]))

    # =========================
    # RGB CONTROL (FIXED PROTOCOL)
    # =========================

    async def set_rgb(self, r, g, b):

        # anti spam
        if (r, g, b) == self.last_rgb:
            return True

        self.last_rgb = (r, g, b)

        if not self.client or not self.client.is_connected:
            return False

        try:

            # HiLighting / Triones RGB protocol
            data = bytes([
                0x56,   # header
                r,
                g,
                b,
                0x00,
                0xF0,
                0xAA
            ])

            print(f"RGB -> R:{r} G:{g} B:{b}")

            await self.client.write_gatt_char(self.write_uuid, data)

            return True

        except Exception as e:
            print("RGB ERROR:", e)
            return False

    # =========================
    # BRIGHTNESS CONTROL (NEW)
    # =========================

    async def set_brightness(self, value: int):

        if not self.client or not self.client.is_connected:
            return False

        try:

            value = max(0, min(100, value))
            v = int(value * 255 / 100)

            # brightness command (common Triones format)
            data = bytes([
                0x56,
                0x00,
                0x00,
                0x00,
                v,
                0xF0,
                0xAA
            ])

            print("BRIGHTNESS:", value)

            await self.client.write_gatt_char(self.write_uuid, data)

            return True

        except Exception as e:
            print("BRIGHTNESS ERROR:", e)
            return False

    # =========================
    # SIMPLE COLORS
    # =========================

    async def red(self):
        return await self.set_rgb(255, 0, 0)

    async def green(self):
        return await self.set_rgb(0, 255, 0)

    async def blue(self):
        return await self.set_rgb(0, 0, 255)