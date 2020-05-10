from app import app
from app.models import User, Muscle, Exercise, Workout, Sets, Workout_Muscle
from flask import request

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
def getMuscles():
    muscles = Muscle.query.all()
    muscles_list = [muscle.name for muscle in muscles]
    return " ".join(muscles_list)

@app.route('/workout/<id>', methods=['POST'])
def startWorkout(id):
    print(request.json['hello'])
    return "hello"
