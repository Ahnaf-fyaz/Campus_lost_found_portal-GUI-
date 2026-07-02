import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # so we can access columns by name
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            first TEXT,
            last TEXT,
            dob TEXT,
            email TEXT,
            phone TEXT,
            student_id TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Lost (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            room INTEGER,
            floor INTEGER,
            item TEXT,
            color TEXT,
            time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Found (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            room INTEGER,
            floor INTEGER,
            item TEXT,
            color TEXT,
            time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ------------------ CRUD Operations ------------------

def get_all_users():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM Users').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_user(data):
    conn = get_connection()
    conn.execute('INSERT INTO Users (username, password, first, last, dob, email, student_id, phone) '
                 'VALUES (:username, :password, :first, :last, :dob, :email, :student_id, :phone)', data)
    conn.commit()
    conn.close()

def get_all_lost():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM Lost').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_lost(data):
    conn = get_connection()
    conn.execute('INSERT INTO Lost (username, room, floor, item, color, time) '
                 'VALUES (:username, :room, :floor, :item, :color, :time)', data)
    conn.commit()
    conn.close()

def get_all_found():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM Found').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_found(data):
    conn = get_connection()
    conn.execute('INSERT INTO Found (username, room, floor, item, color, time) '
                 'VALUES (:username, :room, :floor, :item, :color, :time)', data)
    conn.commit()
    conn.close()

def get_all_notifications():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM Notifications').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_notification(username, message):
    conn = get_connection()
    conn.execute('INSERT INTO Notifications (username, message) VALUES (?, ?)',
                 (username, message))
    conn.commit()
    conn.close()

def clear_notifications_for_user(username):
    conn = get_connection()
    conn.execute('DELETE FROM Notifications WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def delete_lost_item(item_id):
    conn = get_connection()
    conn.execute('DELETE FROM Lost WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def delete_found_item(item_id):
    conn = get_connection()
    conn.execute('DELETE FROM Found WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
def replace_all_lost(items):
    conn = get_connection()
    conn.execute('DELETE FROM Lost')
    for item in items:
        conn.execute('INSERT INTO Lost (username, room, floor, item, color, time) '
                     'VALUES (:username, :room, :floor, :item, :color, :time)', item)
    conn.commit()
    conn.close()

def replace_all_found(items):
    conn = get_connection()
    conn.execute('DELETE FROM Found')
    for item in items:
        conn.execute('INSERT INTO Found (username, room, floor, item, color, time) '
                     'VALUES (:username, :room, :floor, :item, :color, :time)', item)
    conn.commit()
    conn.close()