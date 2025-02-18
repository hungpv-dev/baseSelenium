import webview
from threading import Thread
from server import create_app, start_app

app = create_app()


if __name__ == '__main__':
    server_thread = Thread(target=start_app,args=(app,))
    server_thread.daemon = True
    server_thread.start()

    webview.create_window('Asfy Tech', 'http://127.0.0.1:5000', maximized=True)
    webview.start()