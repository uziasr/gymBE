from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_hashing import Hashing

app = Flask(__name__)
hashing = Hashing(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_pal.db'
db = SQLAlchemy(app)

from app import routes
