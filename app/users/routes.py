from flask import Blueprint, request, jsonify
from app import create_access_token, hashing, db, jsonify_object
from app.models import *
from datetime import datetime, timedelta

user = Blueprint('user', __name__, url_prefix='/user')


# START For user registration and login
@user.route('/register', methods=['POST'])
def create_user():
    user_info = request.get_json()
    if "password" not in user_info or "email" not in user_info or "name" not in user_info:
        return {
            "error": "You are missing one or both of the required fields: password, email"
               }, 400
    if len(User.query.filter_by(email=user_info["email"]).all()) >= 1:
        return {
            "error": "this email has already been taken"
        }, 400
    hashed_password = hashing.hash_value(user_info["password"], salt="salt")
    db.session.add(User(name=user_info['name'], email=user_info['email'], password=hashed_password))
    db.session.commit()
    newly_created_user = User.query.filter_by(email=user_info["email"]).first()
    jsonified_user = jsonify_object(newly_created_user, User, ["password"])
    expires = timedelta(days=365)
    token = create_access_token(identity=newly_created_user.id, expires_delta = expires)
    return {
               "token": token,
                **jsonified_user
           }, 201


@user.route('/login', methods=["POST"])
def sign_in():
    user_info = request.get_json()
    if "password" not in user_info or "email" not in user_info:
        return {
            "error": "You are missing one or both of the required fields: password, email"
               }, 400
    saved_user = User.query.filter_by(email=user_info["email"]).first()
    if saved_user is None:
        return {
            "error": "A user by that email of '{}' does not exist".format(user_info["email"])
               }, 400
    # if hashing.check_value(h, "password", salt="hello)"
    if hashing.check_value(saved_user.password, user_info["password"], salt="salt"):
        expires = timedelta(days=365)
        token = create_access_token(identity=saved_user.id, expires_delta = expires)
        return {
                   "token": token,
                    **jsonify_object(saved_user, User, ["password"])
               }, 200
    else:
        return {
            "Error": "That is an incorrect password"
        }, 500
