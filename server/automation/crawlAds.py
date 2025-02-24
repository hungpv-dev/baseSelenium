from flask import Blueprint, jsonify, request
from helpers import config
from handles import start_crawl_up, stop_crawl_up
from stores import crawl_ads as crawl_adsStore
import threading
from sql import profiles
import os

crawl_ads = Blueprint('crawl_ads', __name__)

@crawl_ads.route('/')
def list():
    data = {}
    for ix, item in crawl_adsStore.items():
        data[str(ix)] = {
            "check": item["check"],
            "status": item["status"],
            "status_process": item["status_process"],
        }
    return jsonify(data)

@crawl_ads.route('start/<string:id>', methods=['POST'])
def start(id):
    profile = profiles.show(id)
    if not profile:
        return jsonify({
            'message': 'Profile không tồn tại',
        }), 404

    start_profile_thread(str(id))

    return jsonify({
        'message': 'Đang khởi tạo trình duyệt',
    })

@crawl_ads.route('stop/<string:id>', methods=['POST'])
def stop(id):
    print(id, crawl_adsStore)
    if id not in crawl_adsStore:
        return jsonify({
            'message': 'Profile không tồn tại',
        }), 404

    crawl_adsStore[id]['check'] = 2
    crawl_adsStore[id]['status_process'] = 2
    crawl_adsStore[id]['stop_event'].set()
    crawl_adsStore[id]['status'] = 'Trình duyệt đang bị dừng'

    thread = threading.Thread(target=stop_crawl_up, args=(id,))
    thread.start()

    return jsonify({
        'message': 'Trình duyệt đang bị dừng',
    })

def start_profile_thread(profile_id):
    stop_event = threading.Event()
    thread = threading.Thread(target=start_crawl_up, args=(profile_id,))
    crawl_adsStore[profile_id] = {
        'check': 2,
        'status': 'Bắt đầu thực khi',
        'status_process': 1,
        'stop_event': stop_event,
        'thread': thread,
    }
    thread.start()
    
