import os
from peewee import PostgresqlDatabase
from peewee import AutoField

# Récupérer les variables d'environnement
DB_NAME = os.getenv('DB_NAME', 'api8inf349')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'pass')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))

db = PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

from peewee import (
    Model,
    IntegerField,
    AutoField,
    CharField,
    DoubleField,
    ForeignKeyField,
    BooleanField
)


class Product(db.Model):
    id = IntegerField(primary_key=True)
    name = CharField()
    type = CharField()
    description = CharField()
    image = CharField()
    height = IntegerField()
    weight = IntegerField()
    price = DoubleField()
    in_stock = BooleanField()

    class Meta:
        database = db


class Order(db.Model):
    id = AutoField(primary_key=True)
    email = CharField(null=True)
    total_price = DoubleField(null=True)
    total_price_tax = DoubleField(null=True)
    credit_card = CharField(null=True)
    shipping_information = CharField(null=True)
    paid = BooleanField(null=True)
    transaction = CharField(null=True)
    shipping_price = DoubleField(null=True)
    payment_status = CharField(null=True)  

    class Meta:
        database = db


class ProductOrder(db.Model):
    id = AutoField(primary_key=True)
    order = ForeignKeyField(Order, backref='product_orders')
    product = ForeignKeyField(Product, backref='orders')
    quantity = IntegerField()

    class Meta:
        database = db
