from flask import Blueprint, jsonify, request,session
import threading
import os
from sql.login import Authen

login = Blueprint('login', __name__)

@login.route('/login', methods=['POST'])
def checkLogin():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    auth = Authen()
    res = auth.Checklogin(username, password)
    # Kiểm tra phản hồi từ API Laravel
    if res.get("check"):
        session['user'] = res.get("data")
        return jsonify({
            'message': 'Đăng nhập thành công',
        }), 200
    else:
        return jsonify({
            'message': 'Tên đăng nhập hoặc mật khẩu không đúng'
        }), 401
@login.route("/login/info")
def login_info():
    return jsonify({
        'message': 'Thông tin đăng nhập',
        'data': session.get('user')
    })