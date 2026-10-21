import sqlite3
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = 'spendly.db'

def get_db():
    """
    Returns a SQLite connection with row_factory set to sqlite3.Row
    and foreign keys enabled.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db():
    """
    Creates the database tables.
    """
    with sqlite3.connect(DATABASE) as conn:
        # Create Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Create Expenses table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

def seed_db():
    """
    Populates the database with sample data for development.
    """
    conn = sqlite3.connect(DATABASE)

    # Sample users
    users = [
        ('Alice Smith', 'alice@example.com', generate_password_hash('password123')),
        ('Bob Jones', 'bob@example.com', generate_password_hash('password456')),
        ('Charlie Brown', 'charlie@example.com', generate_password_hash('password789'))
    ]

    conn.executemany(
        'INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)',
        users
    )
    conn.commit()

    # Get user IDs to associate expenses
    cursor = conn.execute('SELECT id, email FROM users')
    user_map = {email: id for id, email in cursor.fetchall()}

    # Sample expenses
    expenses = [
        (user_map['alice@example.com'], 12.50, 'Food', 'Lunch at Deli', '2023-10-01'),
        (user_map['alice@example.com'], 45.00, 'Transport', 'Gas refill', '2023-10-02'),
        (user_map['alice@example.com'], 120.00, 'Entertainment', 'Concert ticket', '2023-10-05'),
        (user_map['bob@example.com'], 8.00, 'Food', 'Coffee', '2023-10-01'),
        (user_map['bob@example.com'], 600.00, 'Rent', 'October Rent', '2023-10-01'),
        (user_map['bob@example.com'], 25.00, 'Transport', 'Uber', '2023-10-03'),
        (user_map['charlie@example.com'], 15.00, 'Food', 'Snacks', '2023-10-02'),
        (user_map['charlie@example.com'], 50.00, 'Entertainment', 'Movie', '2023-10-04'),
        (user_map['charlie@example.com'], 10.00, 'Transport', 'Bus pass', '2023-10-06'),
        (user_map['charlie@example.com'], 100.00, 'Shopping', 'New shoes', '2023-10-07'),
    ]

    conn.executemany(
        'INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)',
        expenses
    )
    conn.commit()
    conn.close()

def create_user(name, email, password):
    """
    Hashes the password and inserts a new user into the database.
    Returns the new user's ID.
    """
    hashed_password = generate_password_hash(password)
    db = get_db()
    cursor = db.execute(
        'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
        (name, email, hashed_password)
    )
    db.commit()
    return cursor.lastrowid

def get_user_by_email(email):
    """
    Retrieves a user record from the database by email.
    Returns a sqlite3.Row object if found, otherwise None.
    """
    db = get_db()
    return db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
