# 8INF349-Projet_Session
Projet de session du cours de Technologies Web Avancées - 8INF349
## Environment Setup
### 1. Install Python 3.14
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

## Launch Flask App
Linux:
```bash
FLASK_DEBUG=True FLASK_APP=inf349 flask run
```
