from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_hashing import Hashing
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)
hashing = Hashing(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_pal.db'
db = SQLAlchemy(app)

from app import routes
