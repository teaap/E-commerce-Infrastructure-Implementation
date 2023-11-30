import csv
import io

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

ispravnacena = r'\b(0*[1-9]\d*(\.\d+)?([eE][-+]?\d+)?)\b'


@application.route("/search", methods=["GET"])
@jwt_required()
def search():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    prov = get_jwt()
    if int(prov['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    product = request.args.get('name')
    category = request.args.get('category')
    if product is None:
        product = ''
    if category is None:
        category = ''
    categories = Kategorija.query.filter(
        Kategorija.nameKat.like(f"%{category}%")
    ).all()
    products = Proizvod.query.filter(
        Proizvod.name.like(f"%{product}%")
    ).all()
    listakat = []
    listapro = []
    for citem in categories:
        for pitem in products:
            prodcat = ProizvodKategorija.query.filter(
                and_(ProizvodKategorija.categoryId == citem.id, ProizvodKategorija.productId == pitem.id)).first()
            if prodcat:
                listakat.append(citem)
                listapro.append(pitem)

    listakatnova = list(set(listakat))
    listapronova = list(set(listapro))
    listapovpro = []
    for item in listapronova:
        kategorije = Kategorija.query.join(ProizvodKategorija).join(Proizvod).filter(Proizvod.id == item.id).all()
        katname = []
        for it in kategorije:
            katname.append(it.nameKat)
        listapovpro.append({
            "categories": katname,
            "id": item.id,
            "name": item.name,
            "price": item.price
        })

    listakat = []
    for item in listakatnova:
        listakat.append(item.nameKat)
    pov = {
        "categories": listakat,
        "products": listapovpro
    }

    return jsonify(pov), 200


@application.route("/order", methods=["POST"])
@jwt_required()
def order():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    prov = get_jwt()
    if int(prov['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    try:
        content = request.json["requests"]
    except Exception as e:
        return jsonify({'message': 'Field requests is missing.'}), 400
    requests = request.json["requests"]

    i = -1
    uspesniorderi = []

    for ind, item in enumerate(requests):
        i = i + 1
        if "id" not in item:
            return jsonify({'message': f'Product id is missing for request number {i}.'}), 400
        if "quantity" not in item:
            return jsonify({'message': f'Product quantity is missing for request number {i}.'}), 400
        if not re.match(r'\b[1-9][0-9]*\b', str(item["id"])):
            return jsonify({'message': f'Invalid product id for request number {i}.'}), 400
        if not re.match(r'\b[1-9][0-9]*\b', str(item["quantity"])):
            return jsonify({'message': f'Invalid product quantity for request number {i}.'}), 400
        p = Proizvod.query.filter(Proizvod.id == item["id"]).first()
        if not p:
            return jsonify({'message': f'Invalid product for request number {i}.'}), 400
        uspesniorderi.append([item["id"], item["quantity"]])

    customerid = int(get_jwt()["id"])
    timestamp = datetime.datetime.utcnow().isoformat()
    status = 'CREATED'
    emailCustomer = get_jwt_identity()
    o = Order(customerId=customerid, timestamp=timestamp, status=status, emailCustomer=emailCustomer)
    database.session.add(o)
    database.session.commit()
    for item in uspesniorderi:
        product = ProizvodOrder(quantity=item[1], productId=item[0], orderId=o.id)
        database.session.add(product)
        database.session.commit()
    return jsonify({'id': o.id}), 200


@application.route("/status", methods=["GET"])
@jwt_required()
def status():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    prov = get_jwt()
    if int(prov['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    provera = get_jwt()["id"]
    orders = Order.query.filter(Order.customerId == provera).all()
    povratna = {
        "orders": []
    }
    for item in orders:
        time = item.timestamp
        order = {
            "products": [],
            "price": 0,
            "status": item.status,
            "timestamp": time
        }
        proizvodi = ProizvodOrder.query.filter(ProizvodOrder.orderId == item.id).all()
        ukupna_cena = 0
        for proizvod in proizvodi:
            proiz = {"categories": [], "name": "", "price": 0, "quantity": proizvod.quantity}
            p = Proizvod.query.filter(Proizvod.id == proizvod.productId).first()
            proiz["name"] = p.name
            proiz["price"] = p.price
            ukupna_cena += p.price * proizvod.quantity
            kategorije = Kategorija.query.join(ProizvodKategorija).filter(
                ProizvodKategorija.productId == proizvod.productId).all()
            for kat in kategorije:
                proiz["categories"].append(kat.nameKat)
            order["products"].append(proiz)
        order["price"] = ukupna_cena
        povratna["orders"].append(order)

    return jsonify(povratna), 200


@application.route("/delivered", methods=["POST"])
@jwt_required()
def delivered():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    prov = get_jwt()
    if int(prov['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    try:
        content = request.json["id"]
    except Exception as e:
        return jsonify({'message': 'Missing order id.'}), 400
    requests = request.json["id"]

    if not re.match(r'\b[1-9][0-9]*\b', str(requests)):
        return jsonify({'message': 'Invalid order id.'}), 400

    o = Order.query.filter(and_(Order.id == requests, Order.status == "PENDING")).first()
    if not o:
        return jsonify({'message': 'Invalid order id.'}), 400

    o.status = "COMPLETE"
    database.session.commit()
    return jsonify({}), 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
