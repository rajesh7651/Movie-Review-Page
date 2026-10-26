
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set a secret key using an environment variable in production.
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "change-this-development-key"
)

DATABASE = "movie_review.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create the database and users table
def create_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Registration page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirmPassword", "")

        if not name or not email or not password:
            return "All fields are required.", 400

        if len(password) < 6:
            return "Password must contain at least 6 characters.", 400

        if password != confirm:
            return "Passwords do not match.", 400

        hashed_password = generate_password_hash(password)

        try:
            with get_db() as db:
                db.execute(
                    """
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                    """,
                    (name, email, hashed_password)
                )
        except sqlite3.IntegrityError:
            return "This email is already registered.", 409

        return redirect(url_for("signin"))

    return render_template("signup.html")


# Sign-in page
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("dashboard"))

        return "Invalid email or password.", 401

    return render_template("signin.html")


# Protected page after successful login
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    return f"""
        <h1>Welcome, {session['user_name']}!</h1>
        <p>You are signed in to MovieFlix.</p>
        <a href="/logout">Sign Out</a>
    """


# Sign out
@app.route("/")
def home():
    return render_template(
        "index.html",
        user_name=session.get("user_name")
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
