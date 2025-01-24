from peewee import (
    SqliteDatabase,
)
import requests
import CustomClass
from pathlib import Path

# Vérifier si la base de données existe
if Path('products.db').is_file():
    print("La base de données existe déjà.")
    exit()
# Créer la base de données
db = SqliteDatabase('products.db')

db.connect()
db.create_tables([CustomClass.Product])

# Récupérer les données JSON depuis l'URL
url = "https://dimensweb.uqac.ca/~jgnault/shops/products/"
response = requests.get(url)

if response.status_code == 200:
    json_data = response.json()  # Charger les données JSON
    for item in json_data['products']:
        # Ajouter chaque élément dans la base de données
        CustomClass.Product.create(
            id=item['id'],
            name=item['name'],
            type=item['type'],
            description=item['description'],
            image=item['image'],
            height=item['height'],
            weight=item['weight'],
            price=item['price'],
            in_stock=item['in_stock']
        )
else:
    print(f"Erreur lors de la récupération des données : {
          response.status_code}")

# Afficher les données insérées
# for row in Product.select():
#    print(row.id, row.name, row.value)
