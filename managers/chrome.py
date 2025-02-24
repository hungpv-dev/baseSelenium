import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from helpers import create_extension_with_proxy, config
import random
import os
import socket

def create_chrome(profile, undetected=False, debug_port=None):
    options = uc.ChromeOptions() if undetected else Options()
    execute_path = config('driver')['driver_path']

    # Cấu hình cache
    if profile:
        user_dir = os.path.abspath(profile.get('user_dir'))
        options.add_argument(f'--user-data-dir={user_dir}')
        options.add_argument(f'--disk-cache-dir={user_dir}/cache')

        if profile.get('proxy') and profile.get('proxy') != 'no':
            extension_proxy = create_extension_with_proxy(user_dir, profile.get('proxy'))
            if os.path.exists(extension_proxy):
                full_path_extension = os.path.abspath(extension_proxy)
                options.add_argument(f'--load-extension={full_path_extension}')
    
    # Cấu hình user-agent
    default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    user_agent = profile.get('user_agent', default_user_agent) if profile else default_user_agent
    options.add_argument(f"--user-agent={user_agent}")
    
    # Các tùy chọn khác
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Xác định remote debugging port
    if not debug_port:
        debug_port = get_available_port()
    options.add_argument(f"--remote-debugging-port={debug_port}")
    
    # Khởi tạo driver
    if undetected:
        driver = uc.Chrome(
            execute_path=execute_path,
            options=options,
            use_subprocess=True
        )
    else:
        print('Start')
        driver = webdriver.Chrome(service=Service(executable_path=execute_path), options=options)
    
    # Chống phát hiện Selenium
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("""
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    """)
    
    return driver

def get_available_port(start=9223, end=9999):
    while True:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port