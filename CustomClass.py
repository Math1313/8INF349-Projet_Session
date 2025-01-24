
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
