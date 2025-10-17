# Dockerfile pour ProctoFlex AI Backend - Version Complète
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système pour OpenCV, MediaPipe et PostgreSQL
RUN apt-get update && apt-get install -y \
    # Compilation
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    # PostgreSQL
    libpq-dev \
    # OpenCV et traitement d'image
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # libatlas-base-dev removed (not available on base image)
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # Audio processing
    libsndfile1 \
    libasound2-dev \
    # Python development
    python3-dev \
    python3-pip \
    # Utilitaires
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python avec versions compatibles
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs uploads data/gdpr models

# Configuration des permissions
RUN chmod -R 755 /app

# Exposition du port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
