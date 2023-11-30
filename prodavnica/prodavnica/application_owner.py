import csv
import io
import requests
from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Proizvod, Kategorija, ProizvodKategorija
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)

ispravnacena = r'\b(0*[1-9]\d*(\.\d+)?([eE][-+]?\d+)?)\b'


@application.route("/update", methods=["POST"])
@jwt_required()
def update():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    prov = get_jwt()
    if int(prov['role']) != 1:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    try:
        content = request.files["file"]
    except Exception as e:
        return jsonify({'message': 'Field file is missing.'}), 400

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    i = -1
    pomocna = []  # ime,cena
    lista = []  # ime proizvoda i ime kategorije
    for row in reader:
        i = i+1
        if len(row) < 3:
            return jsonify({'message': f'Incorrect number of values on line {i}.'}), 400
        kategorije = row[0].split('|')
        if not re.match(ispravnacena, row[2]):
            return jsonify({'message': f'Incorrect price on line {i}.'}), 400
        p = Proizvod.query.filter(Proizvod.name == row[1]).first()
        if p:
            return jsonify({'message': f'Product {row[1]} already exists.'}), 400
        temp1 = [row[1], float(row[2])]
        pomocna.append(temp1)
        for item in kategorije:
            temp = [row[1], item]
            lista.append(temp)
    for item in pomocna:
        database.session.add(Proizvod(name=item[0], price=item[1]))
        database.session.commit()

    for item in lista:
        k = Kategorija.query.filter(Kategorija.nameKat == item[1]).first()
        if not k:
            database.session.add(Kategorija(nameKat=item[1]))
            database.session.commit()
        katid = Kategorija.query.filter(Kategorija.nameKat == item[1]).first()
        prodid = Proizvod.query.filter(Proizvod.name == item[0]).first()
        database.session.add(ProizvodKategorija(categoryId=katid.id, productId=prodid.id))
        database.session.commit()

    return jsonify({}, 200)


@application.route("/product_statistics", methods=["GET"])
@jwt_required()
def product_statistics():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    prov = get_jwt()
    if int(prov['role']) != 1:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    response = requests.get(url='http://prodavnicaspark:5002/productstatistics')
    application.logger.info(response.text)

    return response.json()


@application.route("/category_statistics", methods=["GET"])
@jwt_required()
def category_statistics():
    ident = get_jwt_identity()
    if not ident:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    prov = get_jwt()
    if int(prov['role']) != 1:
        return jsonify({'msg': 'Missing Authorization Header'}), 401

    response = requests.get(url='http://prodavnicaspark:5002/categorystatistics')
    application.logger.info(response.text)

    return response.json()



@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
