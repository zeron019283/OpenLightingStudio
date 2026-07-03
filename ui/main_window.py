import customtkinter as ctk
import threading
import asyncio

from app.controller import LightingController


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.controller = LightingController()

        self.title("OpenLighting Studio")
        self.geometry("950x700")
        self.minsize(950, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # BUILD UI
        self.build_ui()
        self.build_controls()

    # =========================
    # UI
    # =========================
    def build_ui(self):

        # TITLE
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

        # DEVICE COMBO
        self.device_combo = ctk.CTkComboBox(
            self,
            values=["Belum Scan"],
            width=300
        )
        self.device_combo.pack(pady=10)

        # TOP BUTTON FRAME
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

        # LOG BOX
        self.log = ctk.CTkTextbox(
            self,
            width=800,
            height=400
        )
        self.log.pack(pady=20)

    # =========================
    # CONTROL BUTTONS
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

        self.log.insert("end", "Scanning Bluetooth...\n")

        devices = await self.controller.scan()

        names = []

        for d in devices:
            line = f'{d["name"]} | {d["address"]} ({d["mode"]})'
            names.append(f'{d["name"]} ({d["mode"]})')
            self.log.insert("end", line + "\n")

        if names:
            self.device_combo.configure(values=names)
            self.device_combo.set(names[0])

        self.log.insert("end", "\nSCAN SELESAI\n")

    # =========================
    # CONNECT
    # =========================
    def connect_clicked(self):
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        asyncio.run(self.connect())

    async def connect(self):

        try:
            self.log.insert("end", "Connecting...\n")

            selected = self.device_combo.get()

            if not selected or selected == "Belum Scan":
                self.log.insert("end", "No device selected!\n")
                return

            index = self.device_combo.cget("values").index(selected)

            result = await self.controller.connect(index)

            if result:
                self.log.insert("end", "CONNECTED SUCCESS\n")
                self.status_ok()
            else:
                self.log.insert("end", "CONNECT FAILED\n")

        except Exception as e:
            self.log.insert("end", f"ERROR: {e}\n")