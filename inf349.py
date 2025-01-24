# inf349.py

from flask import Flask, jsonify
import CustomClass

app = Flask(__name__)


@app.route('/hello')
def hello_world():
    return 'Hello, World!'


# Route pour récupérer tous les produits
@app.route('/', methods=['GET'])
def get_all_products():
    # Récupérer tous les produits
    products = CustomClass.Product.select()

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
