from app import app

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