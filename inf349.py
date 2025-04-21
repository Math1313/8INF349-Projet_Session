# inf349.py

from flask import Flask, request, jsonify, make_response
from config import redis_client
from CustomClass import Product, Order, ProductOrder, db
import json, requests
from tasks import queue, do_payment  # Import de la queue RQ et la fonction
from rq.worker import Worker

app = Flask(__name__)


def sanitize(value):
    # Supprimer tous les caractères NUL
    if value is None:
        return None
    return value.replace('\x00', '')


def import_products_from_url():
    url = "https://dimensweb.uqac.ca/~jgnault/shops/products/"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()  # Charger les données JSON
        for item in json_data['products']:
            print("Importing:", item) # Afficher chaque produit importé
            if 'id' not in item or item['id'] is None:
                print("Problème : item sans 'id' => on saute")
                continue
            # Ajouter chaque élément dans la base de données
            Product.create(
                id=item['id'],
                name=sanitize(item['name']),
                type=sanitize(item['type']),
                description=sanitize(item['description']),
                image=sanitize(item['image']),
                height=item['height'],
                weight=item['weight'],
                price=item['price'],
                in_stock=item['in_stock']
            )
        print("Base de données initialisée et produits importés avec succès!")
    else:
        print(f"Erreur lors de la récupération des données : {
        response.status_code}")

# Initialiser la base de données
@app.cli.command("init-db")
def init_db():
    # 1) Se connecter à la base Postgres
    db.connect(reuse_if_open=True)
    # Supprimer puis recréer
    db.drop_tables([Product, Order, ProductOrder])
    # 2) Créer les tables
    db.create_tables([Product, Order, ProductOrder])
    # 3) Facultatif : Importer la liste des produits
    import_products_from_url()


@app.route('/index')
def index():
    return app.send_static_file('index.html')


# worker RQ
@app.cli.command("worker")
def worker():
    """
    Lance un worker RQ sur la queue 'default'.
    On passe directement redis_client au Worker.
    """
    w = Worker(
        queues=[queue],
        connection=redis_client
    )
    w.work()

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
    return jsonify({"products": products_list}), 200


# Route pour créer une commande 
@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()

        # Vérifier s'il y a "products" (tableau) ou "product" (unique)
        products_array = data.get('products')
        single_product = data.get('product')

        # Si on a "products", c’est la nouvelle forme
        if products_array:
            # Valider qu'il n'est pas vide
            if not isinstance(products_array, list) or len(products_array) == 0:
                return return_error("missing-fields", "Aucun produit specifie", 422)

            # Calculer total_price et shipping
            total_price = 0
            total_weight = 0
            for item in products_array:
                prod_id = item.get("id")
                qty = item.get("quantity")
                if not prod_id or not qty:
                    return return_error("missing-fields", "Produit ou quantité manquant", 422)

                if qty < 1:
                    return return_error("invalid-quantity", "La quantité doit être >= 1", 422)

                # Vérifier si le produit existe et est en stock
                try:
                    product = Product.get_by_id(prod_id)
                except:
                    return return_error("not_found", f"Le produit {prod_id} n'existe pas", 404)

                if not product.in_stock:
                    return return_error("out-of-inventory", f"Le produit {prod_id} n'est pas en inventaire", 422)

                total_price += product.price * qty
                total_weight += product.weight * qty

            # Créer la commande
            order = Order.create(
                total_price=total_price,
                shipping_price=get_shipping_price(total_weight, 1),  # ou un param custom
                paid=False
            )

            # Créer les enregistrements ProductOrder
            for item in products_array:
                prod_id = item["id"]
                qty = item["quantity"]
                ProductOrder.create(order=order, product=prod_id, quantity=qty)

            # Retourner la réponse
            resp = make_response(jsonify({}))
            resp.status_code = 302
            resp.headers["Location"] = f"/order/{order.id}"
            return resp

        # Sinon, on gère l'ancien format "product" (rétrocompatibilité.)
        elif single_product:
            product_data = single_product
            if not product_data.get('id') or not product_data.get('quantity'):
                return return_error("missing-fields", "La création d'une commande nécessite un produit", 422)
        
            # Vérifier si le produit existe, etc.
            try:
                product = Product.get(Product.id == product_data['id'])
                if not product.in_stock:
                    return return_error("out-of-inventory", "Le produit n'est pas en inventaire", 422)
            except:
                return return_error("not_found", "Le produit n'existe pas", 404)
        
            total_price = product.price * product_data['quantity']
            shipping_price = get_shipping_price(product.weight, product_data['quantity'])
        
            order = Order.create(
                total_price=total_price,
                shipping_price=shipping_price,
                paid=False
            )
            ProductOrder.create(order=order, product=product.id, quantity=product_data['quantity'])
        
            resp = make_response(jsonify({}))
            resp.status_code = 302
            resp.headers["Location"] = f"/order/{order.id}"
            return resp

        else:
            return return_error("missing-fields", "Aucun champ 'product' ou 'products' trouvé", 422)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour récupérer une commande spécifique
