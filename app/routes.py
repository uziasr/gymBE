from app import app, db
from app.models import User, Muscle, Exercise, Workout, Sets, WorkoutMuscle, WorkoutExercise
from flask import request
from datetime import datetime

def jsonify_object(instance, cls):
    return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns}


@app.route('/')
def hello_world():
    return {"message" : ['hello','there']}


# prime example of taking in parameters from url

@app.route('/muscles')
def get_muscles():
    muscles = Muscle.query.all()
    muscles_list = [muscle.name for muscle in muscles]
    return " ".join(muscles_list)

@app.route('/user', methods=['POST'])
def create_user():
    user_info = request.get_json()
    db.session.add(User(name=user_info['name'], email=user_info['email'], password=user_info['password']))
    db.session.commit()

@app.route('/workout/<id>', methods=['POST'])
def start_workout(id):
    # id will belong to the user
    new_workout = Workout(user_id=id)
    db.session.add(new_workout)
    db.session.commit()
    # for now, support only explicit muscles and not muscle groups
    print(new_workout)
    muscles_getting_trained = request.get_json()["muscles"]
    if new_workout.id:
        for muscle in muscles_getting_trained:
            current_muscle = Muscle.query.filter_by(name=muscle).first()
            print(current_muscle, current_muscle.id, new_workout.id)
            new_wm = WorkoutMuscle(workout_id=new_workout.id, muscle_group_id=current_muscle.id)
            db.session.add(new_wm)
        db.session.commit()
    return {"message":"workout created"}

@app.route('/endWorkout/<id>')
def end_workout(id):
    # id here can be the id of the user of it can be the id of the workout
    # if the former is selected, a query will need to be run to get the users workouts
    # and chose the most recent one
    # for now the id will belong to the workout
    current_workout = Workout.query.get(id)
    current_workout.end_time = datetime.utcnow()
    db.session.commit()
    return {
        "id" : current_workout.id,
        "user_id" : current_workout.user_id,
        "start_time" : current_workout.start_time,
        "end_time" : current_workout.end_time}

@app.route('/workout/<id>/exercise', methods=['POST'])
def add_exercise(id):
    # exercise is coming in as a string and should be looked up in table
    # id should either be passed through url or through json
    new_exercise = request.get_json()
    exercise_id = Exercise.query.filter_by(name=new_exercise["exercise"]).first().id
    new_workout_exercise = WorkoutExercise(workout_id=id, exercise_id=exercise_id, order=new_exercise["order"])
    db.session.add(new_workout_exercise)
    db.session.commit()
    return {
        "id": new_workout_exercise.id,
        "exercise": new_exercise["exercise"],
        "order": new_exercise["order"]
    }

@app.route('/workout/<id>/set', methods=['POST'])
def add_set(id):
    req = request.get_json()
    new_set = Sets(repetition=req["repetition"], set_order=req["set_order"], weight=req["weight"], unit=req["unit"], workout_exercise_id=id)
    db.session.add(new_set)
    db.session.commit()
    return jsonify_object(instance=new_set, cls=Sets)

@app.route('/workout/<id>')
def get_workout(id):
    # exercise_list = WorkoutExercise.query.get(id)
    my_workout = WorkoutExercise.query.filter_by(workout_id=id).all()
    my_workout.sort(key=lambda exercise: exercise.order)
    exercise_list = [Exercise.query.get(i.exercise_id).name for i in my_workout]
    return {
        "exercises": exercise_list
    }

