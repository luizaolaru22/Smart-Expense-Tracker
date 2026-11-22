from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bine ai venit in Smart Expense Tracker!"

if __name__ == "__main__":
    app.run(debug=True)