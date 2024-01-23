import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks."""

    user_id = session["user_id"]

    ## Executing database to gather information on current user
    transactions = db.execute(
        "SELECT symbol, SUM(shares) AS shares, price FROM transactions WHERE user_id = (?) GROUP BY symbol HAVING SUM(shares) > 0;",
        user_id,
    )
    cash = db.execute("SELECT cash FROM users WHERE id = (?);", user_id)

    # Checking money left in User databse
    total_cash = cash[0]["cash"]
    sum = int(total_cash)

    # Looping through all stocks hold by user and adding
    for row in transactions:
        stock = lookup(row["symbol"])
        row["name"] = stock["name"]
        row["price"] = stock["price"]
        row["total"] = row["price"] * row["shares"]
        sum += row["total"]
    return render_template("index.html", database=transactions, users=cash, sum=sum )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    # Checking if user post via valid symbol
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")
        stock = lookup(symbol.upper())

        if stock is None:
            return apology("Symbol Does Not Exist")

        # Check if shares is provided and is a positive integer
        try:
            shares = int(shares_str)
            if shares <= 0:
                return apology("Must provide a positive integer number of shares")
        except ValueError:
            return apology("Invalid number of shares")

        cash_db = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash_check = cash_db[0]["cash"]
        transaction = shares * stock["price"]

        if cash_check < transaction:
            return apology("Insufficient funds in your account")

        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"],
            symbol,
            shares,
            stock["price"],
        )
        update_cash = cash_check - transaction
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", update_cash, session["user_id"]
        )

        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Check database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Search details about the stock
        stock = lookup(str(request.form.get("symbol")))
        # Check for empty field
        if not stock:
            return apology("Invalid symbol!")

        # Format price
        price = float(stock["price"])
        name = stock["name"]
        symbol = stock["symbol"]
        print(name)
        return render_template("quote.html", name=name, price=usd(price), symbol=symbol)

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        retype_password = request.form.get("confirmation")
        if not username or not password or not retype_password:
            return apology("Please fill out all fields")

        if password != retype_password:
            return apology("Passwords do not match")

        if password == retype_password:
            if len(db.execute("SELECT * FROM users WHERE username = ?", username)) > 0:
                return apology("User already exist")
            try:
                hash = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username,hash) VALUES (?,?)", username, hash
                )
                flash("User Registered Successfully!")
            except:
                return apology("Can not register")

        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        # Fetch user's portfolio for displaying available stocks
        user_id = session["user_id"]
        portfolio = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
            user_id,
        )
        return render_template("sell.html", portfolio=portfolio)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")

        try:
            shares = float(shares_str)
        except ValueError:
            return apology("Invalid number of shares", 400)

        stock = lookup(symbol.upper())

        if stock is None:
            return apology("Symbol Does Not Exist")

        # Check if the user has enough shares to sell
        user_id = session["user_id"]
        user_shares_query = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ?",
            user_id,
            symbol,
        )

        if user_shares_query is None or shares > user_shares_query[0]["total_shares"]:
            return apology("Not enough shares to sell")

        # Calculate the transaction amount
        transaction = shares * stock["price"]

        # Update the transactions table for the sell
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id,
            symbol,
            -shares,
            stock["price"],
        )

        # Update the user's cash balance
        cash_query = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = cash_query[0]["cash"]
        update_cash = cash + transaction
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("change_password.html")
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")
        if not old_password or not new_password or not confirm_new_password:
            return apology("Please fill out all fields")

        rows = db.execute("SELECT hash FROM users WHERE id = ?", user_id)
        hash = rows[0]["hash"]
        if (
            check_password_hash(hash, old_password)
            and new_password == confirm_new_password
        ):
            new_password_hash = generate_password_hash(new_password)
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?", new_password_hash, user_id
            )
            flash("Password Changed!")
            return redirect("/")
        else:
            return apology("Password did not match")


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("add_cash.html")

    if request.method == "POST":
        amount = int(request.form.get("amount"))
        card = int(request.form.get("card"))

        if not amount or not card or amount <= 0 or 13 > card > 16:
            return apology("Fill all the required Fields")

        rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        if not rows:
            return apology("Try again")
        cash = rows[0]["cash"]
        new_amount = cash + amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_amount, user_id)
        flash("Amount Added Successfully!")
        return redirect("/")
