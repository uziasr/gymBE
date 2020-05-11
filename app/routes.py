from app import app, db
from app.models import User, Muscle, Exercise, Workout, Sets, Workout_Muscle, Workout_Exercise
from flask import request
from datetime import datetime

sample_data = ['bill', 'is', 'the', 'best']
major_muscle_group = ['Quadriceps', 'Hamstrings', 'Calves', 'Chest', 'Back', 'Shoulders', 'Triceps', 'Biceps',
                      'Forearms', 'Trapezius', 'Abs']
@app.route('/')
def hello_world():
    return 'Hello World!'


# prime example of taking in parameters from url
@app.route('/<name>')
def hello_name(name):
    return 'Hello {}'.format(name)


@app.route('/hidden')
def message():
    return " ".join(sample_data)

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
            new_wm = Workout_Muscle(workout_id=new_workout.id, muscle_group_id=current_muscle.id)
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

@app.route('/workout/<id>/set', methods=['POST'])
def add_exercise(id):
    # exercise is coming in as a string and should be looked up in table
    # id should either be passed through url or through json
    new_exercise = request.get_json()
    exercise_id = Exercise.query.filter_by(name=new_exercise["exercise"]).first().id
    new_workout_exercise = Workout_Exercise(workout_id=id, exercise_id=exercise_id, order=new_exercise["order"])
    db.session.add(new_workout_exercise)
    db.session.commit()
    return {
        "id": new_workout_exercise.id,
        "exercise": new_exercise["exercise"],
        "order": new_exercise["order"]
    }

@app.route('/set', methods=['POST'])
def add_set():
    req = request.get_json()
    new_set = Sets(repetition=req["repetition"], set_order=req["set_order"], weight=req["weight"], unit=req["weight"])
    db.session.add(new_set)
    db.session.add(new_set)
    return new_set
