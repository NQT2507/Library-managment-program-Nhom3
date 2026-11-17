import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "library.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category_id INTEGER,
        is_hidden INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS book_copies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        status TEXT DEFAULT 'available',
        FOREIGN KEY (book_id) REFERENCES books (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        copy_id INTEGER,
        reader_id INTEGER,
        borrow_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        FOREIGN KEY (copy_id) REFERENCES book_copies (id),
        FOREIGN KEY (reader_id) REFERENCES users (id)
    )''')

    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('123456'), 'librarian'))
        
    cursor.execute("SELECT * FROM users WHERE username='student'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ('student', hash_password('123456'), 'reader'))

    default_cats = ['Công nghệ thông tin', 'Kinh tế', 'Văn học', 'Kỹ năng sống', 'Khoa học']
    for cat in default_cats:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
    
    conn.commit()
    conn.close()

def verify_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password_hash=?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def get_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    rows = cursor.fetchall()
    conn.close()
    return rows
