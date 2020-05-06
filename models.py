import sqlite3
# from flask import Flask
# app = Flask(__name__)


# from app import app

class Schema:
    def __init__(self):
        self.conn = sqlite3.connect('gym.db3')
        self.create_users_table()
        self.create_muscle_group_table()
        self.create_exercises_table()
        self.create_workout_table()
        self.create_sets_table()

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Users" (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
        );
        """
        self.conn.execute(query)

    def create_muscle_group_table(self):
        muscle_query = """
        CREATE TABLE IF NOT EXISTS "Muscle_Group" (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
        );
        """
        self.conn.execute(muscle_query)

    def create_exercises_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Exercises" (
        id INTEGER PRIMARY KEY,
        muscle_group_id INTEGER NOT NULL,
        name TEXT UNIQUE,
        FOREIGN KEY (muscle_group_id) REFERENCES Muscle_Group (id)
        );
        """
        self.conn.execute(query)

    def create_workout_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Workouts" (
        id INTEGER PRIMARY KEY NOT NULL,
        user_id INTEGER NOT NULL,
        muscle_group_id INTEGER NOT NULL,
        start_time DATE DEFAULT CURRENT_DATE,
        end_time DATE,
        FOREIGN KEY (user_id) REFERENCES Users (id),
        FOREIGN KEY (muscle_group_id) REFERENCES Muscle_Group (id)
        );
        """
        self.conn.execute(query)

    def create_sets_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Sets" (
        id INTEGER PRIMARY KEY,
        exercise_id INTEGER  NOT NULL,
        workout_id INTEGER NOT NULL,
        repetition INTEGER NOT NULL,
        _order INTEGER NOT NULL,
        weight INTEGER NOT NULL,
        unit TEXT NOT NULL,
        FOREIGN KEY (exercise_id) REFERENCES Exercises (id),
        FOREIGN KEY (workout_id) REFERENCES Workouts (id)
        );
        """
        self.conn.execute(query)
