# inf349.py

from flask import Flask, request, jsonify
from CustomClass import Product, Order, ProductOrder
import create_database

app = Flask(__name__)


@app.cli.command("init-db")
def init_db():
    """Initialise la base de données."""
    # Ajoute ici toutes les tables nécessaires
    create_database.create_database()
    print("Base de données initialisée avec succès.")


@app.route('/hello')
def hello_world():
    return 'Hello, World!'


# Route pour récupérer tous les produits
@app.route('/', methods=['GET'])
def get_all_products():
    # Récupérer tous les produits
    products = Product.select()

    # Convertir en liste de dictionnaires
    products_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "image": product.image,
            "height": product.height,
            "weight": product.weight,
            "price": product.price,
            "in_stock": product.in_stock
        }
        for product in products
    ]

    # Retourner les données en JSON
    return jsonify(products_list)


@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        product_data = data.get('product')

        if not product_data or not product_data.get('id') or not product_data.get('quantity'):
            return jsonify({"errors": {
                "product": {
                    "code": "missing_fields",
                    "name": "La création d'une commande nécessite un produit."
                }
            }}), 422

        try:
            Product.get(Product.id == product_data.get('id'))
        except Exception:
            return jsonify({"errors": {
                "product": {
                    "code": "not_found",
                    "name": "Le produit n'existe pas."
                }
            }}), 422

        order = Order.create()

        product_order = ProductOrder.create(
            order=order, product=product_data.get('id'),
            quantity=product_data.get('quantity'))

        # TODO: RETOURNER LA ROUTE DE LA NOUVELLE COMMANDE. (Ex: /order/<id_commande>)
        return f"ID_COMMANDE: {product_order.id}", 302

    except Exception as e:
        return jsonify({"error": str(e)}), 500
