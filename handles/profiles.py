import time
from selenium.webdriver.common.by import By
from sql import profiles
from stores import store_profiles
from managers import Driver

def create_profile(id):

    profile = profiles.show(id)

    stop_event = store_profiles[id]['stop_event']
    
    # Khởi tạo driver
    driver = Driver(profile=profile)
    start_url = profile.get('start_url')
    if start_url:
        driver.get(start_url)

    store_profiles[id]['check'] = 1
    store_profiles[id]['status'] = 'Đã khởi tạo trình duyệt'
    try:
        while not stop_event.is_set():
            try:
                driver.current_url
            except:
                break
            time.sleep(1)
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")
    finally:
        print('Trình duyệt đã bị đóng')
        driver.quit()
        del store_profiles[id]

def close_profile(id):
    thread = store_profiles[id]['thread']
    thread.join()
    

