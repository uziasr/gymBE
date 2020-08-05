from flask import Blueprint, request, jsonify
from app import jwt_required, get_jwt_identity, db
from app.models import *
from datetime import datetime, timedelta
from app.utils import jsonify_object, one_rep_max, date_formatter

workouts = Blueprint('workouts', __name__, url_prefix='/workout')


@workouts.route('', methods=['POST'])
@jwt_required
def start_workout():
    # id will belong to the user
    id = get_jwt_identity()
    req = request.get_json()
    print("this is req", req)
    if "template_id" in req:
        new_workout = Workout(user_id=id, template_id=req["template_id"])
    else:
        new_workout = Workout(user_id=id)
    db.session.add(new_workout)
    db.session.commit()
    # for now, support only explicit muscles and not muscle groups
    muscles_getting_trained = req["muscles"]
    if new_workout.id:
        for muscle in muscles_getting_trained:
            current_muscle = Muscle.query.filter_by(name=muscle).first()
            new_wm = WorkoutMuscle(workout_id=new_workout.id, muscle_group_id=current_muscle.id)
            db.session.add(new_wm)
        db.session.commit()
    if "exercise" in req:
        exercise_id = Exercise.query.filter_by(name=req["exercise"]).first().id
        new_workout_exercise = WorkoutExercise(workout_id=new_workout.id, exercise_id=exercise_id, order=1)
        db.session.add(new_workout_exercise)
        db.session.commit()
    return {"id": new_workout.id}, 201


@workouts.route('/<int:id>/complete')
@jwt_required
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


@workouts.route('/<int:id>/exercise', methods=['POST'])
@jwt_required
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


@workouts.route('/<int:workout_exercise_id>/exercise', methods=['PATCH'])
@jwt_required
def complete_exercise(workout_exercise_id):
    completed_exercise = WorkoutExercise.query.get(workout_exercise_id)
    completed_exercise.completed = True
    db.session.commit()
    return {
        "success": "updated successfully"
    }, 204


@workouts.route('/exercise/<int:id>/set', methods=['POST', 'PATCH'])
@jwt_required
def manage_set(id):
    # for adding new sets and updating sets
    req = request.get_json()
    current_workout_exercise = WorkoutExercise.query.get(id)
    if request.method == 'POST':
        order = len(current_workout_exercise.sets) + 1
        new_set = Sets(repetition=req["repetition"], set_order=order, weight=req["weight"], unit=req["unit"], workout_exercise_id=id)
        db.session.add(new_set)
        db.session.commit()
        return jsonify_object(instance=new_set, cls=Sets), 201
    elif request.method == 'PATCH':
        current_set = Sets.query.get(req["id"])
        current_set.repetition, current_set.weight, current_set.unit = req["repetition"], req["weight"], req["unit"]
        db.session.commit()
        return jsonify_object(current_set, Sets)


@workouts.route('/exercise/<int:workout_exercise_id>/set/<int:set_id>', methods=['DELETE'])
@jwt_required
def delete_set(workout_exercise_id, set_id):
    current_workout_exercise = WorkoutExercise.query.get(workout_exercise_id)
    current_set = Sets.query.get(set_id)
    if not current_set:
        return {
            "error": "this set does not exist"
        }, 500
    for a_set in current_workout_exercise.sets:
        if current_set.set_order < a_set.set_order:
            a_set.set_order -= 1
            db.session.commit()
    db.session.delete(current_set)
    db.session.commit()
    return jsonify([jsonify_object(a_set, Sets) for a_set in WorkoutExercise.query.get(workout_exercise_id).sets])


@workouts.route('/<int:workout_id>/set')
@jwt_required
def get_full_workout(workout_id):
    user_id = get_jwt_identity()
    # where id comes from WorkoutExercise
    workout_exercise_list = WorkoutExercise.query.filter_by(workout_id=workout_id).all()
    if len(workout_exercise_list) == 0:
        return {
            "error": "this workout contains no exercises yet"
        }, 400
    # grab the primary key here and query sets to get all the additional info
    complete_workout = []
    for exercise in workout_exercise_list:
        set_list = Sets.query.filter_by(workout_exercise_id=exercise.id).all()
        exercise_name = Exercise.query.get(exercise.exercise_id).name
        all_workouts_with_exercise = WorkoutExercise.query.join(Workout).filter(Workout.user_id == user_id).filter(WorkoutExercise.exercise_id == exercise.exercise_id).all()
        exercise_sets = {
            "exercise": exercise_name,
            "muscle": Muscle.query.filter_by(id = Exercise.query.get(exercise.exercise_id).muscle_id).first().name,
            "order": exercise.order,
            "sets": [{**jsonify_object(sets, Sets), "max": one_rep_max(sets)} for sets in set_list],
            "previous_sets": []
        }
        if len(all_workouts_with_exercise) > 1:
            exercise_sets["previous_sets"] = [jsonify_object(sets, Sets) for sets in all_workouts_with_exercise[-2].sets][:len(set_list)]
        complete_workout.append(exercise_sets)
    return jsonify(complete_workout)


