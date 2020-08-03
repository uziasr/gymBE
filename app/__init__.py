from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_hashing import Hashing
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from app.config import Config


db = SQLAlchemy()
hashing = Hashing()  # Change this!
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # app.debug = True

    from app.users.routes import user
    from app.workouts.routes import workouts
    from app.saved_workout.routes import saved
    from app.exercises.routes import exercises

    app.register_blueprint(user)
    app.register_blueprint(workouts)
    app.register_blueprint(saved)
    app.register_blueprint(exercises)

    db.init_app(app)
    hashing.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app=app, db=db)

    # with app.app_context():
    #     db.create_all()

    return app


def jsonify_object(instance, cls, remove_keys=[]):
    return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns if i.key not in remove_keys}


def one_rep_max(a_set):
    # come back and check if the unit of weight is pounds or kilograms
    return a_set.weight * a_set.repetition * .033 + a_set.weight


