from app import app, db, hashing
from app.models import User, Muscle, Exercise, Workout, Sets, WorkoutMuscle, WorkoutExercise
from flask import request, jsonify, Response
from app import (jwt_required, create_access_token,
    get_jwt_identity)
from datetime import datetime, timedelta


def jsonify_object(instance, cls, remove_keys=[]):
    return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns if i.key not in remove_keys}


def one_rep_max(a_set):
    # come back and check if the unit of weight is pounds or kilograms
    return a_set.weight * a_set.repetition * .033 + a_set.weight


@app.route('/muscles')
def get_muscles():
    muscles = Muscle.query.all()
    muscles_list = [muscle.name for muscle in muscles]
    return " ".join(muscles_list)

#START For user registration and login
@app.route('/user/signup', methods=['POST'])
def create_user():
    user_info = request.get_json()
    if "password" not in user_info or "email" not in user_info or "name" not in user_info:
        return {
            "error": "You are missing one or both of the required fields: password, email"
               }, 400
    if len(User.query.filter_by(email=user_info["email"]).all()) >= 1:
        return {
            "error": "this email has already been taken"
        }, 400
    hashed_password = hashing.hash_value(user_info["password"], salt="salt")
    db.session.add(User(name=user_info['name'], email=user_info['email'], password=hashed_password))
    db.session.commit()
    newly_created_user = User.query.filter_by(email=user_info["email"]).first()
    jsonified_user = jsonify_object(newly_created_user, User, ["password"])
    expires = timedelta(days=365)
    token = create_access_token(identity=newly_created_user.id, expires_delta = expires)
    return {
               "token": token,
                **jsonified_user
           }, 201


@app.route('/user/signin', methods=["POST"])
def sign_in():
    user_info = request.get_json()
    if "password" not in user_info or "email" not in user_info:
        return {
            "error": "You are missing one or both of the required fields: password, email"
               }, 400
    saved_user = User.query.filter_by(email=user_info["email"]).first()
    if saved_user is None:
        return {
            "error": "A user by that email of '{}' does not exist".format(user_info["email"])
               }, 400
    # if hashing.check_value(h, "password", salt="hello)"
    print(hashing.check_value(saved_user.password, user_info["password"], salt="salt"))
    if hashing.check_value(saved_user.password, user_info["password"], salt="salt"):
        expires = timedelta(days=365)
        token = create_access_token(identity=saved_user.id, expires_delta = expires)
        return {
                   "token": token,
                    **jsonify_object(saved_user, User, ["password"])
               }, 201
    else:
        return {
            "Error": "That is an incorrect password"
        }, 500
#END


@app.route('/user/workout', methods=['POST'])
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
    return {"id": new_workout.id}

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
    order = len(Workout.query.get(id).workout_exercise) + 1
    exercise_id = Exercise.query.filter_by(name=new_exercise["exercise"]).first().id
    new_workout_exercise = WorkoutExercise(workout_id=id, exercise_id=exercise_id, order=order)
    db.session.add(new_workout_exercise)
    db.session.commit()
    return {
        "id": new_workout_exercise.id,
        "exercise": new_exercise["exercise"],
    }

@app.route('/workout/exercise/<id>/set', methods=['POST'])
def add_set(id):
    req = request.get_json()
    order = len(WorkoutExercise.query.get(id).sets) + 1
    new_set = Sets(repetition=req["repetition"], set_order=order, weight=req["weight"], unit=req["unit"], workout_exercise_id=id)
    db.session.add(new_set)
    db.session.commit()
    return jsonify_object(instance=new_set, cls=Sets)

@app.route('/workout/<id>')
def get_workout(id):
    #!!
    # gets exercises by name for a give workout
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
    if len(exercise_list) == 0:
        return {
            "error": "this workout contains no exercises yet"
        }, 400
    # grab the primary key here and query sets to get all the additional info
    complete_workout= []
    for exercise in exercise_list:
        set_list = Sets.query.filter_by(workout_exercise_id=exercise.id).all()
        exercise_name = Exercise.query.get(exercise.id).name
        exercise_sets = {
            "exercise": exercise_name,
            "muscle": Muscle.query.filter_by(id = Exercise.query.get(exercise.id).muscle_id).first().name,
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
    exercise_with_muscle = []
    for exercise in exercises:
        exercise_with_muscle.append({
            "exercise": exercise.name,
            "muscle": Muscle.query.filter_by(id=exercise.muscle_id).first().name
        })
    return jsonify(exercise_with_muscle)


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

@app.route('/user/exercise')
@jwt_required
def user_exercise_list():
    id = get_jwt_identity()
    print("this is id", id)
    my_workouts = Workout.query.filter_by(user_id=id).all()
    all_my_workout_exercises = [WorkoutExercise.query.get(workout.id) for workout in my_workouts if workout]
    all_my_exercises = [jsonify_object(Exercise.query.filter_by(id=e.exercise_id).first(), Exercise) for e in all_my_workout_exercises if e]
    dates = [w.start_time for w in Workout.query.filter_by(user_id=id).all() if w.end_time]
    def date_formatter(date):
        day = date.day
        month = date.month
        year = date.year
        if month < 10:
            month = f"0{month}"
        if day < 10:
            day = f"0{day}"
        return f"{year}-{month}-{day}"

    return jsonify({
        "exercises": all_my_exercises,
        "dates": [date_formatter(d) for d in dates],
        "total_workouts": len(dates)
                    })

@app.route('/user/<id>/exercise/<e_id>')
def user_exercise_stats(id, e_id):
    my_workouts = Workout.query.filter_by(user_id=id).all()
    all_my_workout_exercises = [WorkoutExercise.query.get(workout.id) for workout in my_workouts]

    filtered_by_exercise = list(filter(lambda x: x and x.exercise_id == int(e_id), all_my_workout_exercises))

    if len(filtered_by_exercise) == 0:
        return {"error": "no information available"}, 500

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
        "total_sets": count,
        "projected_one_rep": {
            "weight": max_one_rep_set.weight,
            "reps": max_one_rep_set.repetition,
            "max_weight": max_one_rep
        }
    })


@app.route('/user/workouts/date',methods=['POST'])
@jwt_required
def get_workout_by_date():
    id = get_jwt_identity()
    print(id)
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

@app.route('/user/workouts')
@jwt_required
def get_all_workouts():
    id = get_jwt_identity()
    my_workouts = Workout.query.filter_by(user_id=id).filter(Workout.end_time!=None).all()
    return jsonify([jsonify_object(workout, Workout) for workout in my_workouts])


@app.route('/workouts/<id>')
def get_users_workout(id):
    workout_dict = {}
    for index, exercise in enumerate(Workout.query.get(2).workout_exercise):
        current_exercise = Exercise.query.get(WorkoutExercise.exercise_id).name
        if current_exercise not in workout_dict:
            workout_dict[current_exercise] = [jsonify_object(current_set, Sets) for current_set in exercise.sets]
        else:
            workout_dict[f"{current_exercise}-{index}"] = [jsonify_object(current_set, Sets) for current_set in exercise.sets]

    return jsonify(workout_dict)

#Start up enpoints for workouts and sets

@app.route("/workout/startup")
@jwt_required
def get_workout_in_progress():
    id = get_jwt_identity()
    latest_user_workout = Workout.query.order_by(Workout.id.desc()).first()
    if latest_user_workout and latest_user_workout.end_time is None: #existing workout
        return jsonify_object(latest_user_workout, Workout), 200
    else:
        return {
            "error": "there is not workout in progress"
        }, 500
        # there are no workouts that are active


@app.route("/workout/startup")
@jwt_required
def get_workout_in_progress():