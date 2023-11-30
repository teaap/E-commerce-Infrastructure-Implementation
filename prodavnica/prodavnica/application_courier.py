from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Proizvod, Kategorija, ProizvodKategorija, Order, ProizvodOrder
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re
import datetime

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
def pick_up_order():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    prov = get_jwt()
    if int(prov['role']) != 3:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    try:
        content = request.json["id"]
    except Exception as e:
        return jsonify({'message': 'Missing order id.'}), 400
    requests = request.json["id"]

    if not re.match(r'\b[1-9][0-9]*\b', str(requests)):
        return jsonify({'message': 'Invalid order id.'}), 400

    o = Order.query.filter(and_(Order.id == requests, Order.status == "CREATED")).first()
    if not o:
        return jsonify({'message': 'Invalid order id.'}), 400

    o.status = "PENDING"
    database.session.commit()
    return jsonify({}), 200


@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
def orders_to_deliver():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    prov = get_jwt()
    if int(prov['role']) != 3:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    orders = Order.query.filter(Order.status == "CREATED").all()
    pov = {
        "orders": []
    }
    for item in orders:
        lista = {
            "id":item.id,
            "email":item.emailCustomer
        }
        pov["orders"].append(lista)
    return jsonify(pov), 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