@workouts.route('/exercise/<int:id>')
@jwt_required
def get_sets_for_workout(id):
    exercise = Exercise.query.get(WorkoutExercise.query.get(id).exercise_id).name
    set_list = Sets.query.filter_by(workout_exercise_id=id).all()
    return {
        "exercise": exercise,
        "sets": [jsonify_object(sets, Sets, ['workout_exercise_id']) for sets in set_list]
    }


@workouts.route('/exercise/<int:workout_exercise_id>', methods=['DELETE'])
@jwt_required
def delete_exercise(workout_exercise_id):
    id = get_jwt_identity()
    deleted_exercise = WorkoutExercise.query.get(workout_exercise_id)
    workout = Workout.query.get(deleted_exercise.workout_id)
    if workout.user_id == id:
        deleted_exercise_dict = jsonify_object(deleted_exercise, WorkoutExercise)
        db.session.delete(deleted_exercise)
        db.session.commit()
        return {
            "message": "successful",
            "exercise": deleted_exercise_dict
        }
    else:
        return {
            "error": "you cannot delete this exercise"
        }, 204


@workouts.route('/date', methods=['POST'])
@jwt_required
def get_workout_by_date():
    id = get_jwt_identity()
    date = request.get_json()['date'] # format will be 2020-05-11
    year, month, day = date.split('-')
    formatted_date = datetime(int(year), int(month), int(day))
    all_workouts = Workout.query.filter_by(user_id = id).filter(Workout.end_time !=None).all()
    all_workouts_by_date = []
    for a_workout in all_workouts:
        if a_workout.start_time.date() == formatted_date.date():
            all_workouts_by_date.append({**jsonify_object(a_workout, Workout),
                                 'total_time':(a_workout.end_time - a_workout.start_time).total_seconds(),
                                 "muscles": (f"{a_workout.muscles}"[1:-1]).split(',')
                                 })
    return jsonify(all_workouts_by_date)


@workouts.route('/all')
@jwt_required
def get_all_workouts():
    user_id = get_jwt_identity()
    my_workouts = Workout.query.filter_by(user_id=user_id).filter(Workout.end_time!=None).all()
    return jsonify([jsonify_object(workout, Workout) for workout in my_workouts])


# @workouts.route('/workouts/<id>')
# def get_users_workout_by_id(id):
#     workout_dict = {}
#     for index, exercise in enumerate(Workout.query.get(2).workout_exercise):
#         current_exercise = Exercise.query.get(WorkoutExercise.exercise_id).name
#         if current_exercise not in workout_dict:
#             workout_dict[current_exercise] = [jsonify_object(current_set, Sets) for current_set in exercise.sets]
#         else:
#             workout_dict[f"{current_exercise}-{index}"] = [jsonify_object(current_set, Sets) for current_set in exercise.sets]
#
#     return jsonify(workout_dict)


@workouts.route("/startup")
@jwt_required
def get_workout_in_progress():
    user_id = get_jwt_identity()
    latest_user_workout = Workout.query.filter_by(user_id=user_id).order_by(Workout.id.desc()).first()
    if latest_user_workout and latest_user_workout.end_time is None: #existing workout
        return jsonify_object(latest_user_workout, Workout), 200
    else:
        return {
            "error": "there is not workout in progress"
        }, 500


@workouts.route("/set/startup")
@jwt_required
def get_set_in_progress():
    user_id = get_jwt_identity()
    latest_user_workout = Workout.query.filter_by(user_id=user_id).order_by(Workout.id.desc()).first()
    if latest_user_workout and latest_user_workout.end_time is None:  # existing workout
        current_workout_exercise = WorkoutExercise.query.filter_by(workout_id=latest_user_workout.id).order_by(WorkoutExercise.order.desc()).first()
        if current_workout_exercise is None or current_workout_exercise.completed:
            return {
                "error": "there is no workout in progress"
            }, 500
        else:
            current_exercise = Exercise.query.get(current_workout_exercise.exercise_id).name
            return {
                current_exercise : [jsonify_object(a_set, Sets) for a_set in current_workout_exercise.sets],
                "current_exercise" : current_exercise,
                "workout_exercise_id" : current_workout_exercise.id
            }, 200
    else:
        return {
                   "error": "there is not workout in progress"
               }, 500


