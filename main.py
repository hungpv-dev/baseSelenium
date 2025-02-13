import webview
from threading import Thread
from routes.index import app

def start_server():
    # Kích hoạt chế độ debug và tắt reloader
    app.run(debug=True, use_reloader=False)

# Khởi động Flask server trong một luồng riêng
server_thread = Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Tạo cửa sổ ứng dụng với nội dung HTML từ Flask
webview.create_window('Asfy Tech', 'http://127.0.0.1:5000')

# Chạy ứng dụng webview
webview.start()