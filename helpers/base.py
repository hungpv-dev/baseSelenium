import json

def dd(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))

def load_file(path):
    file_content = ''
    with open(path, 'r') as file:
        file_content = file.read() 
    return file_content

def config(key = None, defaultValue = None, set = None):
    settings = {}
    try:
        with open('config.json', 'r') as config_file:
            settings = json.load(config_file)
    except FileNotFoundError as e:
        print(f'File setting không tồn tại: {e}')
        with open('config.json', 'w') as config_file:
            settings = {
                "headless": False,
                "browser": "chrome",
                "driver_path": "" 
            }
            json.dump(settings,config_file, indent=4)
    except Exception as e:
        print(f'Lỗi khi đọc file setting: {e}')

    if key is None:
        return settings
    
    return settings.get(key) if key in settings else defaultValue

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