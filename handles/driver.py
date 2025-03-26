import os
import threading
import json
from time import sleep
from helpers import config
from webdriver_manager.chrome import ChromeDriverManager
from stores import isDownloadDriver

def timer_thread():
    global isDownloadDriver
    while isDownloadDriver['status']:
        sleep(1)
        isDownloadDriver['time'] += 1
        print(f"\u23f3 Thời gian tải: {isDownloadDriver['time']} giây")

def download_driver():
    global isDownloadDriver

    custom_path = config('temps')['driver']

    isDownloadDriver['status'] = True
    print("\U0001f680 Bắt đầu tải ChromeDriver...")

    timer = threading.Thread(target=timer_thread, daemon=True)
    timer.start()

    try:
        driver_path = ChromeDriverManager().install()
        print(f"✅ Tải thành công! Lưu tại: {driver_path}")

        # 📝 Cập nhật config.json
        current_config = config()
        
        current_config["driver"]["driver_path"] = driver_path
        with open("config.json", "w") as config_file:
            json.dump(current_config, config_file, indent=4)

    except Exception as e:
        print(f"❌ Lỗi khi tải driver: {e}")

    finally:
        # Kết thúc tiến trình
        isDownloadDriver['status'] = False
        isDownloadDriver['time'] = 0
        print("🛑 Hoàn tất tải.")