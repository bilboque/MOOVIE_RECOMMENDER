from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector  # this works
from flask_login import login_required
from flask import (Flask, jsonify, render_template, request, session, redirect,
                   url_for, flash)

app = Flask(__name__)


def get_session_key():
    try:
        with open('sessionkey.txt', 'r') as file:
            my_super_secret_key = file.readline().strip()
        return my_super_secret_key
    except FileNotFoundError:
        return None


app.secret_key = get_session_key()  # secret key for session management


def read_db_password():
    try:
        with open('password.txt', 'r') as file:
            password = file.readline().strip()  # Assuming password is stored in a single line
        return password
    except FileNotFoundError:
        return None


# create db connection
connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=read_db_password(),
    database="DBMi"  # db name to access
)


cursor = connection.cursor()


@app.route("/")  # this will become the main page with movies displayed
def index():
    return render_template('app.html')


@app.route("/register", methods=["GET", "POST"])  # route for creating account
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            # Store the username and hashed password in the database
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)", (
                        username, generate_password_hash(password))
                )
                connection.commit()
            except connection.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

            flash(error)

        return render_template('auth/register.html')


@app.route("/login", methods=["POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = cursor.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@ app.route("/about/")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


# route for displaying test data
@ app.route("/movies/", methods=['GET'])
def movies():
    mysql_query = """ SHOW TABLES;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return jsonify(output)
    # return str(output)


@ app.route("/api/movies/", methods=['GET'])
def getMovies():
    mysql_query = """SHOW TABLES;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return jsonify(output)


# view movie details
@ app.route("/api/movies/<int:movie_id>", methods=['GET'])
def getMovieDetails(movie_id):
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    if movie:
        return jsonify(movie), 200
    else:
        return jsonify({"error": "Movie not found"}), 404


@ app.route('/api/search', methods=['GET'])  # search for a movie
def search_movie():
    query = request.args.get('query')
    cursor.execute("SELECT * FROM movies WHERE title LIKE %s",
                   ('%' + query + '%',))
    movies = cursor.fetchall()
    if movies:
        return jsonify(movies), 200
    else:
        return jsonify({"message": "No movies found"}), 404


# Watchlist route
@ app.route('/watchlist', methods=['GET'])
@ login_required  # decorator to ensure that only authenticated users can access the route
def view_watchlist():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['user_id']

    cursor.execute(
        "SELECT * watchlist where id = %s", (user_id))
    watchlist = cursor.fetchall()

    if watchlist:
        return jsonify(watchlist), 200
    else:
        return jsonify({"message": "Watchlist is empty"}), 404


if __name__ == '__main__':
    app.run(debug=True)
