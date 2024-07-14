import sqlite3
DATABASE = 'blog.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        # Create a default user. Requires generating a salt and hashing the password.
        salt = binascii.hexlify(os.urandom(16)).decode()
        data = "password" + salt

        # Perform a single SHA-256 hash
        hashed_password = hashlib.sha256(data.encode()).hexdigest()
        db.execute('INSERT INTO users (username, access_key, salt) VALUES (?, ?, ?)', ('admin', hashed_password, salt))
        db.commit()
