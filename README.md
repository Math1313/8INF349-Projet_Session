# 8INF349-Projet_Session
Projet de session du cours de Technologies Web Avancées - 8INF349
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
set FLASK_DEBUG=True && set FLASK_APP=inf349 && flask init-db
```
### Launch Flask App
Linux:
```bash
FLASK_DEBUG=True FLASK_APP=inf349 flask run
```
Windows:
```powershell
set FLASK_DEBUG=True && set FLASK_APP=inf349 && flask run
```
## 📂 API Documentation

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
    ...
]
```

#### 📝 Orders

##### Create order
```http
POST /order
```

**Request Body**
```json
{
    "product":
    {
        "id": 1
        "quantity": 1 
    }
}
```

**Response** `302 Found`
```
/order/:id
```

### Status Codes
Modify this section to adapt to our project

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |
