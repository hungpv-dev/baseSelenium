from flask import Blueprint, jsonify, request
from helpers import config, save_config

settings = Blueprint('settings',__name__)

@settings.route('/')
def list():
    data = config('driver')
    return jsonify({
        'data': data
    })

@settings.route('/', methods=['POST'])
def store():
    data = request.json
    save_config('driver', data)  
    return jsonify({
        'message': 'Cập nhật thành công',
        'data': data
    })
    