from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_hashing import Hashing
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)



db = SQLAlchemy()
hashing = Hashing()  # Change this!
jwt = JWTManager()
migrate = Migrate()

def create_app():
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


    from app.users.routes import user
    app.register_blueprint(user)
    db.init_app(app)
    hashing.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app=app, db=db)
    return app

def jsonify_object(instance, cls, remove_keys=[]):
    return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns if i.key not in remove_keys}

# from app import routes
