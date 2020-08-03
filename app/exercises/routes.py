from flask import Blueprint, request, jsonify
from app import jwt_required, get_jwt_identity, db
from sqlalchemy import func
from app.models import *
from datetime import datetime, timedelta
from app.utils import jsonify_object, one_rep_max, date_formatter

exercises = Blueprint('exercises', __name__, url_prefix='/exercise')


@exercises.route('')
def get_all_exercises():
    all_exercises = Exercise.query.all()
    exercise_with_muscle = []
    for exercise in all_exercises:
        exercise_with_muscle.append({
            "exercise": exercise.name,
            "muscle": Muscle.query.filter_by(id=exercise.muscle_id).first().name
        })
    return jsonify(exercise_with_muscle)


@exercises.route('/user')
@jwt_required
def get_user_exercise_list():
    id = get_jwt_identity()
    exercise_tuple_list = Workout.query.with_entities(Exercise.name, Exercise.id).join(WorkoutExercise).filter(Workout.user_id == id).distinct().all()
    all_my_exercises = [{"id": exercise[1], "name": exercise[0]} for exercise in exercise_tuple_list]
    dates = [w.start_time for w in Workout.query.filter_by(user_id=id).all() if w.end_time]

    return jsonify({
        "exercises": all_my_exercises,
        "dates": [date_formatter(d) for d in dates],
        "total_workouts": len(dates)
                    })


@exercises.route('/<int:e_id>')
@jwt_required
def get_user_exercise_stats(e_id):
    id = get_jwt_identity()

    all_sets_by_exercise = Sets.query.join(WorkoutExercise, Workout, Exercise).filter(Workout.user_id == id).filter(
        WorkoutExercise.exercise_id == e_id).with_entities(Sets).all()

    if len(all_sets_by_exercise) == 0:
        return {"error": "no information available"}, 500

    users_exercise_base_query = Sets.query.join(WorkoutExercise, Workout).filter(Workout.user_id == id).filter(WorkoutExercise.exercise_id == e_id)

    sum_of_reps_by_weight = users_exercise_base_query.with_entities(func.sum(Sets.repetition), Sets.weight).group_by(Sets.weight).all()

    max_rep_tuple = users_exercise_base_query.with_entities(func.max(Sets.repetition), Sets.weight, Workout.start_time, WorkoutExercise.order, Sets.set_order, Sets.unit)\
        .group_by(Sets.weight, Workout.start_time, WorkoutExercise.order, Sets.set_order, Sets.unit).order_by(Sets.weight.desc()).first()

    max_weight_tuple = users_exercise_base_query.with_entities(func.max(Sets.weight), Sets.repetition, Workout.start_time, WorkoutExercise.order, Sets.set_order, Sets.unit)\
        .group_by(Sets.repetition, Workout.start_time, WorkoutExercise.order, Sets.set_order, Sets.unit).order_by(Sets.repetition.desc()).first()

    # tuple consisting of average weight, average reps, total reps, total weights
    aw_ar_tr_tw = users_exercise_base_query.with_entities(func.avg(Sets.weight), func.avg(Sets.repetition), func.sum(Sets.repetition), func.sum(Sets.weight)).first()

    max_one_rep_set = all_sets_by_exercise[0]
    reps = []
    weight = []
    for frequency in sum_of_reps_by_weight:
        reps.append(frequency[0])
        weight.append(frequency[1])


    for current_set in all_sets_by_exercise:
        if one_rep_max(current_set) >= one_rep_max(max_one_rep_set):
            max_one_rep_set = current_set

    stats = {
        "max_weight": {
                    "weight": max_weight_tuple[0],
                    "repetition": max_weight_tuple[1],
                    "date": date_formatter(max_weight_tuple[2]),
                    "exercise_order": max_weight_tuple[3],
                    "set_order": max_weight_tuple[4],
                    "unit": max_weight_tuple[5]
        },
        "max_reps": {
                    "repetition": max_rep_tuple[0],
                    "weight": max_rep_tuple[1],
                    "date": date_formatter(max_rep_tuple[2]),
                    "exercise_order": max_rep_tuple[3],
                    "set_order": max_rep_tuple[4],
                    "unit": max_rep_tuple[5]
                },
        "average_weight": float(aw_ar_tr_tw[0]),
        "average_reps": float(aw_ar_tr_tw[1]),
        "total_sets": aw_ar_tr_tw[2],
        "total_weight": aw_ar_tr_tw[3],
        "projected_one_rep": {
             "weight": max_one_rep_set.weight,
             "reps": max_one_rep_set.repetition,
             "max_weight": one_rep_max(max_one_rep_set)
         },
        "reps_by_weight": [{"totalReps": i[0], "weight": i[1]} for i in sum_of_reps_by_weight],
        "reps": reps,
        "weight": weight
    }

    return stats



