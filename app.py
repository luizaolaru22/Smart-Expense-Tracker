
from flask import Flask, render_template, request, redirect, url_for
from database import create_database, add_transaction, get_transactions

app = Flask(__name__)

create_database()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        amount = request.form.get("suma")
        category = request.form.get("categorie")

        if amount and category:
            try:
                amount = float(amount)

                if amount > 0:
                    add_transaction(amount, category)

            except ValueError:
                pass

        return redirect(url_for("home"))

    transactions = get_transactions()
    return render_template("index.html", transactions=transactions)


if __name__ == "__main__":
    app.run(debug=True)
