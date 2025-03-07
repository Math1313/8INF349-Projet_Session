import json
import pytest
from CustomClass import Product, Order, ProductOrder

@pytest.mark.usefixtures("test_app", "test_db")
class TestFunctionalRoutes:
    """
    Tests fonctionnels pour vérifier les endpoints via le client Flask.
    On utilise les fixtures test_app et test_db pour avoir
    - une base de données de test
    - un client Flask pour envoyer des requêtes
    """

    def test_get_all_products_empty(self, test_app):
        """Au début, la liste de produits est vide si on n'a rien inséré."""
        resp = test_app.get('/')
        assert resp.status_code == 200
        data = resp.get_json()
        #assert data == []  # Aucun produit dans la DB
        assert data["products"] == []
        
    def test_create_product_in_db_then_get(self, test_app):
        """On insère manuellement un produit dans la DB, puis on vérifie qu'il apparaît."""
        Product.create(
            id=1,
            name="Brown eggs",
            type="Food",
            description="Raw organic brown eggs in a basket",
            image="0.jpg",
            height=10,
            weight=400,
            price=28.1,
            in_stock=True
        )
        resp = test_app.get('/')
        assert resp.status_code == 200
        data = resp.get_json()
        #assert len(data) == 1
        #assert data[0]["id"] == 1
        assert len(data["products"]) == 1
        assert data["products"][0]["id"] == 1
        assert data["products"][0]["name"] == "Brown eggs"

    def test_create_order_missing_fields(self, test_app):
        """POST /order sans champ 'product' doit retourner 422."""
        resp = test_app.post('/order', json={})
        assert resp.status_code == 422
        data = resp.get_json()
        assert "errors" in data
        assert data["errors"]["order"]["code"] == "missing-fields"

    def test_create_order_ok(self, test_app):
        """
        POST /order correctement formé => doit créer l'ordre
        et renvoyer un code 302 avec la location de l'order.
        """
        # On insère d'abord un produit en stock
        Product.create(
            id=2, name="Strawberry", type="Fruit",
            description="Fresh stawberry", image="1.jpg",
            height=5, weight=299, price=29.45, in_stock=True
        )

        payload = {
            "product": {
                "id": 2,
                "quantity": 3
            }
        }
        resp = test_app.post('/order', json=payload)
        # Selon votre code, vous renvoyez "Location: /order/<product_order.id>" en texte
        # avec un code 302
        assert resp.status_code == 302
        # On peut vérifier le contenu
        #assert b"Location: /order/" in resp.data
        # Vérifier l'en-tête Location:
        assert resp.headers["Location"].startswith("/order/")
        
        
        # Vérifions en base qu'un Order a bien été créé
        orders = list(Order.select())
        assert len(orders) == 1
        assert orders[0].paid == False

        # Vérifions que le product_order est créé
        product_orders = list(ProductOrder.select())
        assert len(product_orders) == 1
        assert product_orders[0].quantity == 3

    def test_create_order_out_of_stock(self, test_app):
        """Si le produit n'est pas en stock, on doit renvoyer 422 + 'out-of-inventory'."""
        Product.create(
            id=3, name="OutOfStock Product", type="Test",
            description="Desc", image="img.jpg",
            height=5, weight=500, price=10, in_stock=False
        )

        resp = test_app.post('/order', json={
            "product": {
                "id": 3,
                "quantity": 1
            }
        })
        assert resp.status_code == 422
        data = resp.get_json()
        assert data["errors"]["order"]["code"] == "out-of-inventory"

    def test_get_specific_order_ok(self, test_app):
        """Création d'une commande, puis GET /order/<id>."""
        product = Product.create(
            id=10, name="Laptop", type="Computer",
            description="A laptop", image="laptop.jpg",
            height=5, weight=1000, price=100.0, in_stock=True
        )
        order = Order.create(
            id=999, total_price=300.0, total_price_tax=None,
            email=None, credit_card=None, shipping_information=None,
            paid=False, transaction=None, shipping_price=5.0
        )
        # On crée le lien product-order
        ProductOrder.create(
            id=101,
            order=order,
            product=product,
            quantity=3
        )

        resp = test_app.get('/order/999')
        assert resp.status_code == 200
        data = resp.get_json()
        assert "order" in data
        assert data["order"]["id"] == 999
        assert data["order"]["product"]["id"] == product.id
        assert data["order"]["product"]["quantity"] == 3

    def test_get_specific_order_not_found(self, test_app):
        """GET /order/<id> inexistant => 404."""
        resp = test_app.get('/order/12345')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["errors"]["order"]["code"] == "not_found"
        assert data["errors"]["order"]["name"] == "Commande introuvable"
