
from peewee import (
    SqliteDatabase,
    IntegerField,
    CharField,
    DoubleField,
    BooleanField
)

db = SqliteDatabase('products.db')


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
    id = IntegerField(primary_key=True)
    total_price = DoubleField()
    total_price_tax = DoubleField()
    credit_card = CharField()
    shipping_information = CharField()
    paid = BooleanField()
    transaction = CharField()
    shipping_price = DoubleField()

    class Meta:
        database = db


class ProductOrder(db.Model):
    id = IntegerField(primary_key=True)
    product = IntegerField()
    order = IntegerField()
    quantity = IntegerField()

    class Meta:
        database = db
