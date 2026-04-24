# 1. Image de base
FROM python:3.11-slim

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Copier uniquement les dépendances d'abord (optimisation cache)
COPY requirements.txt .

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le reste du code
COPY . .

# 6. Exposer le port
EXPOSE 5000

# 7. Lancer l'application avec Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]