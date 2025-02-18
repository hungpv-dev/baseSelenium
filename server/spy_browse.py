from flask import Blueprint, jsonify
from stores import browse_fb
import threading
from handles import create_browse_link_spy_fb
spy_browse = Blueprint('driver',__name__)

@spy_browse.route('/start/<int:account_id>', methods=['POST'])
def start(account_id):
    if account_id in browse_fb and browse_fb[account_id]['thread'].is_alive():
        return jsonify({'message': 'Driver is already running'}), 400
    
    stop_event = threading.Event()
    driver_theard = threading.Thread(target=create_browse_link_spy_fb, args=(account_id, stop_event))
    driver_theard.daemon = True
    driver_theard.start()
    
    browse_fb[account_id] = {
        'thread': driver_theard,
        'stop_event': stop_event
    }
    return jsonify({'message': 'Driver started'})

@spy_browse.route('/stop/<int:account_id>', methods=['POST'])
def stop(account_id):
    if account_id in browse_fb:
        browse_fb[account_id]['stop_event'].set()
        browse_fb[account_id]['thread'].join()
        del browse_fb[account_id]
        return jsonify({'message': 'Driver stopped'})
    else:
        return jsonify({'message': 'No driver is running for this account'}), 400