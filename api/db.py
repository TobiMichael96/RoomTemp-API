import sqlite3
import logging
from datetime import datetime, timedelta

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

DATABASE_NAME = "db/rooms.sqlite"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_table():
    table = "CREATE TABLE IF NOT EXISTS rooms (name VARCHAR NOT NULL);"
    db = get_db()
    cursor = db.cursor()
    cursor.execute(table)


def build_json(cursor, limit):
    result = []
    for row in cursor.fetchall():
        timestamp = datetime.fromtimestamp(row[0])
        if limit <= 48 and timestamp.minute == 30:
            continue
        room = {
            'time': timestamp.strftime('%H:%M'),
            'date': timestamp.strftime('%A, %d.%m.%Y'),
            'temperature': row[1],
            'humidity': row[2]
        }
        if len(row) > 3:
            print(row[3])
        result.append(room)
    return result


def delete_old(name):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM " + name + " WHERE timestamp < ?"
    seven_days_before = datetime.now() - timedelta(days=7)
    seven_days_before_timestamp = datetime.timestamp(seven_days_before)
    cursor.execute(statement, [seven_days_before_timestamp])
    db.commit()


def get_rooms(limit):
    db = get_db()
    cursor = db.cursor()
    rooms_query = "SELECT name FROM rooms ORDER BY name"
    cursor.execute(rooms_query)
    rooms = [x[0] for x in set(cursor.fetchall())]
    result = {}
    for room in rooms:
        statement = "SELECT timestamp, temperature, humidity FROM " + room + \
                    " ORDER BY timestamp DESC LIMIT ?"
        cursor.execute(statement, [limit * 2])
        result[room] = build_json(cursor, limit)
    return result


def get_by_name(name, limit):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT timestamp, temperature, humidity FROM " + name + \
                " ORDER BY timestamp DESC LIMIT ?"
    try:
        cursor.execute(statement, [limit * 2])
    except sqlite3.DatabaseError:
        return 1
    if cursor.rowcount == 0:
        return 2
    return build_json(cursor, limit)


def create_room(name):
    db = get_db()
    cursor = db.cursor()
    statement_insert = "INSERT INTO rooms (name) VALUES (?)"
    cursor.execute(statement_insert, [name])
    statement = "CREATE TABLE " + name + " (timestamp TIMESTAMP UNIQUE, humidity INTEGER, temperature INTEGER);"
    try:
        cursor.execute(statement)
        db.commit()
    except sqlite3.DatabaseError:
        return False
    return True


def insert_data(name, temperature, humidity, timestamp):
    db = get_db()
    cursor = db.cursor()
    if timestamp is None:
        timestamp = datetime.now()

    if timestamp.minute < 15:
        timestamp = timestamp.replace(microsecond=0, second=0, minute=0)
    elif 15 <= timestamp.minute < 45:
        timestamp = timestamp.replace(microsecond=0, second=0, minute=30)
    elif timestamp.minute >= 45:
        timestamp = timestamp.replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)

    statement = "INSERT INTO " + name + " (temperature, humidity, timestamp) VALUES (?, ?, ?)"
    try:
        cursor.execute(statement, [temperature, humidity, timestamp.timestamp()])
        db.commit()
        delete_old(name)
    except sqlite3.OperationalError:
        return 1
    except sqlite3.IntegrityError:
        return 2
    return 0


def delete_room(name):
    db = get_db()
    cursor = db.cursor()
    drop_statement = "DROP TABLE " + name
    try:
        cursor.execute(drop_statement)
        delete_statement = "DELETE FROM rooms WHERE name = ?"
        cursor.execute(delete_statement, [name])
        db.commit()
    except sqlite3.OperationalError:
        return False
    return True
