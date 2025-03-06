import subprocess
import sys
import os

def build_app():
    # Đường dẫn đến file script chính của bạn
    script_path = "main.py"

    app_name = "asfy"

    # Đường dẫn đến file icon (nếu có)
    icon_path = "logo.ico"

    # Danh sách các file hoặc thư mục cần thêm vào build
    datas = [
        ('static', 'static'),  # Thêm thư mục static
        ('templates', 'templates'),  # Thêm thư mục templates
    ]

    # Đường dẫn đến thư mục cài đặt seleniumbase
    seleniumbase_path = "C:\\Users\\Admin\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python311\\site-packages\\seleniumbase"

    # Tạo lệnh PyInstaller để build ứng dụng
    command = [
        "pyinstaller",
        f"--name={app_name}",  # Đặt tên ứng dụng
        # "--noconsole", # Không hiển thị cửa sổ console
        "--onefile",  # Build thành một file thực thi duy nhất
        f"--icon={icon_path}",  # Thêm icon vào file thực thi
        f"--add-data={seleniumbase_path}{os.pathsep}seleniumbase",  # Thêm SeleniumBase
    ]

    # Thêm các tùy chọn --add-data
    for src, dst in datas:
        command.append(f"--add-data={src}{os.pathsep}{dst}")

    # Thêm file script chính vào lệnh
    command.append(script_path)

    # Chạy lệnh build
    try:
        print("Starting build process...")
        subprocess.run(command, check=True)
        print("Build completed successfully! Check the 'dist' folder for the output.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_app()
