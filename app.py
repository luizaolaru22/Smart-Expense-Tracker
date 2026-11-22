
from flask import Flask, render_template, request, redirect, url_for
from database import create_database, add_transaction, get_transactions, get_total

app = Flask(__name__)

create_database()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        amount = request.form.get("suma")
        transaction_type = request.form.get("tip")
        category = request.form.get("categorie")

        if amount and transaction_type in ["income", "expense"] and category:
            try:
                amount = float(amount)

                if amount > 0:
                    add_transaction(amount, transaction_type, category)

            except ValueError:
                pass

        return redirect(url_for("home"))

    transactions = get_transactions()

    income = get_total("income")
    expenses = get_total("expense")
    balance = income - expenses

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=balance
    )


if __name__ == "__main__":
    app.run(debug=True)
