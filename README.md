# Plateforme de Trading Automatique CFD

Cette application est une plateforme complète pour le trading automatisé de CFD, construite avec Django et React, et entièrement conteneurisée avec Docker.

## Architecture

- **Backend**: Django + Django REST Framework
- **Frontend**: React.js
- **Base de données**: PostgreSQL
- **Tâches asynchrones**: Celery
- **Message Broker**: Redis
- **Déploiement**: Docker Compose

## Prérequis

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation et Lancement

### 1. Configuration de l'environnement

Le backend nécessite un fichier `.env` pour configurer les variables d'environnement. Créez un fichier `backend/.env` à partir de l'exemple ci-dessous.

```
# backend/.env

# Clé secrète de Django (générez une nouvelle clé pour la production)
SECRET_KEY=django-insecure-your-secret-key

# Mode debug (True en développement, False en production)
DEBUG=True

# URL de la base de données PostgreSQL
DATABASE_URL=postgres://user:password@postgres:5432/trading_db

# URLs pour Celery et Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Clé de chiffrement pour les clés API OANDA (doit être de 32 bytes encodée en base64)
# Vous pouvez en générer une avec le script python suivant :
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=votre_cle_de_chiffrement_base64
```

**Important**: Les credentials de la base de données (`user`, `password`, `trading_db`) dans `DATABASE_URL` doivent correspondre à ceux définis dans `docker-compose.yml`.

### 2. Lancement des services

Une fois le fichier `.env` configuré, lancez l'ensemble des services avec Docker Compose depuis la racine du projet :

```bash
docker-compose up --build
```

Cette commande va construire les images pour le backend et le frontend, puis démarrer les 4 conteneurs (backend, frontend, postgres, redis).

Les services seront accessibles aux adresses suivantes :
- **Frontend (React)**: `http://localhost:3000`
- **Backend (Django API)**: `http://localhost:8000`

## Utilisation de l'application

1.  **Créer un compte utilisateur** : Le backend ne fournit pas d'interface d'inscription par défaut. Vous devez créer un superutilisateur pour vous connecter.

    ```bash
    # Exécutez cette commande dans un autre terminal
    docker-compose exec backend python manage.py createsuperuser
    ```

    Suivez les instructions pour créer votre compte.

2.  **Se connecter** : Allez sur `http://localhost:3000` et utilisez les identifiants du superutilisateur que vous venez de créer.

3.  **Configurer la clé API OANDA** :
    - Accédez à la page "API Key".
    - Entrez votre ID de compte OANDA et votre clé d'accès API.
    - La clé sera chiffrée et stockée de manière sécurisée.

4.  **Créer et gérer un bot** :
    - Allez sur la page "Bots".
    - Créez un nouveau bot en lui donnant un nom et en choisissant un actif.
    - Une fois créé, vous pouvez le démarrer, l'arrêter ou le supprimer.

5.  **Consulter le tableau de bord** :
    - La page "Dashboard" affiche un résumé en temps réel de votre compte de trading OANDA (solde, P/L, etc.).

6.  **Lancer un backtest** :
    - Accédez à la page "Backtesting".
    - Remplissez le formulaire pour définir les paramètres de votre test : actif (ex: `EUR_USD`), période (dates de début et de fin), et stratégie.
    - Les paramètres de la stratégie doivent être au format JSON (ex: `{"rsi_period": 14, "sma_period": 50}`).
    - Lancez le backtest. La tâche s'exécutera en arrière-plan.
    - Les résultats s'afficheront dans l'historique des backtests sur la même page, indiquant le statut (en cours, complété, échoué) et les métriques de performance.

## Fonctionnalités Clés

- **Authentification Sécurisée**: JWT (JSON Web Tokens) pour l'authentification des utilisateurs.
- **Gestion Sécurisée des Clés API**: Les clés API OANDA sont chiffrées avant d'être stockées en base de données.
- **Bots de Trading**: Créez, démarrez, et arrêtez des bots de trading qui opèrent selon des stratégies prédéfinies.
- **Backtesting de Stratégies**: Testez vos stratégies sur des données historiques pour évaluer leur performance avant de les déployer en réel.
- **Tâches Asynchrones**: Utilisation de Celery et Redis pour gérer les bots et les backtests sans bloquer l'interface utilisateur.
- **Interface Réactive**: Interface utilisateur construite avec React pour une expérience fluide et dynamique.
