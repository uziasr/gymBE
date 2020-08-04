import os

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    DEBUG = bool(int(os.environ.get('DEBUG')))

    def __repr__(self):
        return f"JWT_SECRET_KEY: {self.JWT_SECRET_KEY}, SQLALCHEMY_DATABASE_URI: {self.SQLALCHEMY_DATABASE_URI}"

    def __str__(self):
        return f"JWT_SECRET_KEY: {self.JWT_SECRET_KEY}, SQLALCHEMY_DATABASE_URI: {self.SQLALCHEMY_DATABASE_URI}"