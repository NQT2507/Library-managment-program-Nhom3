import sqlite3
import hashlib
import os

# Đường dẫn an toàn trỏ ra thư mục gốc
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "library.db")

def hash_password(password):
    """Băm mật khẩu bằng thuật toán SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Khởi tạo CSDL và tạo sẵn tài khoản Admin nếu chưa có"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Bảng Users
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    
    # 2. Bảng Categories
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    # 3. Bảng Books 
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category_id INTEGER,
        is_hidden INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )''')
    
    # 4. Bảng Book_Copies
    cursor.execute('''CREATE TABLE IF NOT EXISTS book_copies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        status TEXT DEFAULT 'available',
        FOREIGN KEY (book_id) REFERENCES books (id)
    )''')
    
    # 5. Bảng Borrow_Records
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

    # Tạo tài khoản Thủ thư mặc định (admin / 123456)
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('123456'), 'librarian'))
    
    conn.commit()
    conn.close()

def verify_login(username, password):
    """Kiểm tra đăng nhập, trả về role nếu thành công, None nếu thất bại"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password_hash=?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None
