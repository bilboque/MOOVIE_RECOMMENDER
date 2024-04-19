from flask import Flask, jsonify, render_template, request, session
import hashlib
import mysql.connector  # this works

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


def authenticate_user(username, password):
    cursor.execute(
        "SELECT password FROM users WHERE username = %s", (username))
    result = cursor.fetchone()

    if result:
        # Assuming password is stored in the first column
        hashed_password = result[0]
        if verify_password(password, hashed_password):
            return True  # Authentication successful
    return False  # Authentication failed


@app.route("/create", methods=["POST"])  # route for creating account
def createAccount():
    username = request.json.get('username')
    password = request.json.get('password')

    # Hash the password
    hashed_password = hash_password(password)

    # Store the username and hashed password in the database
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        if cursor.rowcount == 1:
            return jsonify({"message": "Account created successfully"}), 201
        else:
            return jsonify({"error": "Failed to create account"}), 500
    except mysql.connector.Error as err:
        return jsonify({"error": f"Failed to create account: {err}"}), 500


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if authenticate_user(username, password):  # perform authentication check
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


def hash_password(password):  # function to hash password
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password, hashed_password):  # Function to verify a password
    return hashed_password == hash_password(password)


@app.route("/about/")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


# route for displaying test data
@app.route("/movies/", methods=['GET'])
def movies():
    mysql_query = """ SHOW TABLES;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return jsonify(output)
    # return str(output)


@app.route("/api/movies/", methods=['GET'])
def getMovies():
    mysql_query = """SHOW TABLES;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return jsonify(output)


@app.route("/api/movies/<int:movie_id>", methods=['GET'])  # view movie details
def getMovieDetails(movie_id):
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    if movie:
        return jsonify(movie), 200
    else:
        return jsonify({"error": "Movie not found"}), 404


@app.route('/api/search', methods=['GET'])  # search for a movie
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
@app.route('/watchlist', methods=['GET'])
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
