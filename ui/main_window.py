import customtkinter as ctk
import threading
import asyncio
import time
import queue

from app.controller import LightingController


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.controller = LightingController()
        self.last_send = 0

        # ===== RGB QUEUE SYSTEM (FIX SLIDER) =====
        self.rgb_queue = queue.Queue()
        self.rgb_worker_running = True
        threading.Thread(target=self.rgb_worker, daemon=True).start()

        self.title("OpenLighting Studio")
        self.geometry("950x700")
        self.minsize(950, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.build_ui()
        self.build_controls()

        self.music_btn = ctk.CTkButton(
            self,
            text="MUSIC MODE",
            command=self.controller.start_music_mode
        )
        self.music_btn.pack(pady=10)

        # ===== RGB SLIDERS =====
        self.rgb_frame = ctk.CTkFrame(self)
        self.rgb_frame.pack(pady=10)

        # RED
        self.red_slider = ctk.CTkSlider(
            self.rgb_frame,
            from_=0,
            to=255,
            command=self.update_rgb
        )
        self.red_slider.grid(row=0, column=0, padx=10)
        self.red_slider.set(0)
        ctk.CTkLabel(self.rgb_frame, text="R").grid(row=1, column=0)

        # GREEN
        self.green_slider = ctk.CTkSlider(
            self.rgb_frame,
            from_=0,
            to=255,
            command=self.update_rgb
        )
        self.green_slider.grid(row=0, column=1, padx=10)
        self.green_slider.set(0)
        ctk.CTkLabel(self.rgb_frame, text="G").grid(row=1, column=1)

        # BLUE
        self.blue_slider = ctk.CTkSlider(
            self.rgb_frame,
            from_=0,
            to=255,
            command=self.update_rgb
        )
        self.blue_slider.grid(row=0, column=2, padx=10)
        self.blue_slider.set(0)
        ctk.CTkLabel(self.rgb_frame, text="B").grid(row=1, column=2)

    # =========================
    # RGB WORKER (FIX INTI)
    # =========================
    def rgb_worker(self):
        while self.rgb_worker_running:
            try:
                r, g, b = self.rgb_queue.get(timeout=0.1)
                asyncio.run(self.controller.set_rgb(r, g, b))
            except queue.Empty:
                continue

    # =========================
    # SAFE LOG (THREAD SAFE)
    # =========================
    def safe_log(self, text: str):
        self.log.after(0, lambda: self.log.insert("end", text + "\n"))

    # =========================
    # UI
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

        self.device_combo = ctk.CTkComboBox(
            self,
            values=["Belum Scan"],
            width=300
        )
        self.device_combo.pack(pady=10)

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
            text="DISCONNECT"
        )
        self.disconnect_btn.grid(row=0, column=2, padx=5)

        self.log = ctk.CTkTextbox(self, width=800, height=400)
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
            command=lambda: threading.Thread(target=self._on_thread, daemon=True).start()
        )
        self.on_btn.grid(row=0, column=0, padx=5)

        self.off_btn = ctk.CTkButton(
            control,
            text="OFF",
            command=lambda: threading.Thread(target=self._off_thread, daemon=True).start()
        )
        self.off_btn.grid(row=0, column=1, padx=5)

        self.red_btn = ctk.CTkButton(
            control,
            text="RED",
            command=lambda: threading.Thread(target=self._red_thread, daemon=True).start()
        )
        self.red_btn.grid(row=1, column=0, padx=5)

        self.green_btn = ctk.CTkButton(
            control,
            text="GREEN",
            command=lambda: threading.Thread(target=self._green_thread, daemon=True).start()
        )
        self.green_btn.grid(row=1, column=1, padx=5)

        self.blue_btn = ctk.CTkButton(
            control,
            text="BLUE",
            command=lambda: threading.Thread(target=self._blue_thread, daemon=True).start()
        )
        self.blue_btn.grid(row=1, column=2, padx=5)

    # =========================
    # SLIDER FIX (INI YANG PENTING)
    # =========================
    def update_rgb(self, value=None):

        r = int(self.red_slider.get())
        g = int(self.green_slider.get())
        b = int(self.blue_slider.get())

        # buang queue lama (biar cuma latest value yang dikirim)
        while not self.rgb_queue.empty():
            try:
                self.rgb_queue.get_nowait()
            except:
                break

        self.rgb_queue.put((r, g, b))

    # =========================
    # THREAD WRAPPERS
    # =========================
    def _on_thread(self): asyncio.run(self.controller.on())
    def _off_thread(self): asyncio.run(self.controller.off())
    def _red_thread(self): asyncio.run(self.controller.red())
    def _green_thread(self): asyncio.run(self.controller.green())
    def _blue_thread(self): asyncio.run(self.controller.blue())

    # =========================
    # STATUS
    # =========================
    def status_ok(self):
        self.status_label.configure(text="🟢 CONNECTED")

    # =========================
    # SCAN
    # =========================
    def scan_clicked(self):
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        asyncio.run(self.scan())

    async def scan(self):

        self.safe_log("Scanning Bluetooth...")

        devices = await self.controller.scan()

        names = []

        for d in devices:
            self.safe_log(f'{d["name"]} | {d["address"]} ({d["mode"]})')
            names.append(f'{d["name"]} ({d["mode"]})')

        if names:
            self.device_combo.configure(values=names)
            self.device_combo.set(names[0])

        self.safe_log("SCAN SELESAI")

    # =========================
    # CONNECT
    # =========================
    def connect_clicked(self):
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        asyncio.run(self.connect())

    async def connect(self):

        try:
            self.safe_log("Connecting...")

            selected = self.device_combo.get()

            if not selected or selected == "Belum Scan":
                self.safe_log("No device selected!")
                return

            index = self.device_combo.cget("values").index(selected)

            result = await self.controller.connect(index)

            if result:
                self.safe_log("CONNECTED SUCCESS")
                self.status_ok()
            else:
                self.safe_log("CONNECT FAILED")

        except Exception as e:
            self.safe_log(f"ERROR: {e}")