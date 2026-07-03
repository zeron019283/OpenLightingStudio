import asyncio
from bleak import BleakScanner, BleakClient


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
    # SCAN
    # =========================
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

    # =========================
    # CONNECT
    # =========================
    async def connect(self, address, mode):

        try:
            if self.client and self.client.is_connected:
                await self.client.disconnect()

            self.address = address
            self.mode = mode

            self.client = BleakClient(address)
            await self.client.connect()

            if mode == "L7161":
                self.write_uuid = UUID_L7161
            elif mode == "TRIONES":
                self.write_uuid = UUID_TRIONES
            else:
                self.write_uuid = None

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
    # SEND RAW
    # =========================
    async def send(self, data):

        if not self.client or not self.client.is_connected:
            return False

        if not self.write_uuid:
            return False

        try:
            await self.client.write_gatt_char(self.write_uuid, data)
            return True

        except Exception as e:
            print("SEND ERROR:", e)
            return False

    # =========================
    # SEND HEX
    # =========================
    async def send_hex(self, hex_str):

        data = bytes.fromhex(hex_str.replace(" ", ""))
        return await self.send(data)

    # =========================
    # BASIC COMMANDS
    # =========================
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

    # =========================
    # RGB (FIX UTAMA SLIDER)
    # =========================
    async def set_rgb(self, r, g, b):

        # anti spam (kalau value sama jangan kirim)
        if (r, g, b) == self.last_rgb:
            return True

        self.last_rgb = (r, g, b)

        if not self.client or not self.client.is_connected:
            return False

        if not self.write_uuid:
            return False

        try:
            data = bytes([r, g, b])
            await self.client.write_gatt_char(self.write_uuid, data)
            return True

        except Exception as e:
            print("RGB ERROR:", e)
            return False