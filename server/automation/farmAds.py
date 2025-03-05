from flask import Blueprint, jsonify, request
from helpers import config
from handles import start_crawl_up, stop_crawl_up
from stores import farm_ads as farm_adsStore
import threading
from sql import profiles
import os

farm_ads = Blueprint('farm_ads', __name__)

@farm_ads.route('/')
def list():
    data = {}   
    for ix, item in farm_adsStore.items():
        data[str(ix)] = {
            "check": item["check"],
            "status": item["status"],
            "status_process": item["status_process"],
        }
    return jsonify(data)

@farm_ads.route('start/<string:id>', methods=['POST'])
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

@farm_ads.route('stop/<string:id>', methods=['POST'])
def stop(id):
    print(id, farm_adsStore)
    if id not in farm_adsStore:
        return jsonify({
            'message': 'Profile không tồn tại',
        }), 404

    farm_adsStore[id]['check'] = 2
    farm_adsStore[id]['status_process'] = 2
    farm_adsStore[id]['stop_event'].set()
    farm_adsStore[id]['status'] = 'Trình duyệt đang bị dừng'

    thread = threading.Thread(target=stop_crawl_up, args=(id,))
    thread.start()

    return jsonify({
        'message': 'Trình duyệt đang bị dừng',
    })

def start_profile_thread(profile_id):
    stop_event = threading.Event()
    thread = threading.Thread(target=start_crawl_up, args=(profile_id,))
    farm_adsStore[profile_id] = {
        'check': 2,
        'status': 'Bắt đầu thực khi',
        'status_process': 1,
        'stop_event': stop_event,
        'thread': thread,
    }
    print(farm_adsStore)
    thread.start()
    
