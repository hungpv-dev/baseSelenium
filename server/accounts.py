from flask import Blueprint, jsonify, request
from sql import accounts
from stores import store_newsfeed


account = Blueprint('account',__name__)

@account.route('/')
def list():
    typenot = request.args.get('typenot')
    name = request.args.get('name','') or ''
    params = {
        'typenot': typenot,
        'name': name,
    }
    list_account = accounts.get_all(params)
    for acc in list_account:
        if acc['id'] in store_newsfeed:
            acc['running'] = 1
        else:
            acc['running'] = 2
    return jsonify({
        'data': list_account,
    })