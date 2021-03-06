import os
import db
import logging
import flask
from flask import make_response, jsonify, request, render_template, redirect, abort
from flask_httpauth import HTTPBasicAuth

app = flask.Flask(__name__, template_folder='template')
auth = HTTPBasicAuth()

user = os.getenv("API_USERNAME")
password = os.getenv("API_PASSWORD")
fav_ico = os.getenv("FAV_ICO")

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if user is None:
    logging.warning("No username set, so setting default (admin).")
    user = "admin"
if password is None:
    logging.warning("No password set, so setting default (admin).")
    password = "admin"

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


@app.route('/favicon.ico')
def favicon():
    if fav_ico is None or "http" not in fav_ico:
        return abort(404)
    return redirect(fav_ico)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    limit = request.args.get('limit', default=24, type=int)
    rooms = db.get_rooms(limit)
    return render_template('index.html', rooms=rooms, limit=limit)


@app.route('/api/v1/rooms', methods=['GET'])
@auth.login_required
def get_all():
    if request.json and 'limit' in request.json:
        limit = request.json.get('limit', 24)
    else:
        limit = 24
    rooms = db.get_rooms(limit)
    return jsonify(rooms)


@app.route('/api/v1/room/<string:name>', methods=['GET'])
@auth.login_required
def get_room(name):
    if request.json and 'limit' in request.json:
        limit = request.json.get('limit', 48)
    else:
        limit = 48
    room = db.get_by_name(name, limit)
    if room == 1:
        return make_response(jsonify({'error': 'Room not found.'}), 404)
    if room == 2:
        return make_response(jsonify({'error': 'No data found for room.'}), 204)
    return jsonify(room)


@app.route('/api/v1/room', methods=['POST'])
@auth.login_required
def create_room():
    if not request.json or 'name' not in request.json:
        make_response(jsonify({'error': 'Request invalid.'}), 400)
    name = request.json['name']
    result = db.create_room(name)
    if result:
        return jsonify({'success': 'Room created.', 'room': name}), 201
    else:
        return make_response(jsonify({'error': 'Room already exists.', 'room': name}), 409)


@app.route('/api/v1/room/<string:name>', methods=['POST'])
@auth.login_required
def insert_data(name):
    if not request.json or 'temperature' not in request.json or 'humidity' not in request.json:
        return make_response(jsonify({'error': 'Missing update data.'}), 400)
    temperature = request.json.get('temperature', 0)
    humidity = request.json.get('humidity', 0)
    timestamp = request.json.get('timestamp', None)
    result = db.insert_data(name, temperature, humidity, timestamp)
    if result == 0:
        return make_response(jsonify({'success': 'Data inserted into room.', 'room': name}), 201)
    elif result == 1:
        return make_response(jsonify({'error': 'Room does not exist.'}), 404)
    elif result == 2:
        return make_response(jsonify({'error': 'Data for room already exists.'}), 409)


@app.route('/api/v1/room/<string:name>', methods=['DELETE'])
@auth.login_required
def delete_room(name):
    result = db.delete_room(name)
    if result:
        return jsonify({'success': 'Deleted room.', 'room': name})
    else:
        return make_response(jsonify({'error': 'Room does not exist.'}), 404)


app.run(host='0.0.0.0')
