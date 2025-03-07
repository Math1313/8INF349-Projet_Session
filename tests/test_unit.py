# tests/test_unit.py

import pytest
from inf349 import app, get_taxes_rate, get_shipping_price, return_error

def test_get_taxes_rate():
    assert get_taxes_rate("QC") == 1.15
    assert get_taxes_rate("ON") == 1.13
    assert get_taxes_rate("AB") == 1.05
    assert get_taxes_rate("BC") == 1.12
    assert get_taxes_rate("NS") == 1.14
    # Province inconnue => 0.0
    assert get_taxes_rate("??") == 0.0

def test_get_shipping_price():
    # Moins de 500g
    assert get_shipping_price(100, 1) == 5.0
    # 500g à 2kg
    assert get_shipping_price(499, 2) == 10.0  # 998g
    # 2kg et plus
    assert get_shipping_price(1000, 2) == 25.0  # 2000g

def test_return_error():
    """
    On place l'appel à return_error() dans un contexte d'application Flask,
    pour éviter l'erreur 'Working outside of application context'.
    """
    with app.app_context():
        error_code = "missing-fields"
        error_name = "Un champ requis est manquant"
        http_code = 422

        response, status_code = return_error(error_code, error_name, http_code)
        assert status_code == 422

        # On récupère les données JSON renvoyées par jsonify()
        json_data = response.json
        assert "errors" in json_data
        assert "order" in json_data["errors"]
        assert json_data["errors"]["order"]["code"] == error_code
        assert json_data["errors"]["order"]["name"] == error_name
