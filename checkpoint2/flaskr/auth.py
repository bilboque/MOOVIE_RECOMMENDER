from werkzeug.security import check_password_hash, generate_password_hash
from flask import (Blueprint, render_template, request, session, redirect,
                   url_for, flash)
from db import get_db_connection
import mysql.connector

auth_bp = Blueprint('auth', __name__)

connection = get_db_connection()
cursor = connection.cursor()


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                cursor.execute(
                    "INSERT INTO user (pseudo, mot_de_passe) VALUES (%s, %s)",
                    (username, generate_password_hash(password)),
                )
                connection.commit()
            except mysql.connector.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        try:
            cursor.execute(
                "SELECT * FROM user WHERE pseudo = %s", (username,)
            )
            user = cursor.fetchone()
        except Exception as e:
            print("Error executing SQL query:", e)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[3], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('routes.index'))

        flash(error)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('user_id', None)
    return redirect(url_for('routes.index'))
