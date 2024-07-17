import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime as date

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    portfolio = db.execute("SELECT * FROM portfolio WHERE id = ?", session["user_id"])
    total = db.execute("SELECT sum(total) FROM portfolio WHERE id = ?", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    if len(portfolio) != 0:
        print('es')
        cash = cash[0]['cash']
        total = total[0]['sum(total)'] + cash
    else:
        cash = cash[0]['cash']
        total = cash
    return render_template("index.html", portfolio=portfolio, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":

        #Checks correct input
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide symbol", 400)
        try:
            if int(request.form.get("shares")) < 0:
                return apology("must enter 1 or above", 400)
        except:
            return apology("Must enter numeric stock number", 400)


        #Fetches stock data
        data = lookup(request.form.get("symbol"))
        if data == None:
            return apology("Must enter vaild stock",400)

        #create variables
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = cash[0]['cash']
        total_price = data['price']*float(request.form.get("shares"))

        #checks price
        if total_price > cash:
            return apology("Attemting to purchase to many shares", 400)

        rows = db.execute("SELECT * FROM portfolio WHERE id = ? AND symbol = ?", session["user_id"], data['symbol'])
        time = date.datetime.now()
        if len(rows) == 0:
            #inserts new stock data
            db.execute("INSERT INTO portfolio (id, symbol, name, shares, price, total) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], data['symbol'], data['name'], int(request.form.get("shares")), data['price'],total_price)
            db.execute("INSERT INTO transactions (id, symbol, shares, price, transacted) VALUES(?,?,?,?,?)", session["user_id"], data['symbol'], int(request.form.get("shares")), data['price'], time)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash-total_price, session["user_id"])
        else:
            #update old data
            total_price = rows[0]['total'] + total_price
            new_shares = rows[0]['shares'] + int(request.form.get("shares"))
            new_price = total_price/new_shares
            db.execute("UPDATE portfolio SET shares = ?, price = ?, total = ? WHERE id = ? AND symbol = ?", new_shares, new_price, total_price, session["user_id"], data['symbol'])
            db.execute("INSERT INTO transactions (id, symbol, shares, price, transacted) VALUES(?,?,?,?,?)", session["user_id"], data['symbol'], int(request.form.get("shares")), data['price'], time)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash-total_price, session["user_id"])

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    transactions = db.execute("SELECT * FROM transactions WHERE id = ?", session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 4003)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
    if request.method == 'POST':

        if not request.form.get("symbol"):
            return apology("must provide stock symbol", 400)

        data = lookup(request.form.get("symbol"))
        if data == None:
            return apology("Must enter vaild stock",400)

        return render_template("quoted.html", name=data['name'], symbol=data['symbol'], price=usd(data['price']))
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == 'POST':

        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if password != confirm:
            return apology("Password does not match")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 0:
            return apology("Username already exists", 400)

        password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password)

        #Creates sesion
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":

        #Checks correct input
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide symbol", 400)
        if float(request.form.get("shares")) < 1:
            return apology("must enter 1 or above", 400)

        #Fetches stock data
        data = lookup(request.form.get("symbol"))
        if data == None:
            return apology("Must enter vaild stock",400)

        portfolio = db.execute("SELECT * FROM portfolio WHERE id = ? AND symbol = ?", session["user_id"], data['symbol'])
        #checks shares are not over current shares
        if int(request.form.get("shares")) > portfolio[0]['shares']:
            return apology("Trying to sell to many shares", 400)

        #Fetches stock data
        data = lookup(request.form.get("symbol"))
        if data == None:
            return apology("Must enter vaild stock",400)

        if int(request.form.get("shares")) < portfolio[0]['shares']:
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", data['price']*float(request.form.get("shares")), session["user_id"])
            db.execute("UPDATE portfolio SET shares = shares - ?, total = total - ? WHERE id = ? AND symbol = ?", int(request.form.get("shares")), data['price']*int(request.form.get("shares")), session["user_id"], data['symbol'])
            time = date.datetime.now()
            db.execute("INSERT INTO transactions (id, symbol, shares, price, transacted) VALUES(?,?,?,?,?)", session["user_id"], data['symbol'], -int(request.form.get("shares")), data['price'], time)
        else:
            print(data['price']*float(request.form.get("shares")))
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", data['price']*float(request.form.get("shares")), session["user_id"])
            db.execute("DELETE FROM portfolio WHERE id = ? AND symbol = ?", session["user_id"], data['symbol'])
            time = date.datetime.now()
            db.execute("INSERT INTO transactions (id, symbol, shares, price, transacted) VALUES(?,?,?,?,?)", session["user_id"], data['symbol'], -int(request.form.get("shares")), data['price'], time)
        return redirect("/")
    else:
        portfolio = db.execute("SELECT * FROM portfolio WHERE id = ?", session["user_id"])
        if len(portfolio) == 0:
            return apology("No stocks to sell", 400)
        return render_template("sell.html", portfolio=portfolio)
