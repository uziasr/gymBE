from app.models import Muscle, Exercise
from app import db

major_muscle_group = ['Quadriceps', 'Hamstrings',
                      'Calves', 'Chest',
                      'Back', 'Shoulders',
                      'Triceps', 'Biceps',
                      'Forearms', 'Trapezius',
                      'Abs']

leg_exercises = [
    ('Leg press', 1),('Squat', 1), ('Leg Extensions', 1),
    ('Lunge', 1), ('Goblet Squat', 1), ('Front Squat', 1),
    ('Deadlift', 2), ('Leg Curls', 2), ('Glute-Ham Raise', 2),
    ('Romanian Deadlift', 2), ('Hip Thrust', 2), ('Kettlebell Swing', 2),
    ('Standing Calf Raise', 3), ('Seated Calf raise', 3),
             ]

push_exercises = [
    ('Barbell Bench Press', 4), ('Dumbbell Bench Press', 4), ('Incline Barbell Bench Press', 4),
    ('Incline Dumbbell Bench Press', 4), ('Decline Barbell Bench Press', 4), ('Decline Dumbbell Bench Press', 4),
    ('Cable Crossover', 4), ('Dumbbell Flye', 4), ('Machine Flye', 4), ('Low Cable Crossover', 4),
    ('Underhand Bench Press', 4), ('Wide-Grip Dips', 4), ('Push Ups', 4),
    ('Shoulder Barbell Press', 6),  ('Arnold Dumbbell Press', 6), ('Push Press', 6), ('Lateral Raise', 6),
    ('Seated Dumbbell Shoulder Press', 6), ('Seat Barbell Shoulder Press', 6), ('Reverse Pec Flye', 6),
    ('Dumbbell Lateral Raise', 6), ('Reverse Cable Crossover', 6), ('One-Arm Cable Lateral Raise', 6),
    ('Bent Over Reverse Flye', 6),
    ('Tricep Kickbacks', 7), ('Skull Crushers', 7), ('Dumbbell Lying Tricep Extensions', 7), ('Cable Tricep Push Down', 7),
    ('Cable Tricep Kickbacks', 7), ('Tricep Dips', 7),  ('Overhead Tricep Extension', 7), ('Pullover', 7), ('Overhead Cable Tricep Extension', 7)
                  ]

pull_exercises = [
    ('Barbell Bent Over Row', 5), ('Dumbbell Single Arm Row', 5), ('Barbell Bent Over Row Underhand', 5), ('Seated Cable Row', 5),
    ('Pull ups', 5), ('lat Pulldown', 5), ('Incline Dumbbell Row', 5), ('Chin Ups', 5), ('Inverted Row', 5), ('T-bar Row', 5),
    ('Back Extensions', 5), ('Rack Pulls', 5),
    ('Standing Barbell Curl', 8), ('Concentration Curl', 8), ('Standing Dumbbell Curl', 8), ('Hammer Curl', 8),
    ('Decline Dumbbell Curl', 8), ('Incline Dumbbell Curl', 8), ('Cable Bicep Curl', 8),  ('Preacher Curl', 8),  ('Machine Curl', 8),
    ('E-Z bar Curl', 8),
    ('Dumbbell Wrist Flexion', 9), ('Dumbbell Wrist Extension', 9),
    ("Farmer's Carry", 10), ('Face Pulls', 10),  ('Barbell Shrug', 10), ('Dumbbell Shrug', 10), ('Overhead Barbell Shrug', 10),
    ('Dumbbell Overhead Carry', 10),
]

core_exercises = [
    ('Plank', 11), ('Crunch', 11),  ('Vertical Leg Crunch', 11), ('V-ups', 11), ('Reverse Crunch', 11), ('Flutter Kick', 11),
    ('Scissor Crunch', 11),  ('Side Plank', 11),  ('Oblique V-ups', 11),  ('Russian Twists', 11), ('Bicycle Kicks', 11),
    ('V-tuck', 11), ('Superman', 11), ('Mountain Climber', 11)
]
master_exercises = [*push_exercises, *pull_exercises, *leg_exercises, *core_exercises]

def seed_muscles():
    for muscle in major_muscle_group:
        db.session.add(Muscle(name=muscle))
        db.session.commit()

def seed_exercises():
    for exercise in master_exercises:
        db.session.add(Exercise(name=exercise[0], muscle_id=exercise[1]))

seed_muscles()
seed_exercises()