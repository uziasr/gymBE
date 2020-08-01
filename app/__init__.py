from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_hashing import Hashing
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)

ENV = "dev"

if ENV == "dev":
    pass
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5433/gym'
    app.config['JWT_SECRET_KEY'] = 'super-secret'
    app.debug = True
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
hashing = Hashing(app)  # Change this!
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
