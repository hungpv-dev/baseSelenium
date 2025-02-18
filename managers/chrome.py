import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from helpers import config, create_extension_with_proxy

def create_chrome(proxy=None):
    options = Options()
    service = Service(config('driver_path'))

    # Chạy ở chế độ headless nếu cần
    if config('headless'):
        options.add_argument('--headless=new')

    # Cấu hình proxy nếu có
    if proxy:
        extension_proxy = create_extension_with_proxy(proxy)
        options.add_extension(extension_proxy)

    # Cấu hình cache
    cache_dir = os.path.abspath(config('cache_path', './tmp/chrome-cache'))
    options.add_argument(f'--disk-cache-dir={cache_dir}')
    options.add_argument(f'--user-data-dir={cache_dir}/user-data')

    # Chống phát hiện Selenium
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

   
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")  # Mở full màn hình

    # Khởi tạo driver
    driver = uc.Chrome(service=service, options=options, use_subprocess=True)

    # Chống phát hiện webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("""
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    """)

    return driver
