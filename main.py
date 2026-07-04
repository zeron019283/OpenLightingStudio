# main.py
import tkinter as tk
import asyncio
import threading
import time
import warnings
import soundcard as sc
from PIL import ImageGrab  # Digunakan untuk menangkap gambar layar PC
from main_window import MainWindow
from ble import BluetoothController
from audio import AudioCapture
from music import AudioProcessor
import config

class AppController:
    def __init__(self):
        self.ble = BluetoothController()
        self.audio = AudioCapture()
        self.music = AudioProcessor()
        
        self.visualizer_running = False
        self.ambilight_running = False
        self.r, self.g, self.b = 255, 255, 255
        self.audio_devices = {}
        
        self.root = tk.Tk()
        self.gui = MainWindow(self.root, self)
        
        self.gui_refresh_audio()

    def run_async(self, coroutine):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coroutine)
        threading.Thread(target=run, daemon=True).start()

    def gui_scan_ble(self):
        self.gui.combo_ble['values'] = ["Mencari perangkat (tunggu 5 detik)..."]
        async def scan_task():
            devices = await self.ble.scan_devices()
            self.gui.combo_ble['values'] = devices
            self.gui.combo_ble.set("Klik untuk memilih perangkat...")
        self.run_async(scan_task())

    def gui_connect_ble(self):
        selection = self.gui.combo_ble.get()
        if "(" in selection:
            nama_device = selection.split("(")[0].strip()
            mac_address = selection.split("(")[1].replace(")", "")
            
            if "TRIONES" in nama_device.upper():
                dev_type = "TRIONES"
            else:
                dev_type = "NORDIC"
                
            self.gui.lbl_status.config(text=f"Menghubungkan ke {nama_device}...", foreground="orange")
            
            async def connect_task():
                success = await self.ble.connect(mac_address, device_type=dev_type, device_name=nama_device)
                if success:
                    jumlah = len(self.ble.connected_devices)
                    self.gui.lbl_status.config(text=f"Status: {jumlah} Lampu Berhasil Sinkron!", foreground="green")
                    self.gui.update_connected_list(self.ble.connected_devices)
                    await self.ble.set_rgb_color(self.r, self.g, self.b, 1.0)
                else:
                    self.gui.lbl_status.config(text="Status: Gagal Menghubungkan", foreground="red")
                    
            self.run_async(connect_task())

    def gui_disconnect_ble(self):
        try:
            selected_idx = self.gui.list_connected.curselection()
            if not selected_idx:
                self.gui.lbl_status.config(text="Pilih lampu dari daftar di atas dahulu!", foreground="orange")
                return
            
            selection_text = self.gui.list_connected.get(selected_idx)
            mac_address = selection_text.split("-")[-1].strip()
            
            self.gui.lbl_status.config(text="Memutuskan koneksi lampu...", foreground="orange")
            
            async def disconnect_task():
                success = await self.ble.disconnect(mac_address)
                if success:
                    jumlah = len(self.ble.connected_devices)
                    self.gui.update_connected_list(self.ble.connected_devices)
                    if jumlah > 0:
                        self.gui.lbl_status.config(text=f"Status: {jumlah} Lampu Berhasil Sinkron!", foreground="green")
                    else:
                        self.gui.lbl_status.config(text="Status: Belum Ada Lampu Terhubung", foreground="red")
                else:
                    self.gui.lbl_status.config(text="Gagal memutuskan koneksi", foreground="red")
            self.run_async(disconnect_task())
        except Exception as e:
            print(f"Error Disconnect GUI: {e}")

    def gui_refresh_audio(self):
        self.audio_devices = self.audio.get_audio_devices()
        device_names = list(self.audio_devices.keys())
        self.gui.combo_audio['values'] = device_names
        for name in device_names:
            if "Loopback" in name:
                self.gui.combo_audio.set(name)
                break
        else:
            if device_names: self.gui.combo_audio.set(device_names[0])

    def gui_set_color(self, r, g, b):
        self.r, self.g, self.b = r, g, b
        if self.ble.is_connected and not self.visualizer_running and not self.ambilight_running:
            self.run_async(self.ble.set_rgb_color(r, g, b, 1.0))

    # --- LOGIKA AUDIO VISUALIZER ---
    def start_visualizer(self):
        # Proteksi: Matikan ambilight jika sedang menyala
        if self.ambilight_running:
            self.gui.toggle_ambilight()
            
        selected_audio = self.gui.combo_audio.get()
        if selected_audio in self.audio_devices:
            self.audio.set_device(self.audio_devices[selected_audio])
            
        self.visualizer_running = True
        threading.Thread(target=self.visualizer_loop, daemon=True).start()

    def stop_visualizer(self):
        self.visualizer_running = False
        if self.ble.is_connected:
            self.run_async(self.ble.set_rgb_color(self.r, self.g, self.b, 0.0))

    def visualizer_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        mic = self.audio.mic
        if not mic: return
        warnings.filterwarnings("ignore", category=sc.SoundcardRuntimeWarning)
        try:
            with mic.recorder(samplerate=config.SAMPLE_RATE) as rec:
                last_send_time = time.time()
                while self.visualizer_running and self.ble.is_connected:
                    data = rec.record(numframes=config.CHUNK_SIZE)
                    current_time = time.time()
                    if current_time - last_send_time >= (1.0 / config.MAX_FPS):
                        sensitivity = self.gui.slider_sens.get()
                        brightness = self.music.calculate_brightness(data, sensitivity)
                        loop.run_until_complete(self.ble.set_rgb_color(self.r, self.g, self.b, brightness))
                        last_send_time = current_time
        except Exception as e:
            print(f"Visualizer Error: {e}")

    # --- BARU: LOGIKA AMBIENT LIGHT (SCREEN MIRRORING) ---
    def start_ambilight(self):
        # Proteksi: Matikan visualizer musik jika sedang menyala
        if self.visualizer_running:
            self.gui.toggle_visualizer()
            
        self.ambilight_running = True
        threading.Thread(target=self.ambilight_loop, daemon=True).start()

    def stop_ambilight(self):
        self.ambilight_running = False
        if self.ble.is_connected:
            # Set lampu ke padam saat dimatikan
            self.run_async(self.ble.set_rgb_color(0, 0, 0, 0.0))

    def ambilight_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Menyimpan memori warna terakhir untuk interpolasi kelembutan (Smoothing)
        last_r, last_g, last_b = 0, 0, 0
        
        while self.ambilight_running and self.ble.is_connected:
            start_time = time.time()
            try:
                # 1. Tangkap seluruh layar monitor utama PC
                screenshot = ImageGrab.grab()
                
                # 2. Perkecil ke 1x1 piksel untuk mendapatkan warna rata-rata secara instan
                small_img = screenshot.resize((1, 1))
                r, g, b = small_img.getpixel((0, 0))
                
                # 3. Ambil nilai kelembutan perpindahan warna dari slider GUI (0.05 sampai 1.0)
                smooth_factor = self.gui.slider_amb_smooth.get() / 100.0
                
                # 4. Rumus Linier Interpolasi (LERP) agar warna mengalir mulus tidak patah-patah
                r_final = int(last_r + (r - last_r) * smooth_factor)
                g_final = int(last_g + (g - last_g) * smooth_factor)
                b_final = int(last_b + (b - last_b) * smooth_factor)
                
                # Simpan warna saat ini untuk acuan loop berikutnya
                last_r, last_g, last_b = r_final, g_final, b_final
                
                # 5. Kirim warna ke seluruh lampu (kecerahan diset 1.0 karena warna layar sudah adaptif)
                loop.run_until_complete(self.ble.set_rgb_color(r_final, g_final, b_final, 1.0))
                
            except Exception as e:
                print(f"Ambilight Loop Error: {e}")
            
            # Membatasi FPS penangkapan layar sesuai setelan di config agar CPU tidak boros
            elapsed = time.time() - start_time
            sleep_time = (1.0 / config.MAX_FPS) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def run(self):
        self.root.mainloop()
        if self.ble.is_connected:
            self.run_async(self.ble.set_rgb_color(0, 0, 0, 0.0))
            self.run_async(self.ble.disconnect_all())

if __name__ == "__main__":
    app = AppController()
    app.run()