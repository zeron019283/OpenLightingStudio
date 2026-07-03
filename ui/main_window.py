import customtkinter as ctk
import threading
import asyncio
import queue

from app.controller import LightingController


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.controller = LightingController()

        # RGB queue (anti spam)
        self.rgb_queue = queue.Queue()
        self.rgb_running = True
        threading.Thread(target=self.rgb_worker, daemon=True).start()

        self.title("OpenLighting Studio")
        self.geometry("950x700")
        self.minsize(950, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.build_ui()
        self.build_controls()

        # load audio devices
        self.load_audio_devices()

        # MUSIC MODE BUTTON
        self.music_btn = ctk.CTkButton(
            self,
            text="MUSIC MODE",
            command=self.controller.start_music_mode
        )
        self.music_btn.pack(pady=10)

    # =========================
    # RGB WORKER (ANTI LAG)
    # =========================

    def rgb_worker(self):

        while self.rgb_running:

            try:
                r, g, b = self.rgb_queue.get(timeout=0.1)
                asyncio.run(self.controller.set_rgb(r, g, b))
            except queue.Empty:
                continue

    def update_rgb(self, value=None):

        r = int(self.red_slider.get())
        g = int(self.green_slider.get())
        b = int(self.blue_slider.get())

        # flush old queue (biar realtime)
        while not self.rgb_queue.empty():
            try:
                self.rgb_queue.get_nowait()
            except:
                pass

        self.rgb_queue.put((r, g, b))

    # =========================
    # UI BUILD
    # =========================

    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="OpenLighting Studio",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=10)

        self.status_label = ctk.CTkLabel(
            self,
            text="🔴 DISCONNECTED",
            font=("Segoe UI", 16)
        )
        self.status_label.pack()

        # BLE DEVICE
        self.device_combo = ctk.CTkComboBox(
            self,
            values=["Belum Scan"],
            width=300
        )
        self.device_combo.pack(pady=10)

        # AUDIO DEVICE
        self.audio_device_combo = ctk.CTkComboBox(
            self,
            values=["Loading..."],
            width=300
        )
        self.audio_device_combo.pack(pady=5)

        self.audio_refresh_btn = ctk.CTkButton(
            self,
            text="REFRESH AUDIO DEVICES",
            command=self.load_audio_devices
        )
        self.audio_refresh_btn.pack(pady=5)

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
            command=lambda: threading.Thread(
                target=lambda: asyncio.run(self.controller.disconnect()),
                daemon=True
            ).start()
        )
        self.disconnect_btn.grid(row=0, column=2, padx=5)

        self.log = ctk.CTkTextbox(self, width=800, height=300)
        self.log.pack(pady=20)

    # =========================
    # CONTROLS
    # =========================

    def build_controls(self):

        control = ctk.CTkFrame(self)
        control.pack(pady=10)

        self.on_btn = ctk.CTkButton(
            control,
            text="ON",
            command=lambda: threading.Thread(
                target=lambda: asyncio.run(self.controller.on()),
                daemon=True
            ).start()
        )
        self.on_btn.grid(row=0, column=0, padx=5)

        self.off_btn = ctk.CTkButton(
            control,
            text="OFF",
            command=lambda: threading.Thread(
                target=lambda: asyncio.run(self.controller.off()),
                daemon=True
            ).start()
        )
        self.off_btn.grid(row=0, column=1, padx=5)

        # RGB SLIDERS
        self.rgb_frame = ctk.CTkFrame(self)
        self.rgb_frame.pack(pady=10)

        self.red_slider = ctk.CTkSlider(
            self.rgb_frame,
            from_=0,
            to=255,
            command=self.update_rgb
        )
        self.red_slider.grid(row=0, column=0, padx=10)

        self.green_slider = ctk.CTkSlider(
            self.rgb_frame,
            from_=0,
            to=255,
            command=self.update_rgb
        )
        self.green_slider.grid(row=0, column=1, padx=10)

        self.blue_slider = ctk.CTkSlider(
            self.rgb_frame,
            from_=0,
            to=255,
            command=self.update_rgb
        )
        self.blue_slider.grid(row=0, column=2, padx=10)

    # =========================
    # AUDIO DEVICE CONTROL
    # =========================

    def load_audio_devices(self):

        devices = self.controller.get_audio_devices()

        if not devices:
            self.audio_device_combo.configure(values=["No device"])
            return

        self.audio_device_combo.configure(values=devices)
        self.audio_device_combo.set(devices[0])

    def set_audio_device(self):

        selected = self.audio_device_combo.get()
        devices = self.controller.get_audio_devices()

        if selected in devices:
            index = devices.index(selected)
            self.controller.set_audio_device(index)

    # =========================
    # SCAN / CONNECT
    # =========================

    def scan_clicked(self):
        threading.Thread(
            target=lambda: asyncio.run(self.scan()),
            daemon=True
        ).start()

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

    def connect_clicked(self):
        threading.Thread(
            target=lambda: asyncio.run(self.connect()),
            daemon=True
        ).start()

    async def connect(self):

        selected = self.device_combo.get()

        if not selected:
            return

        index = self.device_combo.cget("values").index(selected)

        result = await self.controller.connect(index)

        if result:
            self.status_label.configure(text="🟢 CONNECTED")
            self.log.insert("end", "CONNECTED\n")