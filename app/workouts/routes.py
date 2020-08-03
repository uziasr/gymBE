from flask import Blueprint, request, jsonify
from app import jwt_required, get_jwt_identity, db, jsonify_object
from app.models import *
from datetime import datetime, timedelta

workouts = Blueprint('workouts', __name__, url_prefix='/workout')


@workouts.route('/', methods=['POST'])
@jwt_required
def start_workout():
    # id will belong to the user
    id = get_jwt_identity()
    new_workout = Workout(user_id=id)
    db.session.add(new_workout)
    db.session.commit()
    # for now, support only explicit muscles and not muscle groups
    muscles_getting_trained = request.get_json()["muscles"]
    if new_workout.id:
        for muscle in muscles_getting_trained:
            current_muscle = Muscle.query.filter_by(name=muscle).first()
            new_wm = WorkoutMuscle(workout_id=new_workout.id, muscle_group_id=current_muscle.id)
            db.session.add(new_wm)
        db.session.commit()
    return {"id": new_workout.id}, 201


@workouts.route('/workout/<int:id>/complete')
def end_workout(id):
    # id here can be the id of the user of it can be the id of the workout
    # if the former is selected, a query will need to be run to get the users workouts
    # and chose the most recent one
    # for now the id will belong to the workout
    current_workout = Workout.query.get(id)
    if not current_workout:
        return {"message": "workout does not exist"}, 400
    if current_workout.end_time:
        return {"message": "workout already finished"}, 400
    current_workout.end_time = datetime.utcnow()
    db.session.commit()
    return {
        "id" : current_workout.id,
        "user_id" : current_workout.user_id,
        "start_time" : current_workout.start_time,
        "end_time" : current_workout.end_time}


@workouts.route('/workout/<int:id>/exercise', methods=['POST'])
def add_exercise(id):
    new_exercise = request.get_json()
    all_exercises_in_workout = WorkoutExercise.query.filter_by(workout_id=id).order_by(WorkoutExercise.order).all()

    if len(all_exercises_in_workout):
        latest_exercise = all_exercises_in_workout[-1]
        if len(latest_exercise.sets) == 0:
            db.session.delete(latest_exercise)
            db.session.commit()

    exercise_id = Exercise.query.filter_by(name=new_exercise["exercise"]).first().id
    order = len(Workout.query.get(id).workout_exercise) + 1
    new_workout_exercise = WorkoutExercise(workout_id=id, exercise_id=exercise_id, order=order)
    db.session.add(new_workout_exercise)
    db.session.commit()
    return {
        "id": new_workout_exercise.id,
        "exercise": new_exercise["exercise"],
    }, 201