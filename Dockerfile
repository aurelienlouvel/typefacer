FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Ajoutons des flags pour voir le processus d'installation
RUN pip install --no-cache-dir -v lightning

# Pour vérifier l'installation
RUN python -c "import lightning; print(f'Lightning version: {lightning.__version__}')"

COPY . .

ENV PYTHONPATH=/app
