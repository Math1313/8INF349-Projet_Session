# tasks.py
import json, requests
from peewee import DoesNotExist
from rq import Queue
from CustomClass import db, Order, ProductOrder
from config import redis_client

# On crée la queue "default" en spécifiant la connexion redis
queue = Queue('default', connection=redis_client)

def do_payment(order_id, credit_card, amount_charged):
    """
    Fonction exécutée par le worker RQ en tâche de fond.
    """
    try:
        db.connect(reuse_if_open=True)
        order = Order.get_by_id(order_id)

        payment_response = requests.post(
            'https://dimensweb.uqac.ca/~jgnault/shops/pay/',
            json={
                "credit_card": credit_card,
                "amount_charged": amount_charged
            },
            headers={"Content-Type": "application/json"}
        )
        payment_data = payment_response.json()

        if payment_data.get("errors"):
            order.paid = False
            order.transaction = json.dumps({
                "success": False,
                "error": payment_data["errors"]
            })
        else:
            order.paid = payment_data["transaction"]["success"]
            order.credit_card = json.dumps(payment_data["credit_card"])
            order.transaction = json.dumps(payment_data["transaction"])

        order.save()

        if order.paid:
            # Mettre la commande dans Redis pour la résilience
            product_orders = ProductOrder.select().where(ProductOrder.order == order.id)
            products_list = []
            for po in product_orders:
                products_list.append({
                    "id": po.product.id,
                    "quantity": po.quantity
                })
            order_json = {
                "order": {
                    "id": order.id,
                    "total_price": order.total_price,
                    "total_price_tax": order.total_price_tax,
                    "email": order.email,
                    "credit_card": json.loads(order.credit_card),
                    "shipping_information": json.loads(order.shipping_information) if order.shipping_information else {},
                    "paid": True,
                    "transaction": json.loads(order.transaction),
                    "products": products_list,
                    "shipping_price": order.shipping_price
                }
            }
            redis_client.set(f"order:{order.id}", json.dumps(order_json))

    except DoesNotExist:
        print(f"Commande {order_id} introuvable.")
    except Exception as e:
        print(f"Erreur do_payment: {e}")
    finally:
        if not db.is_closed():
            db.close()
