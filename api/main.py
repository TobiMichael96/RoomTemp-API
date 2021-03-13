import os
import sqlite3
import db

import flask
from flask import make_response, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth

app = flask.Flask(__name__)
auth = HTTPBasicAuth()

user = os.getenv("API_USERNAME")
password = os.getenv("API_PASSWORD")

if user is None or password is None:
    print("Username or password not set.")
    exit(1)

db.create_table()


@auth.get_password
def get_password(username):
    if username == user:
        return password
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def home():
    return "<h1>API</h1><p>This site is an API for room temperatures.</p>"


# A route to return all of the available entries in our catalog.
@app.route('/api/v1/rooms', methods=['GET'])
def get_all():
    rooms = db.get_rooms()
    return jsonify(rooms)


@app.route('/api/v1/room/<string:name>', methods=['GET'])
def get_room(name):
    room = db.get_by_name(name)
    if len(room) == 0:
        return make_response(jsonify({'error': 'Room not found.'}), 404)
    return jsonify(room[0])


@app.route('/api/v1/room', methods=['POST'])
@auth.login_required
def insert_room():
    if not request.json or 'name' not in request.json:
        abort(400)

    name = request.json['name']
    temp = request.json.get('temp', 0)
    try:
        db.insert_room(name, temp)
        return jsonify({'temp': temp, 'name': name}), 201
    except sqlite3.IntegrityError:
        return make_response(jsonify({'error': "Room already exists.", 'name': name}), 409)


@app.route('/api/v1/room/<string:name>', methods=['PUT'])
@auth.login_required
def update_room(name):
    if not request.json or 'temp' not in request.json:
        abort(400)
    temp = request.json.get('temp', 0)
    result = db.update_room(name, temp)
    if result > 0:
        return jsonify({'success': True, 'name': name, 'temp': temp})
    else:
        return make_response(jsonify({'error': 'Room not found.'}), 404)


@app.route('/api/v1/room/<string:name>', methods=['DELETE'])
@auth.login_required
def delete_task(name):
    result = db.delete_room(name)
    if result > 0:
        return jsonify({'success': True, 'name': name})
    else:
        return make_response(jsonify({'error': 'Room not found.'}), 404)


app.run(host='0.0.0.0')
