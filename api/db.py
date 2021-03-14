import sqlite3
from datetime import datetime, timedelta
import pytz

DATABASE_NAME = "/db/rooms.sqlite"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_table():
    table = "CREATE TABLE IF NOT EXISTS rooms (name VARCHAR NOT NULL);"
    db = get_db()
    cursor = db.cursor()
    cursor.execute(table)


def build_json(cursor):
    result = []
    for row in cursor.fetchall():
        room = {
            'time': row[0],
            'temperature': row[1],
            'humidity': row[2]
        }
        result.append(room)
    return result


def delete_old(name):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM " + name + " WHERE timestamp < ?"
    seven_days_before = datetime.now(tz=pytz.timezone('Europe/Berlin')) - timedelta(days=7)
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
        statement = "SELECT time, temperature, humidity FROM " + room + " ORDER BY timestamp DESC LIMIT ?"
        cursor.execute(statement, [limit])
        result[room] = build_json(cursor)
    return result


def get_by_name(name, limit):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT time, temperature, humidity FROM " + name + " ORDER BY timestamp DESC LIMIT ?"
    try:
        cursor.execute(statement, [limit])
    except sqlite3.DatabaseError:
        return False
    return build_json(cursor)


def create_room(name):
    db = get_db()
    cursor = db.cursor()
    statement_insert = "INSERT INTO rooms (name) VALUES (?)"
    cursor.execute(statement_insert, [name])
    statement = "CREATE TABLE " + name + " (time DATETIME PRIMARY KEY UNIQUE, " \
                "temperature INTEGER DEFAULT 0, " \
                "humidity INTEGER DEFAULT 0, " \
                "timestamp TIMESTAMP DEFAULT 0);"
    try:
        cursor.execute(statement)
        db.commit()
    except sqlite3.DatabaseError:
        return False
    return True


def insert_data(name, temperature, humidity):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO " + name + " (time, temperature, humidity, timestamp) VALUES (?, ?, ?, ?)"
    try:
        cursor.execute(statement, [datetime.now(tz=pytz.timezone('Europe/Berlin')).strftime("%a %d.%m. - %H:%M"),
                                   temperature, humidity,
                                   datetime.timestamp(datetime.now(tz=pytz.timezone('Europe/Berlin')))])
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
