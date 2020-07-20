from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    workouts = db.relationship('Workout', backref='user', lazy=True, cascade="delete")

    def __repr__(self):
        return f"User('{self.id}' '{self.name}','{self.email}')"


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
        return f"Exercise({self.id} '{self.name}')"


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    workout_exercise = db.relationship('WorkoutExercise', backref='workout_exercise', lazy=True, cascade="delete")
    muscles = db.relationship('WorkoutMuscle', backref='workout_muscle', lazy=True, cascade="delete")

    def __repr__(self):
        return f"Workout({self.id}, user_id: {self.user_id}, {self.start_time})"


class Sets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repetition = db.Column(db.Integer, nullable=False)
    set_order = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(15), nullable=False, default='lbs')
    workout_exercise_id = db.Column(db.Integer, db.ForeignKey('workout_exercise.id'), nullable=False)

    def __repr__(self):
        return f"Sets({self.id}, weight: {self.weight}, repetition: {self.repetition}, order: {self.set_order})"


class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    sets = db.relationship('Sets', backref='sets', lazy=True, cascade="delete")

    def __repr__(self):
        return f"WorkoutExercise({self.id}, workout_id: {self.workout_id}, exercise_id: {self.exercise_id}, order:{self.order})"


class WorkoutMuscle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    muscle_group_id = db.Column(db.Integer, db.ForeignKey('muscle.id'), nullable=False)

    def __repr__(self):
        # return f"WorkoutMuscle(id: {self.id}, workout_id: {self.workout_id}, muscle_group_id: {self.muscle_group_id})"
        return f"{Muscle.query.get(self.muscle_group_id).name}"


class SavedWorkout(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"SavedWorkout({self.id}, name: {self.name}, user_id: {self.user_id}, author_id: {self.author_id})"


class Schedule(db.Model):
    id = db.Column(db.integer, primary_key=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    saved_workout_id = db.Column(db.Integer, db.ForeignKey('SavedWorkout.id'), nullable=False)

    def __repr__(self):
        return f"Schedule({self.id}, date: {self.date}, user_id:P {self.user_id}, saved_workout_id: {self.saved_workout_id})"


class SavedWorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"SavedWorkoutExercise({self.id}, exercise_id: {self.exercise_id}, order: {self.order})"


class SavedWorkoutMuscle(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    saved_workout_id = db.Column(db.Integer, db.ForeignKey('saved_workout.id'), nullable=False)
    muscle_id = db.Column(db.Integer, db.ForeignKey("muscle.id"), nullable=False)

    def __repr__(self):
        return f"SavedWorkoutMuscle({self.id}, saved_workout_id: {self.saved_workout_id}, muscle_id: {self.muscle_id})"

