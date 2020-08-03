# from app import app, db, hashing
# from app.models import *
# from flask import request, jsonify, Response
# from sqlalchemy import func
# from app import (jwt_required, create_access_token,
#     get_jwt_identity)
# from datetime import datetime, timedelta
# from itertools import zip_longest
#
#
# def jsonify_object(instance, cls, remove_keys=[]):
#     return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns if i.key not in remove_keys}
#
#
# def one_rep_max(a_set):
#     # come back and check if the unit of weight is pounds or kilograms
#     return a_set.weight * a_set.repetition * .033 + a_set.weight
#
#
# def date_formatter(date):
#     day = date.day
#     month = date.month
#     year = date.year
#     if month < 10:
#         month = f"0{month}"
#     if day < 10:
#         day = f"0{day}"
#     return f"{year}-{month}-{day}"
#
#
# @app.route('/muscles')
# def get_muscles():
#     muscles = Muscle.query.all()
#     muscles_list = [muscle.name for muscle in muscles]
#     return " ".join(muscles_list)
#
#
#
#





# @app.route('/workout/<workout_exercise_id>/exercise', methods=['PATCH'])
# def complete_exercise(workout_exercise_id):
#     completed_exercise = WorkoutExercise.query.get(workout_exercise_id)
#     completed_exercise.completed = True
#     db.session.commit()
#     return {
#         "success": "updated successfully"
#     }, 204
#
#
# @app.route('/workout/exercise/<id>/set', methods=['POST', 'PATCH', 'DELETE'])
# def manage_set(id):
#     req = request.get_json()
#     current_workout_exercise = WorkoutExercise.query.get(id)
#     if request.method == 'POST':
#         order = len(current_workout_exercise.sets) + 1
#         new_set = Sets(repetition=req["repetition"], set_order=order, weight=req["weight"], unit=req["unit"], workout_exercise_id=id)
#         db.session.add(new_set)
#         db.session.commit()
#         return jsonify_object(instance=new_set, cls=Sets), 201
#     elif request.method == 'PATCH':
#         current_set = Sets.query.get(req["id"])
#         current_set.repetition, current_set.weight, current_set.unit = req["repetition"], req["weight"], req["unit"]
#         db.session.commit()
#         return jsonify_object(current_set, Sets)
#     elif request.method == "DELETE":
#         current_set = Sets.query.get(req["id"])
#         for a_set in current_workout_exercise.sets:
#             if current_set.set_order < a_set.set_order:
#                 a_set.set_order -= 1
#                 db.session.commit()
#         db.session.delete(current_set)
#         db.session.commit()
#         return jsonify([jsonify_object(a_set) for a_set in WorkoutExercise.query.get(id)])
#
#
# @app.route('/workout/exercise/<id>/set/<set_id>', methods=['DELETE'])
# @jwt_required
# def delete_set(id, set_id):
#     current_workout_exercise = WorkoutExercise.query.get(id)
#     current_set = Sets.query.get(set_id)
#     if not current_set:
#         return {
#             "error": "this set does not exist"
#         }, 500
#     for a_set in current_workout_exercise.sets:
#         if current_set.set_order < a_set.set_order:
#             a_set.set_order -= 1
#             db.session.commit()
#     db.session.delete(current_set)
#     db.session.commit()
#     return jsonify([jsonify_object(a_set, Sets) for a_set in WorkoutExercise.query.get(id).sets])
#
#
# @app.route('/workout/<workout_id>/set')
# @jwt_required
# def get_full_workout(workout_id):
#     user_id = get_jwt_identity()
#     # where id comes from WorkoutExercise
#     workout_exercise_list = WorkoutExercise.query.filter_by(workout_id=workout_id).all()
#     if len(workout_exercise_list) == 0:
#         return {
#             "error": "this workout contains no exercises yet"
#         }, 400
#     # grab the primary key here and query sets to get all the additional info
#     complete_workout = []
#     for exercise in workout_exercise_list:
#         set_list = Sets.query.filter_by(workout_exercise_id=exercise.id).all()
#         exercise_name = Exercise.query.get(exercise.exercise_id).name
#         all_workouts_with_exercise = WorkoutExercise.query.join(Workout).filter(Workout.user_id == user_id).filter(WorkoutExercise.exercise_id == exercise.exercise_id).all()
#         exercise_sets = {
#             "exercise": exercise_name,
#             "muscle": Muscle.query.filter_by(id = Exercise.query.get(exercise.exercise_id).muscle_id).first().name,
#             "order": exercise.order,
#             "sets": [{**jsonify_object(sets, Sets), "max": one_rep_max(sets)} for sets in set_list],
#             "previous_sets": []
#         }
#         if len(all_workouts_with_exercise) > 1:
#             exercise_sets["previous_sets"] = [jsonify_object(sets, Sets) for sets in all_workouts_with_exercise[-2].sets][:len(set_list)]
#         complete_workout.append(exercise_sets)
#     return jsonify(complete_workout)
#
#
# @app.route('/workout/exercise/<id>')
# def get_sets_for_workout(id):
#     # where id comes from WorkoutExercise
#     exercise = Exercise.query.get(WorkoutExercise.query.get(id).exercise_id).name
#     set_list = Sets.query.filter_by(workout_exercise_id=id).all()
#     # grab the primary key here and query sets to get all the additional info
#     # for exercise in exercise_list:
#     #     #     exercise_sets = Sets.query.filter_by(workout_exercise_id=exercise.id).all()
#     #     # Sets.query.filter_by()
#     return {
#         "exercise": exercise,
#         "sets": [jsonify_object(sets, Sets, ['workout_exercise_id']) for sets in set_list]
#     }
#
#
# @app.route('/workout/exercise')
# def get_all_exercises():
#     exercises = Exercise.query.all()
#     exercise_with_muscle = []
#     for exercise in exercises:
#         exercise_with_muscle.append({
#             "exercise": exercise.name,
#             "muscle": Muscle.query.filter_by(id=exercise.muscle_id).first().name
#         })
#     return jsonify(exercise_with_muscle)
#
#
# @app.route('/workout/exercise/<workout_exercise_id>', methods=['DELETE'])
# @jwt_required
# def delete_exercise(workout_exercise_id):
#     id = get_jwt_identity()
#     deleted_exercise = WorkoutExercise.query.get(workout_exercise_id)
#     workout = Workout.query.get(deleted_exercise.workout_id)
#     if workout.user_id == id:
#         deleted_exercise_dict = jsonify_object(deleted_exercise, WorkoutExercise)
#         db.session.delete(deleted_exercise)
#         db.session.commit()
#         return {
#             "message": "successful",
#             "exercise": deleted_exercise_dict
#         }
#     else:
#         return {
#             "error": "you cannot delete this exercise"
#         }, 204
#
# @app.route('/user/exercise')
# @jwt_required
# def get_user_exercise_list():
#     id = get_jwt_identity()
#     my_workouts = Workout.query.filter_by(user_id=id).all()
#     exercise_tuple_list = Workout.query.with_entities(Exercise.name, Exercise.id).join(WorkoutExercise).filter(Workout.user_id == id).distinct().all()
#     all_my_exercises = [{"id": exercise[1], "name": exercise[0]} for exercise in exercise_tuple_list]
#     dates = [w.start_time for w in Workout.query.filter_by(user_id=id).all() if w.end_time]
#
#     return jsonify({
#         "exercises": all_my_exercises,
#         "dates": [date_formatter(d) for d in dates],
#         "total_workouts": len(dates)
#                     })
#
#
# @app.route('/user/exercise/<e_id>')
# @jwt_required
# def get_user_exercise_stats(e_id):
#     id = get_jwt_identity()
#
#     all_sets_by_exercise = Sets.query.join(WorkoutExercise, Workout, Exercise).filter(Workout.user_id == id).filter(
#         WorkoutExercise.exercise_id == e_id).with_entities(Sets).all()
#
#     if len(all_sets_by_exercise) == 0:
#         return {"error": "no information available"}, 500
#
#     sum_of_reps_by_weight = Sets.query.join(WorkoutExercise, Workout).filter(Workout.user_id == id).filter(
#         WorkoutExercise.exercise_id == e_id).with_entities(func.sum(Sets.repetition), Sets.weight).group_by(
#         Sets.weight).all()
#
#     max_rep_tuple = Sets.query.join(WorkoutExercise, Workout).filter(Workout.user_id== id).filter(WorkoutExercise.exercise_id==e_id)\
#         .with_entities(func.max(Sets.repetition), Sets.weight, Workout.start_time, WorkoutExercise.order, Sets.set_order, Sets.unit).order_by(Sets.weight).first()
#
#     max_weight_tuple = Sets.query.join(WorkoutExercise, Workout).filter(Workout.user_id==id).filter(WorkoutExercise.exercise_id==e_id)\
#         .with_entities(func.max(Sets.weight), Sets.repetition, Workout.start_time, WorkoutExercise.order, Sets.set_order, Sets.unit).order_by(Sets.repetition).first()
#
#     # tuple consisting of average weight, average reps, total reps, total weights
#     aw_ar_tr_tw = Sets.query.join(WorkoutExercise, Workout).filter(Workout.user_id==id).filter(WorkoutExercise.exercise_id==e_id)\
#         .with_entities(func.avg(Sets.weight), func.avg(Sets.repetition), func.sum(Sets.repetition), func.sum(Sets.weight)).first()
#
#     max_one_rep_set = all_sets_by_exercise[0]
#     reps = []
#     weight = []
#     for frequency in sum_of_reps_by_weight:
#         reps.append(frequency[0])
#         weight.append(frequency[1])
#
#
#     for current_set in all_sets_by_exercise:
#         if one_rep_max(current_set) >= one_rep_max(max_one_rep_set):
#             max_one_rep_set = current_set
#     return {
#         "max_weight": {
#             "weight": max_weight_tuple[0],
#             "repetition": max_weight_tuple[1],
#             "date": date_formatter(max_weight_tuple[2]),
#             "exercise_order": max_weight_tuple[3],
#             "set_order": max_weight_tuple[4],
#             "unit": max_weight_tuple[5]
#         },
#         "max_reps": {
#             "repetition": max_rep_tuple[0],
#             "weight": max_rep_tuple[1],
#             "date": date_formatter(max_rep_tuple[2]),
#             "exercise_order": max_rep_tuple[3],
#             "set_order": max_rep_tuple[4],
#             "unit": max_rep_tuple[5]
#         },
#         "average_weight": aw_ar_tr_tw[0],
#         "average_reps": aw_ar_tr_tw[1],
#         "total_sets": aw_ar_tr_tw[2],
#         "total_weight": aw_ar_tr_tw[3],
#         "projected_one_rep": {
#              "weight": max_one_rep_set.weight,
#              "reps": max_one_rep_set.repetition,
#              "max_weight": one_rep_max(max_one_rep_set)
#          },
#         "reps_by_weight": [{"totalReps": i[0], "weight": i[1]} for i in sum_of_reps_by_weight],
#         "reps": reps,
#         "weight": weight
#     }
#
#
# @app.route('/user/workouts/date',methods=['POST'])
# @jwt_required
# def get_workout_by_date():
#     id = get_jwt_identity()
#     date = request.get_json()['date'] # format will be 2020-05-11
#     year, month, day = date.split('-')
#     formatted_date = datetime(int(year), int(month), int(day))
#     all_workouts = Workout.query.filter_by(user_id = id).filter(Workout.end_time !=None).all()
#     all_workouts_by_date = []
#     for a_workout in all_workouts:
#         if a_workout.start_time.date() == formatted_date.date():
#             all_workouts_by_date.append({**jsonify_object(a_workout, Workout),
#                                  'total_time':(a_workout.end_time - a_workout.start_time).total_seconds(),
#                                  "muscles": (f"{a_workout.muscles}"[1:-1]).split(',')
#                                  })
#     return jsonify(all_workouts_by_date)
#
# @app.route('/user/workouts')
# @jwt_required
# def get_all_workouts():
#     id = get_jwt_identity()
#     my_workouts = Workout.query.filter_by(user_id=id).filter(Workout.end_time!=None).all()
#     return jsonify([jsonify_object(workout, Workout) for workout in my_workouts])
#
#
# @app.route('/workouts/<id>')
# def get_users_workout(id):
#     workout_dict = {}
#     for index, exercise in enumerate(Workout.query.get(2).workout_exercise):
#         current_exercise = Exercise.query.get(WorkoutExercise.exercise_id).name
#         if current_exercise not in workout_dict:
#             workout_dict[current_exercise] = [jsonify_object(current_set, Sets) for current_set in exercise.sets]
#         else:
#             workout_dict[f"{current_exercise}-{index}"] = [jsonify_object(current_set, Sets) for current_set in exercise.sets]
#
#     return jsonify(workout_dict)
#
# #Start up enpoints for workouts and sets
#
# @app.route("/workout/startup")
# @jwt_required
# def get_workout_in_progress():
#     id = get_jwt_identity()
#     latest_user_workout = Workout.query.filter_by(user_id=id).order_by(Workout.id.desc()).first()
#     if latest_user_workout and latest_user_workout.end_time is None: #existing workout
#         return jsonify_object(latest_user_workout, Workout), 200
#     else:
#         return {
#             "error": "there is not workout in progress"
#         }, 500
#         # there are no workouts that are active
#
#
# @app.route("/workout/set/startup")
# @jwt_required
# def get_set_in_progress():
#     id = get_jwt_identity()
#     latest_user_workout = Workout.query.filter_by(user_id=id).order_by(Workout.id.desc()).first()
#     if latest_user_workout and latest_user_workout.end_time is None:  # existing workout
#         current_workout_exercise = WorkoutExercise.query.filter_by(workout_id=latest_user_workout.id).order_by(WorkoutExercise.order.desc()).first()
#         if current_workout_exercise is None or current_workout_exercise.completed:
#             return {
#                 "error": "there is no workout in progress"
#             }, 500
#         else:
#             current_exercise = Exercise.query.get(current_workout_exercise.exercise_id).name
#             return {
#                 current_exercise : [jsonify_object(a_set, Sets) for a_set in current_workout_exercise.sets],
#                 "current_exercise" : current_exercise,
#                 "workout_exercise_id" : current_workout_exercise.id
#             }, 200
#     else:
#         return {
#                    "error": "there is not workout in progress"
#                }, 500
#
#
# @app.route("/saved/workout", methods=['POST'])
# @jwt_required
# def create_template_workout():
#     user_id = get_jwt_identity()
#     req = request.get_json()
#     new_template = WorkoutTemplate(name=req['name'], author_id=user_id)
#     db.session.commit()
#     return jsonify_object(new_template, WorkoutTemplate), 201
#
#
# @app.route("/workout/template/<template_id>/exercise", methods=['POST', 'PATCH'])
# @jwt_required
# def add_saved_workout_exercise(template_id):
#     user_id = get_jwt_identity()
#     req = request.get_json()
#     current_template = WorkoutTemplate.query.get(template_id)
#     if current_template.author_id == user_id:
#         if request.method == 'POST':
#             exercise_id = Exercise.query.filter_by(name=req["exercise"]).first().id
#             length_of_workout = len(current_template.saved_workout_exercise)
#             SavedWorkoutExercise(template_id=template_id, exercise_id=exercise_id, order= length_of_workout + 1)
#             db.session.commit()
#             return jsonify([jsonify_object(swe, SavedWorkoutExercise) for swe in current_template.saved_workout_exercise])
#         if request.method == 'PATCH':
#             current_template.complete = True
#             SavedWorkout(template_id=template_id, user_id=user_id)
#             db.session.commit()
#             return jsonify_object(current_template, WorkoutTemplate)
#     else:
#         return {"error": "This template does not belong to you"}, 500
#
#
#
#
# @app.route("/workout/template/exercise/<saved_workout_exercise_id>", methods=['DELETE'])
# @jwt_required
# def delete_saved_workout_exercise(saved_workout_exercise_id):
#     user_id = get_jwt_identity()
#     current_swe = SavedWorkoutExercise.query.get(saved_workout_exercise_id)
#     current_workout_template = WorkoutTemplate.query.get(current_swe.template_id)
#     if user_id == current_workout_template.author_id:
#         template_length = len(current_workout_template.saved_workout_exercise)
#         for saved_we in current_workout_template[current_swe.order:]:
#             saved_we.order -= 1
#             db.session.commit()
#         db.session.delete(current_swe)
#         return jsonify([jsonify_object(swe, SavedWorkoutExercise) for swe in current_workout_template.saved_workout_exercise])
#     else:
#         return {"error":"This workout exercise is not yours to delete"}, 500
#
#
# @app.route('/saved/workout/<workout_id>', methods=['POST'])
# @jwt_required
# def create_full_saved_workout(workout_id):
#     print("hello")
#     user_id = get_jwt_identity()
#     req = request.get_json()
#
#     canvas_workout = Workout.query.get(workout_id)
#     canvas_muscles_trained = canvas_workout.muscles
#     canvas_we = canvas_workout.workout_exercise
#
#     if not len(canvas_muscles_trained) and not len(canvas_we):
#         return {
#             "error":"muscles or exercise from this workout are missing"
#         }, 500
#
#     new_workout_template = WorkoutTemplate(name=req['name'], author_id=user_id)
#     db.session.add(new_workout_template)
#     db.session.commit()
#
#     for muscle in canvas_muscles_trained:
#         db.session.add(SavedWorkoutMuscle(template_id=new_workout_template.id, muscle_id=muscle.id))
#         db.session.commit()
#     for workout_exercise in canvas_we:
#         db.session.add(SavedWorkoutExercise(exercise_id=workout_exercise.exercise_id, template_id=new_workout_template.id, order=workout_exercise.order))
#         db.session.commit()
#
#     db.session.add(SavedWorkout(user_id=user_id, workout_template_id=new_workout_template.id))
#     db.session.commit()
#
#     new_workout_template.complete = True
#     db.session.commit()
#     return {
#         "name": new_workout_template.name,
#         "user": User.query.get(user_id).name,
#         "muscles": [muscles.name for muscles in new_workout_template.muscles],
#         "exercise_length": len(new_workout_template.saved_workout_exercise)
#     }
#
# @app.route("/workout/saved")
# @jwt_required
# def get_saved_workouts():
#     user_id = get_jwt_identity()
#     my_saved_workout_templates = SavedWorkout.query.join(WorkoutTemplate, User).filter(SavedWorkout.id == user_id).with_entities(WorkoutTemplate).all()
#     return jsonify([jsonify_object(template, WorkoutTemplate) for template in my_saved_workout_templates])
#
#
# @app.route("/workout/saved/<template_id>/schedule", methods=["POST"])
# @jwt_required
# def schedule_workout(template_id):
#     user_id = get_jwt_identity()
#     req = request.get_json()
#
#     formatted_date = req['date'].replace('-', ' ')
#     formatted_date_final = datetime.strptime(formatted_date, '%Y %m %d')
#     new_schedule = Schedule(date=formatted_date_final, user_id=user_id, template_id=template_id)
#     db.session.add(new_schedule)
#     db.session.commit()
#     return {
#         "message": "success"
#     }
#
#
# @app.route("/workout/schedule")
# @jwt_required
# def get_schedule():
#     user_id = get_jwt_identity()
#     user_schedule = Schedule.query.join(WorkoutTemplate).filter(Schedule.user_id==user_id).with_entities(Schedule.date, WorkoutTemplate.name, WorkoutTemplate.id).all()
#     agenda = {}
#     for plan in user_schedule:
#         formatted_date = date_formatter(plan[0])
#         if formatted_date in agenda:
#             agenda[formatted_date] = [*agenda[formatted_date], {"name": plan[1], "id": plan[2]}]
#         else:
#             agenda[formatted_date] = [{"name": plan[1], "id": plan[2]}]
#     return jsonify(agenda)
#
#
# @app.route("/workout/saved/today", methods=['POST'])
# @jwt_required
# def get_workout_of_the_day():
#     user_id = get_jwt_identity()
#     formatted_date = request.get_json()['date'].replace('-', ' ')
#     formatted_date_final = datetime.strptime(formatted_date, '%Y %m %d')
#     workout_of_the_day = Schedule.query.join(WorkoutTemplate).filter(Schedule.user_id==user_id).filter(Schedule.date==formatted_date_final).with_entities(WorkoutTemplate).all()
#     return_arr = []
#     for workout in workout_of_the_day:
#         return_dict = { "name": workout.name }
#         return_dict["muscles"] = [Muscle.query.get(swm.muscle_id).name for swm in workout.muscles]            # for muscle in workout.muscles:
#         return_dict["exercises"] = [Exercise.query.get(swe.exercise_id).name for swe in workout.saved_workout_exercise]
#         return_arr.append(return_dict)
#     return jsonify(return_arr)
#
