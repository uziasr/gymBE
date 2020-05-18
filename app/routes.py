from app import app, db
from app.models import User, Muscle, Exercise, Workout, Sets, WorkoutMuscle, WorkoutExercise
from flask import request, jsonify, Response
from datetime import datetime

def jsonify_object(instance, cls, remove_keys=[]):
    return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns if i.key not in remove_keys}

def one_rep_max(a_set):
    return a_set.weight * a_set.repetition * .033 + a_set.weight

@app.route('/')
def hello_world():
    return jsonify(["hello","there"])


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

@app.route('/workout/<id>/end')
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

@app.route('/workout/<id>/set')
def get_full_workout(id):
    # where id comes from WorkoutExercise
    exercise_list = WorkoutExercise.query.filter_by(workout_id=id).all()
    # grab the primary key here and query sets to get all the additional info
    complete_workout= []
    for exercise in exercise_list:
        set_list = Sets.query.filter_by(workout_exercise_id=exercise.id).all()
        exercise_name = Exercise.query.get(exercise.id).name
        exercise_sets = {
            "exercise": exercise_name,
            "order": exercise.order,
            "sets": [jsonify_object(sets, Sets, ['workout_exercise_id']) for sets in set_list]
        }
        complete_workout.append(exercise_sets)
    return jsonify(complete_workout)

@app.route('/workout/exercise/<id>')
def get_sets_for_workout(id):
    # where id comes from WorkoutExercise
    exercise = Exercise.query.get(WorkoutExercise.query.get(id).exercise_id).name
    set_list = Sets.query.filter_by(workout_exercise_id=id).all()
    # grab the primary key here and query sets to get all the additional info
    # for exercise in exercise_list:
    #     #     exercise_sets = Sets.query.filter_by(workout_exercise_id=exercise.id).all()
    #     # Sets.query.filter_by()
    return {
        "exercise": exercise,
        "sets": [jsonify_object(sets, Sets, ['workout_exercise_id']) for sets in set_list]
    }
@app.route('/workout/exercise')
def get_all_exercises():
    exercises = Exercise.query.all()
    return jsonify([e.name for e in exercises])

@app.route('/workout/<id>/exercise/<exercise_id>', methods=['DELETE'])
def delete_exercise(id, exercise_id):
    deleted_exercise = WorkoutExercise.query.get(exercise_id)
    deleted_exercise_dict = jsonify_object(deleted_exercise, WorkoutExercise)
    deleted_exercise.delete()
    return {
        "message": "successful",
        "exercise": deleted_exercise_dict
    }

@app.route('/sets/<set_id>', methods=['DELETE'])
def delete_set(set_id):
    deleted_set = Sets.query.get(set_id)
    delete_set_dict = jsonify_object(delete_set, Sets)
    deleted_set.delete()
    return {
        "message":" successful",
        "set": delete_set_dict
    }

@app.route('/user/<id>/exercise')
def user_exercise_list(id):
    my_workouts = Workout.query.filter_by(user_id=id).all()
    all_my_workout_exercises = [WorkoutExercise.query.get(workout.id) for workout in my_workouts if workout]
    all_my_exercises = [jsonify_object(Exercise.query.filter_by(id=e.exercise_id).first(), Exercise) for e in all_my_workout_exercises if e]
    return jsonify(all_my_exercises)

@app.route('/user/<id>/exercise/<e_id>')
def user_exercise_stats(id, e_id):


    my_workouts = Workout.query.filter_by(user_id=id).all()
    all_my_workout_exercises = [WorkoutExercise.query.get(workout.id) for workout in my_workouts]

    filtered_by_exercise = filter(lambda x: x and x.exercise_id == int(e_id), all_my_workout_exercises)

    all_sets = []
    for exercise in filtered_by_exercise:
        all_sets = [*all_sets, *exercise.sets]
    max_rep, max_weight, max_combination, max_one_rep, max_one_rep_set = all_sets[0], all_sets[0], all_sets[0], one_rep_max(all_sets[0]), all_sets[0]
    count, sum_weight, sum_reps = 0,0,0

    for current_set in all_sets:
        if current_set.weight > max_weight.weight: max_weight = current_set
        if current_set.weight == max_weight.weight:
            if current_set.repetition > max_weight.repetition:
                max_weight = current_set
        if current_set.repetition > max_rep.repetition: max_rep = current_set
        if current_set.repetition == max_rep.repetition:
            if current_set.weight > max_rep.weight:
                max_rep = current_set
        if one_rep_max(current_set) >= one_rep_max(max_one_rep_set):
            max_one_rep_set = current_set
        count += 1
        sum_weight += current_set.weight
        sum_reps += current_set.repetition

    return jsonify({
        "max_weight": jsonify_object(max_weight, Sets),
        "max_reps": jsonify_object(max_rep, Sets),
        "average_reps": sum_reps/count,
        "average_weight": sum_weight/count,
        "total_sets": count
    })

