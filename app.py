# from models import Schema
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_pal.db'
db = SQLAlchemy(app)

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


if __name__ == '__main__':
    # Schema()
    app.run(debug=True)  # this should be set to True in development mode
