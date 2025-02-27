
from peewee import (
    ForeignKeyField,
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
    email = CharField(null=True)
    total_price = DoubleField(null=True)
    total_price_tax = DoubleField(null=True)
    credit_card = CharField(null=True)
    shipping_information = CharField(null=True)
    paid = BooleanField(null=True)
    transaction = CharField(null=True)
    shipping_price = DoubleField(null=True)

    class Meta:
        database = db


class ProductOrder(db.Model):
    id = IntegerField(primary_key=True)
    order = ForeignKeyField(Order, backref='product_orders')
    product = ForeignKeyField(Product, backref='orders')
    quantity = IntegerField()

    class Meta:
        database = db
