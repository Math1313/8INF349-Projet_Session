# test_integration.py

import json
import pytest
from unittest.mock import patch, MagicMock
from CustomClass import Product, Order, ProductOrder

@pytest.mark.usefixtures("test_app", "test_db")
class TestIntegration:
    @patch("requests.post")
    def test_pay_order_ok(self, mock_post, test_app):
        """
        Test d'intégration : on met à jour la commande via PUT /order/<id>
        avec la credit_card et le amount_charged, en simulant
        un service de paiement qui renvoie une transaction réussie.
        """
        # 1) On crée un produit et une commande dans la DB de test
        product = Product.create(
            id=50,
            name="Keyboard",
            type="Computer",
            description="A mechanical keyboard",
            image="kb.jpg",
            height=2,
            weight=500,
            price=100.0,
            in_stock=True
        )
        order = Order.create(
            id=123,
            total_price=200.0,      # ex: 2 x 100
            total_price_tax=None,
            email=None,
            credit_card=None,
            shipping_information=None,
            paid=False,
            transaction=None,
            shipping_price=10.0     # ex: 2 x 500g => 10$
        )
        ProductOrder.create(
            id=99,
            order=order,
            product=product,
            quantity=2
        )

        # 2) On simule un service de paiement qui renvoie une transaction OK
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "credit_card": {
                "name": "John Doe",
                "first_digits": "4242",
                "last_digits": "4242",
                "expiration_year": 2024,
                "expiration_month": 9
            },
            "transaction": {
                "id": "ABCDE12345",
                "success": True,
                "amount_charged": 240.0  # 230 (tax) + 10 shipping
            }
        }
        mock_post.return_value = mock_response

        # 3) On met d'abord à jour l'email et l'adresse (PUT /order/123)
        update_data = {
            "order": {
                "email": "test@example.com",
                "shipping_information": {
                    "province": "QC",
                    "city": "Chicoutimi",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "country": "Canada"
                }
            }
        }
        resp = test_app.put('/order/123', json=update_data)
        assert resp.status_code == 200

        # Vérifions que la taxe est mise à jour (200 * 1.15 = 230)
        data = resp.get_json()
        assert data["order"]["total_price_tax"] == pytest.approx(230.0, 0.01)

        # 4) On paye la commande (PUT /order/123 avec credit_card + amount_charged)
        pay_data = {
            "credit_card": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",  # carte valide
                "expiration_year": 2024,
                "expiration_month": 9,
                "cvv": "123"
            },
            "amount_charged": 240.0  # 230 + 10 de shipping
        }
        resp2 = test_app.put('/order/123', json=pay_data)
        assert resp2.status_code == 200

        # 5) On vérifie que la commande est payée
        data2 = resp2.get_json()
        assert data2["order"]["paid"] is True
        assert data2["order"]["transaction"]["id"] == "ABCDE12345"

        # Vérifions que "requests.post" a bien été appelé avec le bon JSON
        mock_post.assert_called_once_with(
            'https://dimensweb.uqac.ca/~jgnault/shops/pay/',
            json={
                "credit_card": pay_data["credit_card"],
                "amount_charged": 240.0
            },
            headers={"Content-Type": "application/json"}
        )

    @patch("requests.post")
    def test_pay_order_card_declined(self, mock_post, test_app):
        """
        Test d'intégration : carte de crédit refusée par le service distant.
        """
        # 1) On crée un produit et une commande dans la DB de test
        product = Product.create(
            id=50,
            name="Keyboard",
            type="Computer",
            description="A mechanical keyboard",
            image="kb.jpg",
            height=2,
            weight=500,
            price=100.0,
            in_stock=True
        )
        order = Order.create(
            id=999,
            total_price=100.0,      # ex: 1 x 100
            total_price_tax=None,
            email=None,
            credit_card=None,
            shipping_information=None,
            paid=False,
            transaction=None,
            shipping_price=5.0
        )
        ProductOrder.create(
            id=101,
            order=order,
            product=product,
            quantity=1
        )

        # 2) On simule un service de paiement qui renvoie une erreur
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": {
                "credit_card": {
                    "code": "card-declined",
                    "name": "La carte de crédit a été déclinée"
                }
            }
        }
        mock_post.return_value = mock_response

        # 3) On remplit d'abord l'email et l'adresse
        update_data = {
            "order": {
                "email": "test@example.com",
                "shipping_information": {
                    "province": "QC",
                    "city": "Chicoutimi",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "country": "Canada"
                }
            }
        }
        resp = test_app.put('/order/999', json=update_data)
        assert resp.status_code == 200

        # 4) On tente de payer la commande avec une carte "déclinée"
        pay_data = {
            "credit_card": {
                "name": "John Doe",
                "number": "4000 0000 0000 0002",  # carte refusée
                "expiration_year": 2024,
                "expiration_month": 9,
                "cvv": "123"
            },
            "amount_charged": 120.0  # ex: 100 *1.15 + 5 shipping
        }
        resp2 = test_app.put('/order/999', json=pay_data)
        # On s'attend à un code 422 ou 4xx selon ton code
        assert resp2.status_code == 422

        data2 = resp2.get_json()
        # L'erreur est "card-declined" ou "payment_error" selon ta logique
        assert data2["errors"]["order"]["code"] in ["card-declined", "payment_error"]
