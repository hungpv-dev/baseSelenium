from flask import Blueprint, jsonify
from managers import create_chrome
from time import sleep

driver = Blueprint('driver',__name__)

@driver.route('/start')
def start():
    driver = create_chrome()
    driver.get('https://facebook.com')
    sleep(3)
    driver.quit()
    print('Start browser')
    return jsonify({
        'message': 'What the fuck?',
    })