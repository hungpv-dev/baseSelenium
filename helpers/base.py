import json

def dd(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))

def load_file(path):
    file_content = ''
    with open(path, 'r') as file:
        file_content = file.read() 
    return file_content

import os
def config(key=None, defaultValue=None):
    config_path = './config.json'
    
    # Nếu file không tồn tại, tạo file với dữ liệu mặc định
    if not os.path.exists(config_path):
        print('File setting khong ton tai, tao file moi...')
        settings = {
            "driver": {
                "browser": "chrome",
                "headless": "false",
                "driver_path": "C:\\Users\\Admin\\.wdm\\drivers\\chromedriver\\win64\\133.0.6943.141\\chromedriver-win32/chromedriver.exe",
                "omocaptcha_token": "OMO_YPTPQ1NI1ECAKCDU0XEKQIGXS4ZAYIAKDKT4MPGKQOGGT3KGFZMZO7XYHL1CDU1738834769",
                "chat_telegram_id": "-1002493389024"
            },
            "temps": {
                "profiles": "./tmp/profiles",
                "driver": "./tmp/drivers"
            }
        }
        with open(config_path, 'w', encoding='utf-8') as config_file:
            json.dump(settings, config_file, indent=4, ensure_ascii=False)
    else:
        # Đọc file nếu đã tồn tại
        try:
            with open(config_path, 'r', encoding='utf-8') as config_file:
                settings = json.load(config_file)
        except Exception as e:
            print(f'Loi khi doc file file setting: {e}')
            return defaultValue  # Trả về giá trị mặc định nếu có lỗi
    
    return settings if key is None else settings.get(key, defaultValue)


def save_config(key, value):
    settings = config()
    settings[key] = value
    with open('config.json', 'w') as config_file:
        json.dump(settings, config_file, indent=4)

import re
def convert_shorthand_to_number(value):
    """Chuyển đổi các giá trị dạng '4.2K', '1.1M' thành số nguyên. Nếu lỗi, trả về 0."""
    if not value or not isinstance(value, str):  # Kiểm tra giá trị rỗng hoặc không phải chuỗi
        return 0

    value = value.strip()  # Loại bỏ khoảng trắng thừa
    
    suffixes = {
        "K": 10**3,
        "M": 10**6,
        "B": 10**9,
    }

    match = re.search(r"([\d,.]+)([KMB]?)", value, re.IGNORECASE)
    if match:
        num, suffix = match.groups()
        num = num.replace(",", "")  # Xóa dấu phẩy nếu có (vd: '1,2K' -> '12K')
        
        try:
            num = float(num)
            multiplier = suffixes.get(suffix.upper(), 1)
            return int(num * multiplier)
        except ValueError:
            return 0  # Trường hợp lỗi khi chuyển đổi số
    
    return 0  # Nếu không khớp với pattern, trả về 0