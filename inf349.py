# inf349.py

from flask import Flask, request, jsonify
from CustomClass import Product, Order, ProductOrder
import create_database
import json, requests

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


# Route pour créer une commande
@app.route('/order', methods=['POST'])
def create_order():
    try:
        # Récupérer les données JSON envoyées par le client
        data = request.get_json()
        product_data = data.get('product')

        # Vérifier si les données sont valides (présence des champs)
        if not product_data or not product_data.get('id') or not product_data.get('quantity'):
            return return_error("missing-fields", "La création d'une commande nécessite un produit", 422)

        # Vérifier si quantité négative ou 0
        if product_data.get('quantity') < 1:
            return return_error("missing-fields", "Quantité invalide", 422)
        # Vérifier si le produit existe dans la base de données
        try:
            product = Product.get(Product.id == product_data.get('id'))
            # Vérifier si le produit est en inventaire
            print(product.in_stock)
            if not product.in_stock:
                return return_error("out-of-inventory", "Le produit demandé n'est pas en inventaire", 422)
        except Exception:
            # Retourner une erreur si le produit n'existe pas
            return return_error("not_found", "Le produit n'existe pas", 404)

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


# Route pour récupérer une commande spécifique
@app.route('/order/<int:id>', methods=['GET'])
def get_specific_order(id):
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
                "credit_card": json.loads(order.credit_card) if order.credit_card else {},
                "shipping_information": json.loads(order.shipping_information) if order.shipping_information else {},
                "paid": order.paid,
                "transaction": json.loads(order.transaction) if order.transaction else {},
                "product":
                {
                    "id": product_order.product_id,
                    "quantity": product_order.quantity
                },
                "shipping_price": order.shipping_price
            }

        }), 200
    except Exception as e:
        return return_error ("not_found", "Commande introuvable", 404)


# Route pour mettre à jour une commande
@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        # Récupérer les informations de la commandes
        order = Order.get_or_none(Order.id == order_id)
        if not order:
            return return_error("not_found", "Commande introuvable", 404)

        if order.paid:
            return return_error("already-paid", "La commande a déjà été payée", 422)
        data = request.get_json()
        
        # Vérifier si l'update doit mettre à jour les informations de paiement
        if "credit_card" in data and data.get("amount_charged"):
            if not order.shipping_information:
                return return_error("missing_shipping",
                                    "Les informations d'expédition sont requises avant d'ajouter une carte de crédit",
                                    422)

            credit_card = data["credit_card"]
            
            required_cc_fields = [
                credit_card.get("name"),
                credit_card.get("number"),
                credit_card.get("expiration_year"),
                credit_card.get("expiration_month"),
                credit_card.get("cvv"),
                data.get("amount_charged")
            ]

            # Valider que tous les champs de la carte de crédit sont présents
            if not all(required_cc_fields):
                return return_error("missing_fields", "Information de carte de crédit incomplète", 422)
            
            # Valider que le CVV est une chaîne de 3 chiffres
            if not isinstance(credit_card.get("cvv"), str) or not credit_card.get("cvv").isdigit() or len(credit_card.get("cvv")) != 3:
                return return_error("invalid-cvv", "Le CVV doit être une chaîne de 3 chiffres", 422)

            # Valider que l'année et le mois sont des entiers
            if not isinstance(credit_card.get("expiration_year"), int) or not isinstance(credit_card.get("expiration_month"), int):
                return return_error("invalid-expiration-date", "L'année et le mois d'expiration doit être un nombre entier", 422)
                
            # Valider que le montant chargé est un nombre décimal
            if not isinstance(data.get("amount_charged"), (float, int)):
                return return_error("invalid-amount", "Le montant doit être un nombre décimal", 422)
            
            if order.total_price_tax + order.shipping_price != data["amount_charged"]:
                return return_error("invalid-amount", "Le montant payé doit être égal au total de la commande", 422)

            # Faire une requête de paiement à l'API externe
            try:
                payment_response = requests.post(
                    'https://dimensweb.uqac.ca/~jgnault/shops/pay/',
                    json={
                        "credit_card": credit_card,
                        "amount_charged": data["amount_charged"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                payment_data = payment_response.json()
                
                # Valider les erreurs si le paiement a échoué
                if payment_data.get("errors"):
                    # Retourner une erreur si le numéro de la carte de crédit est invalide
                    if payment_data.get("errors").get("credit_card").get("code") == "card-invalid":
                        return return_error("card-declined", "La carte de crédit a été déclinée", 422)
                    
                    # Retourner une erreur si la carte de crédit est expirée
                    elif payment_data.get("errors").get("credit_card").get("code") == "card-expired":
                        return return_error("card-expired", "La carte de crédit est expirée", 422)
                
                # Enregistrer les informations de paiement
                order.credit_card = json.dumps(payment_data["credit_card"])
                order.transaction = json.dumps(payment_data["transaction"])
                order.paid = payment_data["transaction"]["success"]
                order.save()
                
                # Retourner les informations de la commande
                return get_specific_order(order_id)

            # Retourner une erreur si le paiement a échoué    
            except Exception as e:
                return return_error("payment_error", "Erreur lors du traitement du paiement", 500)

        # Vérifier si l'update doit mettre à jour les informations d'expédition
        order_data = data.get("order")
        if not order_data:
            return return_error("missing_fields", "Les données de commande sont requises", 422)

        shipping_data = order_data.get("shipping_information", {})
        required_fields = [
            shipping_data.get("province"),
            shipping_data.get("city"),
            shipping_data.get("address"),
            shipping_data.get("postal_code"),
            shipping_data.get("country"),
            order_data.get("email")
        ]

        # Valider que tous les champs de l'expédition sont présents
        if not all(required_fields):
            return return_error("missing_fields", "Il manque un ou plusieurs champs qui sont obligatoires", 422)
        
        # Mettre à jour les informations de la commande
        order.email = order_data.get("email")
        order.total_price_tax = round(order.total_price * get_taxes_rate(shipping_data.get("province")), 2)
        order.shipping_information = json.dumps(shipping_data)
        order.save()
        
        return get_specific_order(order_id)

    # Retourner une erreur si la commande n'existe pas
    # Ce bloc attrapera toutes les autres erreurs potentielles qui ne sont pas gérées
    except Exception as e:
        return jsonify({"error": "Commande introuvable"}), 404


# Fonctions utilitaires pour les calculs
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

def return_error(error_code, error_name, http_code):
    return jsonify({
        "errors": {
            "order": {
                "code": error_code,
                "name": error_name
            }
        }
    }), http_code