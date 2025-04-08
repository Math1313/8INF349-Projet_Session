# 8INF349-Projet_Session
Projet de session du cours de Technologies Web Avancées - 8INF349
'''
# realiser par 
 - Mathis Audusseau
 - Mathis Gauthier 
 - Zhakael Bondu

## 🐍 Environment Setup
### 1. Install Python 3.13
### 2. Create virtual environment
```bash
python -m venv .venv
```
### 3. Activate virtual environment
Linux:
```bash
source .venv/bin/activate
```
Windows:
```powershell
.venv\Scripts\activate.ps1
```
### 4. Install requirements
```bash
pip install -r requirements.txt
```

## 🚀 Execute API
### Create Database
Linux:
```bash
FLASK_DEBUG=True FLASK_APP=inf349 flask init-db
```
Windows:
```powershell
$env:FLASK_DEBUG = "True"; $env:FLASK_APP = "inf349"; flask init-db
```
### Launch Flask App
Linux:
```bash
FLASK_DEBUG=True FLASK_APP=inf349 flask run
```
Windows:
```powershell
$env:FLASK_DEBUG = "True"; $env:FLASK_APP = "inf349"; flask run
```
### Lunch Flask tests

```powershell & linux
python -m pytest -v
```
### 📂 API Documentation

### Base URL
```
http://127.0.0.1:5000/
```

### Endpoints

#### 🧰 Product

##### Get all products
```http
GET /
```

**Response** `200 OK`
Content-Type: application/json
```json
[
    {
        "description": "Raw organic brown eggs in a basket",
        "height": 600,
        "id": 1,
        "image": "0.jpg",
        "in_stock": true,
        "name": "Brown eggs",
        "price": 28.1,
        "weight": 400
    },
    "..."
]
```

#### 📝 Orders

##### Create order
```http
POST /order
```

**Request Body**
Content-Type: application/json
```json
{
    "product":
    {
        "id": 1,
        "quantity": 1 
    }
}
```

**Response** `302 Found`
```
Location: /order/:id
```
##### Put order (shipping_information)
```http
PUT /order/<int:order_id>
```

**Request Body**
Content-Type: application/json
```json
{ 
  "order" : { 
    "email" : "user@uqac.ca", 
    "shipping_information" : { 
        "country" : "Canada", 
        "address" : "201, rue Président-Kennedy", 
        "postal_code" : "G7X 3Y7", 
        "city" : "Chicoutimi", 
        "province" : "QC" 
    } 
  } 
}
```

**Response** `200 OK`
Content-Type: application/json
```json
{ 
  "order" : { 
    "shipping_information" : { 
        "country" : "Canada", 
        "address" : "201, rue Président-Kennedy", 
        "postal_code" : "G7X 3Y7", 
        "city" : "Chicoutimi", 
        "province" : "QC" 
    }, 
    "credit_card" : {}, 
    "email" : "user@uqac.ca", 
    "total_price" : 9148, 
    "total_price_tax" : 10520.20, 
    "transaction": {}, 
    "paid": false, 
    "product" : { 
        "id" : 123, 
        "quantity" : 1 
    }, 
    "shipping_price" : 1000, 
    "id" : 6543 
  } 
} 
```
##### Put order (credit_card & amount_charged)
```http
PUT /order/<int:order_id>
```

**Request Body**
Content-Type: application/json
```json
{ 
  "credit_card" : { 
    "name" : "John Doe", 
    "number" : "4242 4242 4242 4242", 
    "expiration_year" : 2026, 
    "cvv" : "123", 
    "expiration_month" : 9 
  },
  "amount_charged": 32.31
}
```

**Response** `200 OK`
Content-Type: application/json
```json
{
  "order": {
    "credit_card": {
      "expiration_month": 9,
      "expiration_year": 2026,
      "first_digits": "4242",
      "last_digits": 4242,
      "name": "John Doe"
    },
    "email": "jgnault@uqac.ca",
    "id": 4,
    "paid": true,
    "product": {
      "id": 2,
      "quantity": 1
    },
    "shipping_information": {
      "address": "201, rue Président-Kennedy",
      "city": "Chicoutimi",
      "country": "Canada",
      "postal_code": "G7X 3Y7",
      "province": "QC"
    },
    "shipping_price": 5.0,
    "total_price": 29.45,
    "total_price_tax": 33.87,
    "transaction": {
      "amount_charged": 38.87,
      "id": "RNBqiliect72GsZn8CJ1",
      "success": "true"
    }
  }
}
```

##### Get order
```http
GET /order/<int:order_id>
```

**Response** `200 OK`
Content-Type: application/json
```json
{
  "order": {
    "credit_card": {},
    "email": "null",
    "id": 1,
    "paid": null,
    "product": {
      "id": 1,
      "quantity": 1
    },
    "shipping_information": {},
    "shipping_price": null,
    "total_price": null,
    "total_price_tax": null,
    "transaction": {}
  }
}
```

### Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 302 | Found - Resource found successfully |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Entity cannot be processed |
| 500 | Internal Server Error - Server error |

## 📋 Todo List

### 🛠️ Configuration Initiale
- [x] Mettre en place l'environnement Python 3.6+
- [x] Installer les dépendances requises
  - [x] Flask 1.11+
  - [x] pytest
  - [x] pytest-flask
  - [x] peewee
- [x] Créer la structure du projet Flask
- [x] Configurer SQLite3 avec Peewee
- [x] Implémenter la commande `flask init-db`

### 🔄 Service de Récupération des Produits
- [x] Implémenter la récupération des produits depuis l'API distante
  - [x] Connexion à `http://dimensweb.uqac.ca/~jgnault/shops/products/`
  - [x] Persistance locale des produits dans SQLite
  - [x] Vérifier que la récupération se fait uniquement au lancement

### 📦 Gestion des Produits (GET /)
- [x] Implémenter l'endpoint GET / pour lister les produits
- [x] Assurer le format JSON correct de la réponse
- [x] Inclure tous les champs requis (name, id, in_stock, description, price, weight, image)

### 🛒 Gestion des Commandes
#### Création de Commande (POST /order)
- [x] Implémenter la création de commande
- [x] Valider les champs obligatoires (product_id, quantity)
- [x] Gérer les erreurs
  - [x] Champs manquants
  - [x] Produit hors stock
  - [x] Quantité invalide
- [x] Retourner la redirection 302 avec l'ID de commande

#### Consultation de Commande (GET /order/<id>)
- [X] Implémenter la consultation de commande
- [x] Calculer les prix
  - [x] Prix total (total_price)
  - [x] Prix avec taxes selon la province
  - [x] Frais d'expédition selon le poids
- [x] Retourner toutes les informations de la commande

#### Mise à jour des Informations Client (PUT /order/<id>)
- [x] Implémenter la mise à jour des informations client
- [x] Valider les champs obligatoires
  - [x] Email
  - [x] Informations d'expédition complètes
- [x] Gérer les erreurs de validation
- [x] Empêcher la modification des champs protégés

#### Paiement de Commande
- [x] Implémenter l'intégration avec le service de paiement distant
- [x] Valider la carte de crédit
  - [x] Format du numéro
  - [x] Date d'expiration
- [x] Gérer les réponses du service de paiement
- [x] Mettre à jour le statut de la commande
- [x] Empêcher le double paiement

### 🧪 Tests
- [ ] Tests unitaires
  - [ ] Modèles de données
  - [ ] Logique métier
- [ ] Tests fonctionnels
  - [ ] Endpoints API
  - [ ] Scénarios de commande
- [ ] Tests d'intégration
  - [ ] Service de produits
  - [ ] Service de paiement

### 📝 Documentation
- [ ] README.md
  - [ ] Instructions d'installation
  - [ ] Documentation API
  - [ ] Exemples d'utilisation
- [ ] Commentaires dans le code
- [ ] Documentation des modèles de données

### 🔍 Vérification Finale
- [ ] Vérifier toutes les exigences techniques
- [ ] Tester tous les scénarios d'erreur
- [ ] Valider le format des réponses JSON
- [ ] Nettoyer et optimiser le code
- [ ] Vérifier la couverture des tests

---
*Dates importantes :*
- 📅 Première remise : 6 mars 2025 (20%)
- 📅 Remise finale : 17 avril 2025 (30%)
