# from flask_login import login_required
from flask import Flask
from auth import auth_bp
from db import db_blueprint
from routes import routes_bp

temp_app = Flask(__name__)
temp_app.register_blueprint(auth_bp)
temp_app.register_blueprint(db_blueprint)
temp_app.register_blueprint(routes_bp)


if __name__ == '__main__':
    temp_app.run(debug=True)
