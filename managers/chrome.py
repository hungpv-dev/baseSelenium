from seleniumbase import Driver
from helpers import config
import random
import os
import socket

def create_chrome(profile):
    # Thiết lập chế độ headless
    headless_mode = config('driver')['headless'] == "true"

    # Cấu hình User-Agent
    user_agent = profile.get('user_agent', None) if profile else None

    # Cấu hình thư mục Profile
    user_data_dir = None

    if profile:
        user_dir = profile.get('user_dir')  
        if user_dir:
            user_data_dir = os.path.abspath(user_dir)

    # Cấu hình Proxy (Nếu có)
    proxy_config = None
    if profile:
        proxy = profile.get('proxy')
        if proxy and isinstance(proxy, dict) and proxy.get('host') and proxy.get('port'):
            proxy_host = proxy['host']
            proxy_port = proxy['port']
            username = proxy.get('user')
            password = proxy.get('pass')
            if username and password:
                proxy_config = f"{username}:{password}@{proxy_host}:{proxy_port}"
            else:
                proxy_config = f"{proxy_host}:{proxy_port}"

    # Khởi tạo trình duyệt với SeleniumBase
    driver = Driver(
        uc=True,  # Bật chế độ chống phát hiện bot (UnDetectable)
        headless=headless_mode,  # Chế độ Headless
        incognito=False,  # Không mở trình duyệt ẩn danh
        browser="chrome",  # Trình duyệt Chrome
        proxy=proxy_config,  # Proxy dạng "IP:PORT" (nếu không có username/password)
        window_size="1920,1080",
        undetectable=True,
        disable_csp=True,  # Bỏ qua Content Security Policy
        enable_ws=True,  # Bật Web Security
        no_sandbox=True,  # Chạy trình duyệt mà không cần sandbox (tránh hạn chế)
        disable_gpu=True,  # Tắt GPU tăng tính ổn định
        do_not_track=True,
        user_data_dir=user_data_dir,  # Hồ sơ Chrome có thể copy
        # agent=user_agent,  # User-Agent
    )

    return driver

def get_available_port(start=9223, end=9999):
    while True:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