@app.route('/order/<int:id>', methods=['GET'])
def get_specific_order(id):
# Vérifier d'abord si c'est dans Redis.
    # 1) Vérifier si la commande est déjà en cache
    cached_data = redis_client.get(f"order:{id}")
    if cached_data:
    # 2) La commande est payée, on renvoie le JSON direct
        return make_response(cached_data, 200, {"Content-Type": "application/json"})
    # Si non, on interroge Postgres :
    order = Order.get_or_none(Order.id == id)
    if not order:
        return return_error("not_found", "Commande introuvable", 404)
    # S'il est IN_PROGRESS, on renvoie 202 Accepted (vide)
    if order.payment_status == "IN_PROGRESS":
        return make_response("payment en cours ", 202)

    # Sélectionner tous les ProductOrder de cette commande
    product_orders = ProductOrder.select().where(ProductOrder.order == order.id)
    products_list = []
    grand_total = None
    if order.total_price_tax is not None and order.shipping_price is not None:
        grand_total = order.total_price_tax + order.shipping_price
    
    for po in product_orders:
        products_list.append({
            "id": po.product.id,
            "quantity": po.quantity
        })

    return jsonify({
        "order": {
            "id": order.id,
            "total_price": order.total_price,
            "total_price_tax": order.total_price_tax,
            "email": order.email,
            "credit_card": json.loads(order.credit_card) if order.credit_card else {},
            "shipping_information": json.loads(order.shipping_information) if order.shipping_information else {},
            "paid": order.paid,
            "transaction": json.loads(order.transaction) if order.transaction else {},
            "products": products_list, 
            "shipping_price": order.shipping_price,
            "grand_total": grand_total,
        
        }
    }), 200


# Route pour mettre à jour une commande
@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        order = Order.get_or_none(Order.id == order_id)
        if not order:
            return return_error("not_found", "Commande introuvable", 404)

        # Si la commande est déjà payée, on ne peut plus la modifier
        if order.paid:
            return return_error("already-paid", "La commande a deja ete payee", 422)

        data = request.get_json()

        # 1) Vérifier s'il y a un champ "credit_card" + "amount_charged"
        if "credit_card" in data and data.get("amount_charged"):
            # Vérifier que la commande n'est pas déjà en cours de paiement
            if order.payment_status == "IN_PROGRESS":
                return return_error("conflict", "Commande dejà en cours de paiement", 409)

            # Vérifier que les infos d'expédition existent déjà
            if not order.shipping_information:
                return return_error(
                    "missing_shipping",
                    "Les informations d'expédition sont requises avant d'ajouter une carte de crédit",
                    422
                )

            credit_card = data["credit_card"]
            amount_charged = data["amount_charged"]

            required_cc_fields = [
                credit_card.get("name"),
                credit_card.get("number"),
                credit_card.get("expiration_year"),
                credit_card.get("expiration_month"),
                credit_card.get("cvv"),
                amount_charged
            ]
            if not all(required_cc_fields):
                return return_error("missing_fields", "Information de carte de crédit incomplete", 422)

            # (Même validations que tu faisais avant)
            if not isinstance(credit_card.get("cvv"), str) or len(credit_card.get("cvv")) != 3:
                return return_error("invalid-cvv", "Le CVV doit être une chaîne de 3 chiffres", 422)

            # etc. (expiration_year, expiration_month, etc.)

            # Vérifier que (total_price_tax + shipping_price) == amount_charged
            if order.total_price_tax + order.shipping_price != amount_charged:
                return return_error("invalid-amount", "Le montant paye doit être égal au total de la commande", 422)

            # 2) Marquer la commande en cours de paiement
            order.payment_status = "IN_PROGRESS"
            order.save()

            # 3) Enquêter la tâche asynchrone dans RQ
            #    -> do_payment(order_id, credit_card, amount_charged)
            from tasks import queue, do_payment
            queue.enqueue(do_payment, order.id, credit_card, amount_charged)

            # 4) Retourner 202 Accepted immédiatement
            return make_response("", 202)

        # Sinon, on met à jour les infos d'expédition
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
        if not all(required_fields):
            return return_error("missing_fields", "Il manque un ou plusieurs champs obligatoires", 422)

        # Mettre à jour la commande
        order.email = order_data.get("email")
        order.total_price_tax = round(order.total_price * get_taxes_rate(shipping_data.get("province")), 2)
        order.shipping_information = json.dumps(shipping_data)
        order.save()

        # Retourne la commande (toujours 200 OK)
        return get_specific_order(order_id)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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