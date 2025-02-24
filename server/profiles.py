from flask import Blueprint, jsonify, request
from helpers import config
from handles import create_profile, close_profile
import threading
from sql import profiles as sql_profiles, groups
from stores import store_profiles
import os

profiles = Blueprint('profiles', __name__)

@profiles.route('/', methods=['GET'])
def list():
    params = request.args
    data = sql_profiles.get_all(params)
    for item in data:
        profile_id = str(item.get('id'))
        if profile_id in store_profiles and store_profiles[profile_id]['thread'].is_alive():
            item['status_process'] = 1
            item['check'] = store_profiles[profile_id]['check']
            item['status_text'] = store_profiles[profile_id]['status']
        else:
            item['status_process'] = 2
            item['check'] = 1
            item['status_text'] = '-'
    return jsonify({
        'data': data,
    })

@profiles.route('create', methods=['POST'])
def create():
    data = request.json
    user_dir = data.get('user_dir')
    if os.path.exists(user_dir):
        return jsonify({
            'message': 'Thư mục chứa profile đã tồn tại',
        }), 400
    res = sql_profiles.create(data)
    print(res)
    if 'id' not in res:
        return jsonify({
            'message': 'Có lỗi xảy ra, thử lại sau...',
            'res': res,
        }), 400
    id = str(res.get('id'))
    start_profile_thread(id)
    return jsonify({
        'message': 'Thêm mới profile thành công',
    })

@profiles.route('start/<string:id>', methods=['POST'])
def start(id):
    profile = sql_profiles.show(id)
    if not profile:
        return jsonify({
            'message': 'Profile không tồn tại',
        }), 404

    start_profile_thread(str(id))

    return jsonify({
        'message': 'Đang khởi tạo trình duyệt',
    })

@profiles.route('stop/<string:id>', methods=['POST'])
def stop(id):
    if id not in store_profiles:
        return jsonify({
            'message': 'Profile không tồn tại',
        }), 404

    store_profiles[id]['check'] = 2
    store_profiles[id]['stop_event'].set()
    store_profiles[id]['status'] = 'Trình duyệt đang bị dừng'

    thread = threading.Thread(target=close_profile, args=(id,))
    thread.start()

    return jsonify({
        'message': 'Trình duyệt đang bị dừng',
    })

@profiles.route('info', methods=['GET'])
def info():
    profile_info = {
        'user-dir': config('temps').get('profiles'), 
    }
    return jsonify(profile_info)

def start_profile_thread(profile_id):
    stop_event = threading.Event()
    thread = threading.Thread(target=create_profile, args=(profile_id,))
    thread.start()
    store_profiles[profile_id] = {
        'stop_event': stop_event,
        'thread': thread,
        'check': 2,
        'status': 'Đang khởi tạo trình duyệt'
    }
    
