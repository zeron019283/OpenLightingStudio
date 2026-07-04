# config.py

# Konstanta Bluetooth (Nordic UART Service)
BLE_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
BLE_WRITE_UUID   = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
BLE_NOTIFY_UUID  = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Pengaturan Sistem
MAX_FPS = 15  # Kecepatan maksimal pengiriman data ke bluetooth (jangan terlalu tinggi)
SAMPLE_RATE = 44100  # Standar kualitas audio
CHUNK_SIZE = 1024  # Ukuran sampel audio yang diambil per frame