import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from random import choices

from helpers import apology, login_required, get_token, get_auth_header, get_songs_by_artist, search_for_artist

#load client variables
from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token = get_token(client_id, client_secret)

song_list = []

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")

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
    songs = db.execute("SELECT * FROM distribution WHERE user = ?", session["user_id"])
    print(token)
    return render_template("index.html", songs=songs)



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

@app.route("/add song", methods=["GET", "POST"])
@login_required
def addsong():
    if request.method == "POST":

        #Song name variable
        song = request.form.get("song")

        #checks if input has been provided
        if not song:
            return apology("Must provide song", 400)

        #Checks the song is not in db
        rows = db.execute("SELECT * FROM distribution WHERE song = ? AND user = ?", song, session["user_id"])
        if len(rows) != 0:
            return apology("Song already in list", 400)

        #inserts song
        db.execute("INSERT INTO distribution (user, song, probability) VALUES(?, ?, ?)", session["user_id"], song, 0)

        return redirect("/add song")
    else:
        return render_template("add_song.html")

@app.route("/reset", methods=["POST"])
@login_required
def reset():
    song_count = db.execute("SELECT COUNT(song) FROM distribution WHERE user = ?", session["user_id"])
    song_count = song_count[0]['COUNT(song)']
    prob = 1/song_count

    #updates prob
    db.execute("UPDATE distribution SET probability = ? WHERE user = ?", prob, session["user_id"])

    return redirect("/")


@app.route("/spotify", methods=["POST", "GET"])
@login_required
def spotify():
    global song_list
    if request.method == "POST":

        #Song name variable
        artist = request.form.get("artist")

        if not artist:
            return apology("Must provide Artist", 400)

        if get_songs_by_artist(token, artist) == None:
            return apology("Incorrect Artist Name", 400)

        songs = get_songs_by_artist(token, artist)
        song_list = []
        for song in songs:
            song_list.append(song['name'])

        return render_template("confirm_songs.html", songs=song_list, artist=artist)
    else:

        return render_template("spotify.html", songs="none")

@app.route("/confirm", methods=["POST"])
@login_required
def confirm():
    global song_list
    if request.method == "POST":
        for song in song_list:
            try:
                db.execute("INSERT INTO distribution (user, song, probability) VALUES(?, ?, ?)", session["user_id"], song, 0)
            except:
                pass
        return redirect("/")

@app.route("/dump", methods=["POST"])
@login_required
def dump():
    if request.method == "POST":
        db.execute("DELETE FROM distribution WHERE user = ?", session["user_id"])
        return redirect("/")


@app.route("/random", methods=["POST", "GET"])
@login_required
def random():
    if request.method == "POST":
        songs = {}

        #loads probabilities into a dict
        song_count = db.execute("SELECT COUNT(song) FROM distribution WHERE user = ?", session["user_id"])
        song_count = song_count[0]['COUNT(song)']
        songs_database = db.execute("SELECT song, probability FROM distribution WHERE user = ?", session["user_id"])
        for i in range(len(songs_database)):
            songs[songs_database[i]['song']] = songs_database[i]['probability']

        #random song
        random_song = choices(list(songs), songs.values())

        #redistributes probabilties
        increase = songs[random_song[0]]/(song_count-1)
        db.execute("UPDATE distribution SET probability = probability + ? WHERE user = ?", increase, session["user_id"])
        db.execute("UPDATE distribution SET probability = 0 WHERE user = ? AND song = ?", session["user_id"], random_song[0])

        return render_template("random.html", song=random_song[0])
    else:
        return render_template("random.html", song="NA")

@app.route("/about")
@login_required
def about():
    return render_template("about.html")