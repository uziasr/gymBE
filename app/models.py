from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    workouts = db.relationship('Workout', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.name}','{self.email}')"


class Muscle(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    exercises = db.relationship('Exercise', backref='exercises', lazy=True)

    def __repr__(self):
        return f"Muscle_Group({self.id}, '{self.name}')"


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    muscle_id = db.Column(db.Integer, db.ForeignKey('muscle.id'), nullable=False)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    muscle_group_id = db.Column(db.Integer, db.ForeignKey('muscle.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    muscle_group = db.relationship('Muscle', backref='muscle_group', lazy=True)


class Sets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    repetition = db.Column(db.Integer, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    exercise_order = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(15), nullable=False, default='lbs')