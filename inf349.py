# inf349.py

from flask import Flask, jsonify
from CustomClass import Product, Order
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
    # Créer une commande
    order = Order.create(
        product=1,
        quantity=2,
        total_price=20.0
    )

    # Retourner un message de succès
    return jsonify({"message": "Order created successfully"})
