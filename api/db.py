import sqlite3
from datetime import datetime
import pytz

DATABASE_NAME = "/db/rooms.sqlite"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_table():
    table = "CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
            "name VARCHAR NOT NULL UNIQUE, " \
            "temperature INTEGER DEFAULT 0, " \
            "humidity INTEGER DEFAULT 0, " \
            "updated VARCHAR);"
    db = get_db()
    cursor = db.cursor()
    cursor.execute(table)


def build_json(cursor):
    result = []
    for row in cursor.fetchall():
        room = {
            'name': row[1],
            'temperature': row[2],
            'humidity': row[3],
            'updated': row[4]
        }
        result.append(room)
    return result


def insert_room(name, temperature, humidity):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO rooms(name, temperature, humidity, updated) VALUES (?, ?, ?, ?)"
    cursor.execute(statement, [name, temperature, humidity, datetime.now(pytz.timezone('Europe/Berlin')).strftime("%a %d.%m. - %H:%M:%S")])
    db.commit()
    return True


def update_room(name, temperature=None, humidity=None):
    db = get_db()
    cursor = db.cursor()
    if temperature is not None:
        statement = "UPDATE rooms SET temperature = ?, updated = ? WHERE name = ?"
        cursor.execute(statement, [temperature, datetime.now(pytz.timezone('Europe/Berlin')).strftime("%a %d.%m. - %H:%M:%S"), name])
    if humidity is not None:
        statement = "UPDATE rooms SET humidity = ?, updated = ? WHERE name = ?"
        cursor.execute(statement, [humidity, datetime.now(pytz.timezone('Europe/Berlin')).strftime("%a %d.%m. - %H:%M:%S"), name])
    db.commit()
    return cursor.rowcount


def delete_room(name):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM rooms WHERE name = ?"
    cursor.execute(statement, [name])
    db.commit()
    return cursor.rowcount


def get_by_name(name):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT id, name, temperature, humidity, updated FROM rooms WHERE name = ?"
    cursor.execute(statement, [name])
    return build_json(cursor)


def get_rooms():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * from rooms"
    cursor.execute(query)
    return build_json(cursor)

