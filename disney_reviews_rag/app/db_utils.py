import sqlite3
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_PATH = os.environ.get("DATABASE_PATH", 'request_counter.db')

def get_db_connection():
    """
    Establishes a connection to the SQLite database
    and returns the connection object.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database and creates the counter table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INTEGER PRIMARY KEY,
            value INTEGER NOT NULL
        )
    """)
    # Check if the counter exists, if not, create it with value 0
    cursor.execute("SELECT * FROM counter WHERE id = 1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO counter (id, value) VALUES (1, 0)")
    conn.commit()
    conn.close()

def get_counter():
    """
    Retrieves the current value of the counter.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM counter WHERE id = 1")
    count = cursor.fetchone()["value"]
    conn.close()
    return count

def increment_counter():
    """
    Atomically increments the counter value.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
    conn.commit()
    conn.close()

def reset_counter():
    """
    Resets the counter value to zero.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE counter SET value = 0 WHERE id = 1")
    conn.commit()
    conn.close()