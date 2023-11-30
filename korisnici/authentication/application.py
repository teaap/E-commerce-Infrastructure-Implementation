from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)

patternEmail = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'


@application.route("/register_customer", methods=["POST"])
def register_customer():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    if len(forename) == 0:
        return jsonify({'message': 'Field forename is missing.'}), 400

    if len(surname) == 0:
        return jsonify({'message': 'Field surname is missing.'}), 400

    if len(email) == 0:
        return jsonify({'message': 'Field email is missing.'}), 400

    if len(password) == 0:
        return jsonify({'message': 'Field password is missing.'}), 400

    if not re.match(patternEmail, email):
        return jsonify({'message': 'Invalid email.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Invalid password.'}), 400

    user = User.query.filter(User.email == email).first()

    if user:
        return jsonify({'message': 'Email already exists.'}), 400

    user = User(forename=forename, surname=surname, email=email, password=password, role=2)
    database.session.add(user)
    database.session.commit()

    return jsonify({}), 200


@application.route("/register_courier", methods=["POST"])
def register_courier():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    if len(forename) == 0:
        return jsonify({'message': 'Field forename is missing.'}), 400

    if len(surname) == 0:
        return jsonify({'message': 'Field surname is missing.'}), 400

    if len(email) == 0:
        return jsonify({'message': 'Field email is missing.'}), 400

    if len(password) == 0:
        return jsonify({'message': 'Field password is missing.'}), 400

    if not re.match(patternEmail, email):
        return jsonify({'message': 'Invalid email.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Invalid password.'}), 400

    user = User.query.filter(User.email == email).first()

    if user:
        return jsonify({'message': 'Email already exists.'}), 400

    user = User(forename=forename, surname=surname, email=email, password=password, role=3)
    database.session.add(user)
    database.session.commit()

    return jsonify({}), 200


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0:
        return jsonify({'message': 'Field email is missing.'}), 400
    if len(password) == 0:
        return jsonify({'message': 'Field password is missing.'}), 400

    if not re.match(patternEmail, email):
        return jsonify({'message': 'Invalid email.'}), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if not user:
        return jsonify({'message': 'Invalid credentials.'}), 400

    additionalClaims = {
        "forename": user.forename,
        "id": str(user.id),
        "surname": user.surname,
        "role": str(user.role)
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    # return Response ( accessToken, status = 200 );
    return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    user = User.query.filter(User.email == ident).first()
    if not user:
        return jsonify({'message': 'Unknown user.'}), 400

    database.session.delete(user)
    database.session.commit()

    return jsonify({}), 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid!"


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"]
    }

    return Response(create_access_token(identity=identity, additional_claims=additionalClaims), status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
