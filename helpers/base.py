import json

def dd(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))

def load_file(path):
    file_content = ''
    with open(path, 'r') as file:
        file_content = file.read() 
    return file_content

def config(key = None, defaultValue = None):
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