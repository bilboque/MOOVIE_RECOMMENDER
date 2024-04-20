from flask import Flask
from auth import auth_bp
from db import db_blueprint
from routes import routes_bp
from api_routes import api_bp

temp_app = Flask(__name__)
temp_app.register_blueprint(auth_bp)
temp_app.register_blueprint(db_blueprint)
temp_app.register_blueprint(routes_bp)
temp_app.register_blueprint(api_bp)


def get_session_key():
    try:
        with open('sessionkey.txt', 'r') as file:
            my_super_secret_key = file.readline().strip()
        return my_super_secret_key
    except FileNotFoundError:
        return None


temp_app.secret_key = get_session_key()  # secret key for session management

if __name__ == '__main__':
    temp_app.run(debug=True)
