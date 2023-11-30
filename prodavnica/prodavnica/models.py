from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProizvodKategorija(database.Model):
    __tablename__ = "proizvodikategorije"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("proizvodi.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("kategorije.id"), nullable=False)


class ProizvodOrder(database.Model):
    __tablename__ = "proizvodiorder"

    id = database.Column(database.Integer, primary_key=True)
    quantity = database.Column(database.Integer, nullable=False)
    productId = database.Column(database.Integer, database.ForeignKey("proizvodi.id"), nullable=False)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)


class Proizvod(database.Model):
    __tablename__ = "proizvodi"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)
    categories = database.relationship("Kategorija", secondary=ProizvodKategorija.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=ProizvodOrder.__table__, back_populates="products")


class Kategorija(database.Model):
    __tablename__ = "kategorije"

    id = database.Column(database.Integer, primary_key=True)
    nameKat = database.Column(database.String(256), nullable=False, unique=True)
    products = database.relationship("Proizvod", secondary=ProizvodKategorija.__table__, back_populates="categories")


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    customerId = database.Column(database.Integer, nullable=False)
    products = database.relationship("Proizvod", secondary=ProizvodOrder.__table__, back_populates="orders")
    emailCustomer = database.Column(database.String(256), nullable=False)
    status = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)
