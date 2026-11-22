
import os
import math
import secrets
import sqlite3
import calendar

from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import (
    create_database,
    add_user,
    get_user,
    update_password,
    add_transaction,
    get_transactions,
    get_total
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-only")

create_database()


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not password:
            return render_template("register.html", error="Complete all fields.")

        if len(password) < 8:
            return render_template("register.html", error="Password must have at least 8 characters.")

        if password != confirm:
            return render_template("register.html", error="Passwords do not match.")

        if get_user(username):
            return render_template("register.html", error="Username already exists.")

        recovery_code = secrets.token_urlsafe(18)

        try:
            add_user(
                username,
                generate_password_hash(password),
                generate_password_hash(recovery_code)
            )
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists.")

        return render_template("register.html", recovery_code=recovery_code)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user(username)

        if user and check_password_hash(user[2], password):
            session.clear()
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Incorrect username or password.")

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        recovery_code = request.form.get("recovery_code", "")
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        user = get_user(username)

        if not user or not user[3] or not check_password_hash(user[3], recovery_code):
            return render_template(
                "forgot_password.html",
                error="Invalid username or recovery code."
            )

        if len(new_password) < 8:
            return render_template(
                "forgot_password.html",
                error="Password must have at least 8 characters."
            )

        if new_password != confirm:
            return render_template(
                "forgot_password.html",
                error="Passwords do not match."
            )

        update_password(username, generate_password_hash(new_password))
        session.clear()

        return render_template("forgot_password.html", success=True)

    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        amount = request.form.get("suma", "")
        transaction_type = request.form.get("tip", "")
        category = request.form.get("categorie", "")

        categories = {
            "income": ["Salariu", "Bursa", "Cadouri", "Altele"],
            "expense": ["Mancare", "Transport", "Cumparaturi", "Facturi", "Altele"]
        }

        if transaction_type in categories and category in categories[transaction_type]:
            try:
                amount = float(amount)

                if math.isfinite(amount) and amount > 0:
                    add_transaction(amount, transaction_type, category, user_id)

            except ValueError:
                pass

        return redirect(url_for("dashboard"))

    transactions = get_transactions(user_id)
    income = get_total("income", user_id)
    expenses = get_total("expense", user_id)
    balance = income - expenses

    return render_template(
        "index.html",
        transactions=transactions[:5],
        income=income,
        expenses=expenses,
        balance=balance
    )


@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    transactions = get_transactions(session["user_id"])

    return render_template("history.html", transactions=transactions)


@app.route("/statistics")
def statistics():
    if "user_id" not in session:
        return redirect(url_for("login"))

    period = request.args.get("period", "month")

    if period not in ["week", "month", "year"]:
        period = "month"

    # Data aleasa de utilizator
    selected_date = request.args.get("date", date.today().isoformat())

    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = date.today()

    # Stabilim intervalul analizat
    if period == "week":
        start = selected_date - timedelta(days=selected_date.weekday())
        end = start + timedelta(days=6)

    elif period == "month":
        start = selected_date.replace(day=1)
        last_day = calendar.monthrange(
            selected_date.year, selected_date.month
        )[1]
        end = selected_date.replace(day=last_day)

    else:
        start = selected_date.replace(month=1, day=1)
        end = selected_date.replace(month=12, day=31)

    # Pregatim etichetele pentru grafic
    labels = []
    income_data = []
    expense_data = []

    if period == "year":
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        labels = month_names

    else:
        current_day = start

        while current_day <= end:
            labels.append(current_day.strftime("%d.%m"))
            current_day += timedelta(days=1)

    income_data = [0] * len(labels)
    expense_data = [0] * len(labels)

    total_income = 0
    total_expenses = 0

    transactions = get_transactions(session["user_id"])

    for transaction in transactions:
        transaction_date = date.fromisoformat(transaction[5])
        amount = transaction[1]
        transaction_type = transaction[2]

        if start <= transaction_date <= end:

            if period == "year":
                position = transaction_date.month - 1
            else:
                position = (transaction_date - start).days

            if transaction_type == "income":
                income_data[position] += amount
                total_income += amount

            elif transaction_type == "expense":
                expense_data[position] += amount
                total_expenses += amount

    income_data = [round(value, 2) for value in income_data]
    expense_data = [round(value, 2) for value in expense_data]

    return render_template(
        "statistics.html",
        period=period,
        selected_date=selected_date.isoformat(),
        labels=labels,
        income_data=income_data,
        expense_data=expense_data,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=total_income - total_expenses
    )


if __name__ == "__main__":
    app.run(debug=True)
