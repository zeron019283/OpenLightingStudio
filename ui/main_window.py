import customtkinter as ctk
import threading
import asyncio
import queue

from app.controller import LightingController


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.controller = LightingController()

        # RGB queue (manual slider / fallback system)
        self.rgb_queue = queue.Queue()
        self.running = True

        threading.Thread(target=self.rgb_worker, daemon=True).start()

        self.title("OpenLighting Studio")
        self.geometry("950x700")
        self.minsize(950, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.build_ui()

        # auto load devices
        self.load_audio_devices()
        self.load_mics()

    # =========================
    # RGB WORKER THREAD
    # =========================

    def rgb_worker(self):

        while self.running:

            try:
                r, g, b = self.rgb_queue.get(timeout=0.1)
                asyncio.run(self.controller.set_rgb(r, g, b))

            except queue.Empty:
                continue

    # =========================
    # RGB SLIDER UPDATE
    # =========================

    def update_rgb(self, value=None):

        r = int(self.red_slider.get())
        g = int(self.green_slider.get())
        b = int(self.blue_slider.get())

        # clear old queue (anti lag)
        while not self.rgb_queue.empty():
            try:
                self.rgb_queue.get_nowait()
            except:
                pass

        self.rgb_queue.put((r, g, b))

    # =========================
    # BRIGHTNESS UPDATE (NEW)
    # =========================

    def update_brightness(self, value=None):

        v = int(self.brightness_slider.get())

        threading.Thread(
            target=lambda: asyncio.run(
                self.controller.set_brightness(v)
            ),
            daemon=True
        ).start()

    # =========================
    # UI BUILD
    # =========================

    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="OpenLighting Studio",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=10)

        # STATUS
        self.status_label = ctk.CTkLabel(
            self,
            text="🔴 DISCONNECTED",
            font=("Segoe UI", 16)
        )
        self.status_label.pack()

        # =========================
        # BLE DEVICE LIST
        # =========================

        self.device_combo = ctk.CTkComboBox(
            self,
            values=["Belum Scan"],
            width=300
        )
        self.device_combo.pack(pady=10)

        # =========================
        # AUDIO OUTPUT (optional)
        # =========================

        self.audio_device_combo = ctk.CTkComboBox(
            self,
            values=["Loading audio..."],
            width=300
        )
        self.audio_device_combo.pack(pady=5)

        # =========================
        # MICROPHONE
        # =========================

        self.mic_combo = ctk.CTkComboBox(
            self,
            values=["Loading mic..."],
            width=300
        )
        self.mic_combo.pack(pady=5)

        self.mic_btn = ctk.CTkButton(
            self,
            text="APPLY MIC",
            command=self.apply_mic
        )
        self.mic_btn.pack(pady=5)

        # =========================
        # CONTROL BUTTONS
        # =========================

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10)

        self.scan_btn = ctk.CTkButton(
            frame,
            text="SCAN",
            command=self.scan_clicked
        )
        self.scan_btn.grid(row=0, column=0, padx=5)

        self.connect_btn = ctk.CTkButton(
            frame,
            text="CONNECT",
            command=self.connect_clicked
        )
        self.connect_btn.grid(row=0, column=1, padx=5)

        self.disconnect_btn = ctk.CTkButton(
            frame,
            text="DISCONNECT",
            command=self.disconnect_clicked
        )
        self.disconnect_btn.grid(row=0, column=2, padx=5)

        # =========================
        # RGB SLIDERS
        # =========================

        self.red_slider = ctk.CTkSlider(self, from_=0, to=255, command=self.update_rgb)
        self.red_slider.set(0)
        self.red_slider.pack()

        self.green_slider = ctk.CTkSlider(self, from_=0, to=255, command=self.update_rgb)
        self.green_slider.set(0)
        self.green_slider.pack()

        self.blue_slider = ctk.CTkSlider(self, from_=0, to=255, command=self.update_rgb)
        self.blue_slider.set(0)
        self.blue_slider.pack()

        # =========================
        # BRIGHTNESS SLIDER (NEW FEATURE)
        # =========================

        self.brightness_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=100,
            command=self.update_brightness
        )
        self.brightness_slider.set(50)
        self.brightness_slider.pack(pady=10)

        ctk.CTkLabel(self, text="Brightness").pack()

        # =========================
        # MUSIC MODE
        # =========================

        self.music_btn = ctk.CTkButton(
            self,
            text="MUSIC MODE",
            command=self.controller.start_music_mode
        )
        self.music_btn.pack(pady=10)

        # =========================
        # LOG
        # =========================

        self.log = ctk.CTkTextbox(self, width=800, height=200)
        self.log.pack(pady=10)

    # =========================
    # MIC APPLY
    # =========================

    def apply_mic(self):

        selected = self.mic_combo.get()
        mics = self.controller.get_microphones()

        if selected in mics:
            index = mics.index(selected)
            self.controller.set_microphone(index)
            self.log.insert("end", f"Mic selected: {selected}\n")

    # =========================
    # LOAD MIC
    # =========================

    def load_mics(self):

        mics = self.controller.get_microphones()

        if not mics:
            self.mic_combo.configure(values=["No mic found"])
            return

        self.mic_combo.configure(values=mics)
        self.mic_combo.set(mics[0])

    # =========================
    # LOAD AUDIO OUTPUT
    # =========================

    def load_audio_devices(self):

        devices = self.controller.get_audio_devices()

        if not devices:
            self.audio_device_combo.configure(values=["No audio device"])
            return

        self.audio_device_combo.configure(values=devices)
        self.audio_device_combo.set(devices[0])

    # =========================
    # SCAN
    # =========================

    def scan_clicked(self):
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        asyncio.run(self.scan())

    async def scan(self):

        self.log.insert("end", "Scanning...\n")

        devices = await self.controller.scan()

        names = []

        for d in devices:
            line = f'{d["name"]} | {d["address"]} ({d["mode"]})'
            names.append(f'{d["name"]} ({d["mode"]})')
            self.log.insert("end", line + "\n")

        if names:
            self.device_combo.configure(values=names)
            self.device_combo.set(names[0])

    # =========================
    # CONNECT
    # =========================

    def connect_clicked(self):
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        asyncio.run(self.connect())

    async def connect(self):

        selected = self.device_combo.get()

        if not selected:
            return

        index = self.device_combo.cget("values").index(selected)

        result = await self.controller.connect(index)

        if result:
            self.status_label.configure(text="🟢 CONNECTED")
            self.log.insert("end", "CONNECTED\n")

    # =========================
    # DISCONNECT
    # =========================

    def disconnect_clicked(self):
        threading.Thread(
            target=lambda: asyncio.run(self.controller.disconnect()),
            daemon=True
        ).start()