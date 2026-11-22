
import sqlite3
from datetime import date


def create_database():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_transaction(amount, category):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (amount, type, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (amount, "expense", category, "", date.today().isoformat()))

    conn.commit()
    conn.close()


def get_transactions():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    transactions = cursor.fetchall()

    conn.close()
    return transactions


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
