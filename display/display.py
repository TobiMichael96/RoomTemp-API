import flask
from flask import render_template
import requests


app = flask.Flask(__name__, template_folder='template')


@app.route('/')
def index():
    rooms = requests.get('https://roomtemp.tmem.de/api/v1/rooms')
    rooms = rooms.json()
    return render_template('index.html', rooms=rooms)


app.run(host='0.0.0.0')
