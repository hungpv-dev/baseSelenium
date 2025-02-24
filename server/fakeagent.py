from flask import Blueprint, jsonify, request
from fake_useragent import UserAgent

useragent = Blueprint('useragent', __name__)
ua = UserAgent()

@useragent.route('/fake', methods=['GET'])
def fake():
    ua = UserAgent(os=['Windows', 'Linux', 'Mac OS X'])
    user_agent = ua.random
    return jsonify({"user_agent": user_agent})
