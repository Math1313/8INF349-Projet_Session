import os
import pytest
from inf349 import app
from peewee import SqliteDatabase
from CustomClass import db, Product, Order, ProductOrder

TEST_DB = 'test_products.db'

@pytest.fixture(scope='function')
def test_app():
    """
    Fixture pour l'application Flask,
    retourne un test client pour exécuter les requêtes.
    """
    # Configuration de l'application (si besoin)
    app.config.update({
        "TESTING": True,
        # Désactive les erreurs d'autorisation CSRF
        "WTF_CSRF_ENABLED": False,
    })

    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def test_db():
    if os.path.exists(TEST_DB):
        os.unlink(TEST_DB)

    test_database = SqliteDatabase(TEST_DB)

    # Pour que vos modèles (Product, Order...) pointent vers test_database,
    # vous pouvez faire un bind :
    test_database.bind([Product, Order, ProductOrder], bind_refs=False, bind_backrefs=False)
    test_database.connect()
    test_database.create_tables([Product, Order, ProductOrder])

    yield

    test_database.drop_tables([Product, Order, ProductOrder])
    test_database.close()
    if os.path.exists(TEST_DB):
        os.unlink(TEST_DB)
