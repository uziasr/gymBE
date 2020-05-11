from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    workouts = db.relationship('Workout', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}' {self.name}','{self.email}')"


class Muscle(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    exercises = db.relationship('Exercise', backref='exercises', lazy=True)

    def __repr__(self):
        return f"Muscle({self.id}, '{self.name}')"


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    muscle_id = db.Column(db.Integer, db.ForeignKey('muscle.id'), nullable=False)


    def __repr__(self):
        return f"Exercise('{self.name}')"

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    workout_exercise = db.relationship('Workout_Exercise', backref='workout_exercise', lazy=True)


    def __repr__(self):
        return f"Workout({self.id}, user_id: {self.user_id}, {self.start_time})"

class Sets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repetition = db.Column(db.Integer, nullable=False)
    set_order = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(15), nullable=False, default='lbs')


    def __repr__(self):
        return f"Sets({self.id}, weight: {self.weight}, repetition: {self.repetition}, exercise_order: {self.exercise_order}, order: {self.order})"

class Workout_Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

class Workout_Muscle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    muscle_group_id = db.Column(db.Integer, db.ForeignKey('muscle.id'), nullable=False)

    def __repr__(self):
        return f"Workout_Muscle(id: {self.id}, workout_id: {self.workout_id}, muscle_group_id: {self.muscle_group_id})"
