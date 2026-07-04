# ble.py
import asyncio
from bleak import BleakClient, BleakScanner
import config

class BluetoothController:
    def __init__(self):
        # Menyimpan semua perangkat terhubung: {"MAC_ADDRESS": {"client": BleakClient, "type": "...", "name": "..."}}
        self.connected_devices = {}

    @property
    def is_connected(self):
        return len(self.connected_devices) > 0

    async def scan_devices(self):
        print("Mencari perangkat bluetooth di sekitar...")
        devices = await BleakScanner.discover(timeout=5.0)
        return [f"{d.name or 'Unknown'} ({d.address})" for d in devices]

    async def connect(self, mac_address, device_type="NORDIC", device_name="Unknown"):
        client = BleakClient(mac_address)
        try:
            print(f"Mencoba menghubungkan ke {mac_address} ({device_type})...")
            await client.connect()
            
            # Simpan detail perangkat termasuk namanya
            self.connected_devices[mac_address] = {
                "client": client,
                "type": device_type,
                "name": device_name
            }
            print(f"Berhasil terhubung ke {mac_address}!")
            return True
        except Exception as e:
            print(f"Gagal terhubung ke {mac_address}: {e}")
            return False

    async def disconnect(self, mac_address):
        """Memutuskan satu perangkat tertentu"""
        if mac_address in self.connected_devices:
            try:
                await self.connected_devices[mac_address]["client"].disconnect()
                print(f"Terputus dari {mac_address}.")
            except Exception as e:
                print(f"Gagal memutus {mac_address}: {e}")
            
            del self.connected_devices[mac_address]
            return True
        return False

    async def disconnect_all(self):
        for mac, data in self.connected_devices.items():
            try:
                await data["client"].disconnect()
                print(f"Terputus dari {mac}.")
            except Exception as e:
                print(f"Gagal memutus {mac}: {e}")
        self.connected_devices.clear()

    async def set_rgb_color(self, r, g, b, brightness=1.0):
        if not self.is_connected:
            return

        brightness = max(0.0, min(1.0, float(brightness)))
        r_final = int(max(0, min(255, r * brightness)))
        g_final = int(max(0, min(255, g * brightness)))
        b_final = int(max(0, min(255, b * brightness)))

        tasks = []

        for mac, data in self.connected_devices.items():
            client = data["client"]
            dev_type = data["type"]

            if dev_type == "NORDIC":
                uuid = config.BLE_WRITE_UUID
                packet = bytearray([0x55, 0x07, 0x01, r_final, g_final, b_final])
            elif dev_type == "TRIONES":
                uuid = "0000ffd9-0000-1000-8000-00805f9b34fb"
                packet = bytearray([0x56, r_final, g_final, b_final, 0x00, 0xF0, 0xAA])
            else:
                continue

            tasks.append(client.write_gatt_char(uuid, packet, response=False))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)