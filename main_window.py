# main_window.py
import tkinter as tk
from tkinter import ttk, colorchooser

class MainWindow:
    def __init__(self, root, app_controller):
        self.root = root
        self.app = app_controller
        self.root.title("Studio Pencahayaan Pintar - OpenLightingStudio")
        self.root.geometry("460x520")
        
        # --- KONTROLER TAB UTAMA ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Membuat halaman bingkai (frame) untuk masing-masing tab
        self.tab_connect = ttk.Frame(self.notebook)
        self.tab_visualizer = ttk.Frame(self.notebook)
        self.tab_ambilight = ttk.Frame(self.notebook)
        
        # Daftarkan tab ke menu utama
        self.notebook.add(self.tab_connect, text=" 🔌 Koneksi & Alat ")
        self.notebook.add(self.tab_visualizer, text=" 🎵 Audio Visualizer ")
        self.notebook.add(self.tab_ambilight, text=" 📺 Ambient Light ")
        
        # Panggil fungsi perakit masing-masing tab
        self.setup_tab_connect()
        self.setup_tab_visualizer()
        self.setup_tab_ambilight()

    # --- TAB 1: KONEKSI & PERANGKAT ---
    def setup_tab_connect(self):
        # Frame Bluetooth
        frame_ble = ttk.LabelFrame(self.tab_connect, text=" Pengaturan Lampu Bluetooth ")
        frame_ble.pack(fill="x", padx=10, pady=10, ipady=5)
        
        self.combo_ble = ttk.Combobox(frame_ble, width=48, state="readonly")
        self.combo_ble.pack(pady=5)
        
        btn_frame = tk.Frame(frame_ble)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Scan Devices", command=self.app.gui_scan_ble).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Connect Selected", command=self.app.gui_connect_ble).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_ble, text="Lampu Terhubung Saat Ini:").pack(pady=(10, 0))
        self.list_connected = tk.Listbox(frame_ble, height=3, width=48, selectmode=tk.SINGLE)
        self.list_connected.pack(pady=5)
        
        ttk.Button(frame_ble, text="Disconnect Selected Device", command=self.app.gui_disconnect_ble).pack(pady=2)
        
        self.lbl_status = ttk.Label(frame_ble, text="Status: Belum Ada Lampu Terhubung", foreground="red", font=("Arial", 9, "bold"))
        self.lbl_status.pack(pady=5)

        # Frame Audio Source
        frame_audio = ttk.LabelFrame(self.tab_connect, text=" Sumber Input Suara ")
        frame_audio.pack(fill="x", padx=10, pady=5, ipady=5)
        
        self.combo_audio = ttk.Combobox(frame_audio, width=48, state="readonly")
        self.combo_audio.pack(pady=5)
        ttk.Button(frame_audio, text="Refresh Audio Devices", command=self.app.gui_refresh_audio).pack(pady=2)

    # --- TAB 2: AUDIO VISUALIZER ---
    def setup_tab_visualizer(self):
        frame_vis = ttk.LabelFrame(self.tab_visualizer, text=" Kontrol Sinkronisasi Musik ")
        frame_vis.pack(fill="both", expand=True, padx=10, pady=10, ipady=10)
        
        ttk.Label(frame_vis, text="1. Pilih Warna Dasar Lampu:").pack(pady=(15, 0))
        self.color_btn = tk.Button(frame_vis, text="Buka Palet Warna", command=self.choose_color, bg="#ffffff", width=25, relief=tk.GROOVE)
        self.color_btn.pack(pady=5)

        ttk.Label(frame_vis, text="2. Atur Sensitivitas Hentakan Beat:").pack(pady=(20, 0))
        self.slider_sens = ttk.Scale(frame_vis, from_=1.0, to=100.0, orient='horizontal', length=350)
        self.slider_sens.set(30.0) 
        self.slider_sens.pack(pady=5)

        self.is_visualizer_on = False
        self.btn_on_off = tk.Button(frame_vis, text="START AUDIO VISUALIZER", bg="#28a745", fg="white", 
                                    font=("Arial", 11, "bold"), height=2, command=self.toggle_visualizer)
        self.btn_on_off.pack(side=tk.BOTTOM, fill="x", padx=20, pady=20)

    # --- TAB 3: AMBIENT LIGHT (SUDAH DIPERBAIKI) ---
    def setup_tab_ambilight(self):
        frame_amb = ttk.LabelFrame(self.tab_ambilight, text=" Kontrol Penyelarasan Warna Layar PC ")
        frame_amb.pack(fill="both", expand=True, padx=10, pady=10, ipady=10)
        
        # Perbaikan di sini: wraplength=400 piksel agar memanjang normal
        ttk.Label(frame_amb, text="Kelembutan Transisi Perubahan Warna (Smoothness):", wraplength=400).pack(pady=(20, 0), padx=10)
        
        self.slider_amb_smooth = ttk.Scale(frame_amb, from_=5.0, to=100.0, orient='horizontal', length=350)
        self.slider_amb_smooth.set(25.0) 
        self.slider_amb_smooth.pack(pady=5)
        
        # Perbaikan di sini: wraplength=400 piksel
        ttk.Label(frame_amb, text="Tip: Nilai 20-30% sangat cocok untuk menonton film agar transisinya sinematik dan tidak membuat mata lelah.", 
                  font=("Arial", 8, "italic"), foreground="gray", justify=tk.CENTER, wraplength=400).pack(pady=10, padx=15)

        self.is_ambilight_on = False
        self.btn_ambilight = tk.Button(frame_amb, text="START AMBIENT LIGHT", bg="#007bff", fg="white", 
                                       font=("Arial", 11, "bold"), height=2, command=self.toggle_ambilight)
        self.btn_ambilight.pack(side=tk.BOTTOM, fill="x", padx=20, pady=20)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Pilih Warna LED")
        if color_code[0]:
            r, g, b = [int(x) for x in color_code[0]]
            self.color_btn.config(bg=color_code[1])
            self.app.gui_set_color(r, g, b)

    def toggle_visualizer(self):
        self.is_visualizer_on = not self.is_visualizer_on
        if self.is_visualizer_on:
            self.btn_on_off.config(text="STOP AUDIO VISUALIZER", bg="#dc3545")
            self.app.start_visualizer()
        else:
            self.btn_on_off.config(text="START AUDIO VISUALIZER", bg="#28a745")
            self.app.stop_visualizer()

    def toggle_ambilight(self):
        self.is_ambilight_on = not self.is_ambilight_on
        if self.is_ambilight_on:
            self.btn_ambilight.config(text="STOP AMBIENT LIGHT", bg="#dc3545")
            self.app.start_ambilight()
        else:
            self.btn_ambilight.config(text="START AMBIENT LIGHT", bg="#007bff")
            self.app.stop_ambilight()

    def update_connected_list(self, connected_devices):
        self.list_connected.delete(0, tk.END)
        for mac, data in connected_devices.items():
            self.list_connected.insert(tk.END, f"{data['name']} ({data['type']}) - {mac}")