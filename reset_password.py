
import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash


username = input("Username: ").strip()

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT id FROM users WHERE username = ?",
    (username,)
)

user = cursor.fetchone()

if user is None:
    print("User not found.")
else:
    password = getpass("New password: ")
    confirm_password = getpass("Confirm password: ")

    if len(password) < 8:
        print("Password must have at least 8 characters.")

    elif password != confirm_password:
        print("Passwords do not match.")

    else:
        password_hash = generate_password_hash(password)

        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (password_hash, user[0])
        )

        conn.commit()
        print("Password updated successfully!")

conn.close()
