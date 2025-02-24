from flask import Blueprint, jsonify
from handles import download_driver
from stores import isDownloadDriver
import threading

drivers = Blueprint('drivers',__name__)

@drivers.route('/')

@drivers.route('/check-status-download-driver')
def checkStatusDownloadDriver():
    global isDownloadDriver
    return jsonify({
        'is_download': isDownloadDriver
    })

@drivers.route('/download-driver', methods=['POST'])
def downloadDriver():
    global isDownloadDriver
    
    if isDownloadDriver.get('status'):
        return jsonify({'message': 'Tiến trình tải đã chạy trước đó!'}), 400
    
    isDownloadDriver['status'] = True
    isDownloadDriver['time'] = 1

    # Tạo và chạy thread
    thread = threading.Thread(target=download_driver, daemon=True)
    thread.start()

    return jsonify({
        'message': 'Đang bắt đầu tiến trình tải',
    })
