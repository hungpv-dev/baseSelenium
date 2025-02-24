from flask import Blueprint, jsonify, request
from sql import proxies

proxy = Blueprint('proxy', __name__)

@proxy.route('/')
def get():
    params = request.args
    data = proxies.get_all(params)
    return jsonify(data)
