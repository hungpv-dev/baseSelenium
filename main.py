import webview
from threading import Thread
import traceback
import sys
from server import *

def log_exceptions(exc_type, exc_value, exc_traceback):
    with open("error.log", "a", encoding="utf-8") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

sys.excepthook = log_exceptions

app = create_app()


if __name__ == '__main__':
    port = 8000

    if is_port_in_use(port):
        kill_existing_process(port)  # Đóng tiến trình cũ trên cổng 8000
        port = find_free_port(port)  # Tìm cổng trống mới

    # start_app(app, port=port)
    server_thread = Thread(target=start_app, args=(app, False, port))
    server_thread.daemon = True
    server_thread.start()

    webview.create_window('Asfy Tech', 'http://127.0.0.1:5000', maximized=True)
    webview.start()