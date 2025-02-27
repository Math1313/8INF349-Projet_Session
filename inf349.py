# inf349.py

from flask import Flask, request, jsonify
from CustomClass import Product, Order, ProductOrder
import create_database
import json

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
    return jsonify(products_list), 200


# Route pour récupérer un produit par son ID
@app.route('/order', methods=['POST'])
def create_order():
    try:
        # Récupérer les données JSON envoyées par le client
        data = request.get_json()
        product_data = data.get('product')

        # Vérifier si les données sont valides (présence des champs)
        if not product_data or not product_data.get('id') or not product_data.get('quantity'):
            return jsonify({"errors": {
                "product": {
                    "code": "missing_fields",
                    "name": "La création d'une commande nécessite un produit."
                }
            }}), 422

        # Vérifier si quantité négative ou 0
        if product_data.get('quantity') < 1:
            return jsonify({"errors": {
                "product": {
                    "code": "missing-fields",
                    "name": "Quantité invalide"
            }}}), 422
        # Vérifier si le produit existe dans la base de données
        try:
            product = Product.get(Product.id == product_data.get('id'))
            # Vérifier si le produit est en inventaire
            print(product.in_stock)
            if not product.in_stock:
                return jsonify({"errors": {
                    "product": {
                        "code": "out-of-inventory",
                        "name": "Le produit demandé n'est pas en inventaire."
                    }
                }}), 422
        except Exception:
            # Retourner une erreur si le produit n'existe pas
            return jsonify({"errors": {
                "product": {
                    "code": "not_found",
                    "name": "Le produit n'existe pas."
                }
            }}), 422

        # Créer une nouvelle commande et une table de jonction avec le produit
        # TODO: Créer la nouvelle commande avec les paramètres nécessaires
        # total_price, total_price_tax, paid
        product = Product.get(Product.id == product_data.get('id'))
        total_price = product.price * product_data.get('quantity')

        order = Order.create(
            total_price=total_price,
            shipping_price=get_shipping_price(product.weight, product_data.get('quantity')),
            paid=False
            )
        product_order = ProductOrder.create(
            order=order, product=product_data.get('id'),
            quantity=product_data.get('quantity')
            )

        return f"Location: /order/{product_order.id}", 302

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/order/<int:id>', methods=['GET'])
def get_specific_product(id):
    try:
        product_order = ProductOrder.get(ProductOrder.order_id == id)
        order = Order.get(Order.id == product_order.order_id)

        return jsonify({
            "order":
            {
                "id": order.id,
                "total_price": order.total_price,
                "total_price_tax": order.total_price_tax,
                "email": order.email,
                "credit_card": {},
                "shipping_information": json.loads(order.shipping_information) if order.shipping_information else {},
                "paid": order.paid,
                "transaction": {},
                "product":
                {
                    "id": product_order.product_id,
                    "quantity": product_order.quantity
                },
                "shipping_price": order.shipping_price
            }

        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        return jsonify({"error": "Commande introuvable"}), 404

    data = request.get_json()
    order_data = data.get("order")
    shipping_data = order_data.get("shipping_information", {})
    if order_data.get("email"):
        order.email = order_data.get("email")
    if shipping_data:
        order.total_price_tax = round(order.total_price * get_taxes_rate(shipping_data.get("province")), 2)
        order.shipping_information = json.dumps(shipping_data)

    order.save()
    return jsonify({"order": order_data})


def get_taxes_rate(province):
    taxes = {
        "QC": 1.15,
        "ON": 1.13,
        "BC": 1.12,
        "AB": 1.05,
        "NS": 1.14
    }
    return taxes.get(province, 0.0)

def get_shipping_price(weight, quantity):
    if weight * quantity < 500:
        return 5.0
    elif weight * quantity < 2000:
        return 10.0
    else:
        return 25.0