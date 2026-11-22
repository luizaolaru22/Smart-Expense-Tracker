
import sqlite3
from datetime import date


def create_database():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            recovery_hash TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            user_id INTEGER
        )
    """)

    # Adaugam coloanele noi si in bazele de date existente.
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]

    if "recovery_hash" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN recovery_hash TEXT")

    cursor.execute("PRAGMA table_info(transactions)")
    transaction_columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in transaction_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()


def add_user(username, password_hash, recovery_hash):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password, recovery_hash)
        VALUES (?, ?, ?)
    """, (username, password_hash, recovery_hash))

    conn.commit()
    conn.close()


def get_user(username):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def update_password(username, password_hash):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET password = ?, recovery_hash = NULL
        WHERE username = ?
    """, (password_hash, username))

    conn.commit()
    conn.close()


def save_recovery_code(user_id, recovery_hash):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET recovery_hash = ? WHERE id = ?",
        (recovery_hash, user_id)
    )

    conn.commit()
    conn.close()


def add_transaction(amount, transaction_type, category, user_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (amount, type, category, description, date, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        amount,
        transaction_type,
        category,
        "",
        date.today().isoformat(),
        user_id
    ))

    conn.commit()
    conn.close()


def get_transactions(user_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    transactions = cursor.fetchall()
    conn.close()
    return transactions


def get_total(transaction_type, user_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount) FROM transactions
        WHERE type = ? AND user_id = ?
    """, (transaction_type, user_id))

    total = cursor.fetchone()[0]
    conn.close()

    if total is None:
        return 0

    return total


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
