from app.models import Muscle, Exercise
from app import db

major_muscle_group = ['Quadriceps', 'Hamstrings',
                      'Calves', 'Chest',
                      'Back', 'Shoulders',
                      'Triceps', 'Biceps',
                      'Forearms', 'Trapezius',
                      'Abs']

leg_exercises = [
    ('leg press', 1),('squat', 1), ('leg extensions', 1),
    ('lunge', 1), ('goblet squat', 1), ('front squat', 1),
    ('deadlift', 2), ('leg curls', 2), ('Glute-Ham Raise', 2),
    ('Romanian deadlift', 2), ('hip thrust', 2), ('kettlebell swing', 2),
    ('standing calf raise', 3), ('seated calf raise', 3),
             ]

push_exercises = [
    ('barbell bench press', 4), ('dumbbell bench press', 4), ('incline barbell bench press', 4),
    ('incline dumbbell bench press', 4), ('decline barbell bench press', 4), ('decline dumbbell bench press', 4),
    ('cable crossover', 4), ('dumbbell fly', 4), ('machine flye', 4), ('low cable crossover', 4),
    ('underhand bench press', 4), ('wide-grip dips', 4), ('push ups', 4),
    ('shoulder barbell press', 6),  ('arnold dumbbell press', 6), ('push press', 6), ('lateral raise', 6),
    ('seated dumbbell shoulder press', 6), ('seat barbell shoulder press', 6), ('reverse pec fly', 6),
    ('dumbbell lateral raise', 6), ('reverse cable crossover', 6), ('one-arm cable lateral raise', 6),
    ('bent over reverse flye', 6),
    ('tricep kickbacks', 7), ('skull crushers', 7), ('dumbbell lying tricep extensions', 7), ('cable tricep push down', 7),
    ('cable tricep kickbacks', 7), ('tricep dips', 7),  ('overhead tricep extension', 7), ('pullover', 7), ('overhead cable tricep extension', 7)
                  ]

pull_exercises = [
    ('barbell bent over row', 5), ('dumbbell single arm row', 5), ('barbell bent over row underhand', 5), ('seated cable row', 5),
    ('pull ups', 5), ('lat pulldown', 5), ('incline dumbbell row', 5), ('chin ups', 5), ('inverted row', 5), ('T-bar rows', 5),
    ('back extensions', 5), ('rack pulls', 5),
    ('standing barbell curl', 8), ('concentration curl', 8), ('standing dumbbell curl', 8), ('hammer curl)', 8),
    ('decline dumbbel curl', 8), ('incline dumbbell curl', 8), ('cable bicep curl', 8),  ('preacher curl', 8),  ('machine curl', 8),
    ('e-z bar curl', 8),
    ('dumbbell wrist flexion', 9), ('dumbbell wrist extension', 9),
    ("farmer's carry", 10), ('face pulls', 10),  ('barbell shrug', 10), ('dumbbell shrug', 10), ('overhead barbell shrug', 10),
    ('dumbbell overhead carry', 10),
]

core_exercises = [
    ('plank', 11), ('crunch', 11),  ('vertical leg crunch', 11), ('v-up', 11), ('reverse crunch', 11), ('flutter kick', 11),
    ('scissor crunch', 11),  ('side plank', 11),  ('oblique v-up', 11),  ('russian twists', 11), ('bicycle kicks', 11),
    ('v-tuck', 11), ('superman', 11), ('mountain climber', 11)
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