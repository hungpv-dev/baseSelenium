from flask import Blueprint, jsonify, request
from sql import groups

group = Blueprint('group', __name__)

@group.route('/', methods=['GET','POST'])
def get():
    if request.method == 'POST':
        data = request.json
        res = groups.create(data)
        return jsonify({
            'message': 'Cập nhập nhóm thành công',
            'res': res,
        }), 201
    else:
        params = request.args
        data = groups.get_all(params)
        return jsonify(data)

@group.route('/<int:id>', methods=['GET','PUT','DELETE'])
def show(id):
    if request.method == 'GET':
        res = groups.show(id)
        return jsonify(data)
    if request.method == 'PUT':
        data = request.json
        res = groups.update(id, data)
        return jsonify({
            'message': 'Cập nhập nhóm thành công',
            'res': res,
        }), 200
    else:
        data = groups.destroy(id)
        return jsonify({
            'message': 'Xoá thông tin nhóm',
        }), 200


@group.route('/operating-systems')
def operasystem():
    data = groups.get_operasystem()
    return jsonify(data)


