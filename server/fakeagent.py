from flask import Blueprint, jsonify
from fake_useragent import UserAgent
import random

useragent = Blueprint('useragent', __name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
]

@useragent.route('/fake', methods=['GET'])
def fake():
    try:
        ua = UserAgent(platforms='desktop', use_cache_server=True)
        user_agent = ua.random
        return jsonify({"user_agent": user_agent})
    except Exception as e:
        user_agent = random.choice(USER_AGENTS)
        return jsonify({"user_agent": user_agent})

