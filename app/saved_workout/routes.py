from flask import Blueprint, request, jsonify
from app import jwt_required, get_jwt_identity, db
from app.models import *
from datetime import datetime, timedelta
from app.utils import jsonify_object, one_rep_max, date_formatter

saved = Blueprint('saved', __name__, url_prefix='/saved')


@saved.route("/workout", methods=['POST'])
@jwt_required
def manage_template_workout():
    if request.method == "POST":
        user_id = get_jwt_identity()
        req = request.get_json()
        new_template = WorkoutTemplate(name=req['name'], author_id=user_id)
        db.session.commit()
        return jsonify_object(new_template, WorkoutTemplate), 201
    else:
        my_saved_workout_templates = SavedWorkout.query.join(WorkoutTemplate, User).filter(SavedWorkout.id == user_id).with_entities(WorkoutTemplate).all()
        return jsonify([jsonify_object(template, WorkoutTemplate) for template in my_saved_workout_templates])



@saved.route("/workout/template/<template_id>/exercise", methods=['POST', 'PATCH'])
@jwt_required
def add_saved_workout_exercise(template_id):
    # currently not used
    user_id = get_jwt_identity()
    req = request.get_json()
    current_template = WorkoutTemplate.query.get(template_id)
    if current_template.author_id == user_id:
        if request.method == 'POST':
            exercise_id = Exercise.query.filter_by(name=req["exercise"]).first().id
            length_of_workout = len(current_template.saved_workout_exercise)
            SavedWorkoutExercise(template_id=template_id, exercise_id=exercise_id, order= length_of_workout + 1)
            db.session.commit()
            return jsonify([jsonify_object(swe, SavedWorkoutExercise) for swe in current_template.saved_workout_exercise])
        if request.method == 'PATCH':
            current_template.complete = True
            SavedWorkout(template_id=template_id, user_id=user_id)
            db.session.commit()
            return jsonify_object(current_template, WorkoutTemplate)
    else:
        return {"error": "This template does not belong to you"}, 500


@saved.route("/workout/template/exercise/<saved_workout_exercise_id>", methods=['DELETE'])
@jwt_required
def delete_saved_workout_exercise(saved_workout_exercise_id):
    # currently not used
    user_id = get_jwt_identity()
    current_swe = SavedWorkoutExercise.query.get(saved_workout_exercise_id)
    current_workout_template = WorkoutTemplate.query.get(current_swe.template_id)
    if user_id == current_workout_template.author_id:
        template_length = len(current_workout_template.saved_workout_exercise)
        for saved_we in current_workout_template[current_swe.order:]:
            saved_we.order -= 1
            db.session.commit()
        db.session.delete(current_swe)
        return jsonify([jsonify_object(swe, SavedWorkoutExercise) for swe in current_workout_template.saved_workout_exercise])
    else:
        return {"error":"This workout exercise is not yours to delete"}, 500


@saved.route('/workout/<workout_id>', methods=['POST'])
@jwt_required
def create_full_saved_workout(workout_id):
    # currently not used
    print("hello")
    user_id = get_jwt_identity()
    req = request.get_json()

    canvas_workout = Workout.query.get(workout_id)
    canvas_muscles_trained = canvas_workout.muscles
    canvas_we = canvas_workout.workout_exercise

    if not len(canvas_muscles_trained) and not len(canvas_we):
        return {
            "error":"muscles or exercise from this workout are missing"
        }, 500

    new_workout_template = WorkoutTemplate(name=req['name'], author_id=user_id)
    db.session.add(new_workout_template)
    db.session.commit()

    for muscle in canvas_muscles_trained:
        db.session.add(SavedWorkoutMuscle(template_id=new_workout_template.id, muscle_id=muscle.id))
        db.session.commit()
    for workout_exercise in canvas_we:
        db.session.add(SavedWorkoutExercise(exercise_id=workout_exercise.exercise_id, template_id=new_workout_template.id, order=workout_exercise.order))
        db.session.commit()

    db.session.add(SavedWorkout(user_id=user_id, workout_template_id=new_workout_template.id))
    db.session.commit()

    new_workout_template.complete = True
    db.session.commit()
    return {
        "name": new_workout_template.name,
        "user": User.query.get(user_id).name,
        "muscles": [muscles.name for muscles in new_workout_template.muscles],
        "exercise_length": len(new_workout_template.saved_workout_exercise)
    }


@saved.route("/<template_id>/schedule", methods=["POST"])
@jwt_required
def schedule_workout(template_id):
    user_id = get_jwt_identity()
    req = request.get_json()

    formatted_date = req['date'].replace('-', ' ')
    formatted_date_final = datetime.strptime(formatted_date, '%Y %m %d')
    new_schedule = Schedule(date=formatted_date_final, user_id=user_id, template_id=template_id)
    db.session.add(new_schedule)
    db.session.commit()
    return {
        "message": "success"
    }


@saved.route("/schedule")
@jwt_required
def get_schedule():
    user_id = get_jwt_identity()
    user_schedule = Schedule.query.join(WorkoutTemplate).filter(Schedule.user_id==user_id).with_entities(Schedule.date, WorkoutTemplate.name, WorkoutTemplate.id).all()
    agenda = {}
    for plan in user_schedule:
        formatted_date = date_formatter(plan[0])
        if formatted_date in agenda:
            agenda[formatted_date] = [*agenda[formatted_date], {"name": plan[1], "id": plan[2]}]
        else:
            agenda[formatted_date] = [{"name": plan[1], "id": plan[2]}]
    return jsonify(agenda)


@saved.route("/today", methods=['POST'])
@jwt_required
def get_workout_of_the_day():
    user_id = get_jwt_identity()
    formatted_date = request.get_json()['date'].replace('-', ' ')
    formatted_date_final = datetime.strptime(formatted_date, '%Y %m %d')
    workout_of_the_day = Schedule.query.join(WorkoutTemplate).filter(Schedule.user_id==user_id).filter(Schedule.date==formatted_date_final).with_entities(WorkoutTemplate).all()
    return_arr = []
    for workout in workout_of_the_day:
        return_dict = { "name": workout.name }
        return_dict["muscles"] = [Muscle.query.get(swm.muscle_id).name for swm in workout.muscles]            # for muscle in workout.muscles:
        return_dict["exercises"] = [Exercise.query.get(swe.exercise_id).name for swe in workout.saved_workout_exercise]
        return_arr.append(return_dict)
    return jsonify(return_arr)
