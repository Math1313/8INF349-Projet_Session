# Dockerfile

# Choisir une image Python
FROM python:3.13

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier tout le contenu de ton projet dans /app
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 5000 pour Flask
EXPOSE 5000

# Définir la commande par défaut (lancement de Flask)
CMD ["flask", "run", "--host=0.0.0.0"]
