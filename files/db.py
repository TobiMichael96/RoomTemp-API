import sqlite3
from datetime import datetime


DATABASE_NAME = "/db/rooms.sqlite"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_table():
    table = "CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
            "name VARCHAR NOT NULL UNIQUE, " \
            "temp INTEGER DEFAULT 0, " \
            "updated VARCHAR);"
    db = get_db()
    cursor = db.cursor()
    cursor.execute(table)


def build_json(cursor):
    result = []
    for row in cursor.fetchall():
        room = {
            'name': row[1],
            'temp': row[2],
            'updated': row[3]
        }
        result.append(room)
    return result


def insert_room(name, temp):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO rooms(name, temp, updated) VALUES (?, ?, ?)"
    cursor.execute(statement, [name, temp, datetime.now()])
    db.commit()
    return True


def update_room(name, temp):
    db = get_db()
    cursor = db.cursor()
    statement = "UPDATE rooms SET temp = ?, updated = ? WHERE name = ?"
    cursor.execute(statement, [temp, datetime.now(), name])
    db.commit()
    return {'name': name, 'temp': temp}


def delete_room(name):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM rooms WHERE name = ?"
    cursor.execute(statement, [name])
    db.commit()
    return {'success': True, 'name': name}


def get_by_name(name):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT id, name, temp, updated FROM rooms WHERE name = ?"
    cursor.execute(statement, [name])
    return build_json(cursor)


def get_rooms():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * from rooms"
    cursor.execute(query)
    return build_json(cursor)

