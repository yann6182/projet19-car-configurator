# Système de Débat Assisté par IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un système de débat assisté par IA pour aider à structurer, analyser et améliorer les échanges argumentatifs en temps réel. Cette application permet à des utilisateurs de débattre avec l'assistance d'agents IA qui analysent leurs arguments, identifient les faiblesses, suggèrent des contre-arguments, et aident à construire des débats plus constructifs.

## ✨ Fonctionnalités Principales

- **Analyse d'arguments en temps réel :** Les LLMs évaluent la pertinence, la cohérence et la force des arguments soumis par les utilisateurs.
- **Identification des failles logiques :** Le système détecte les sophismes et les faiblesses dans le raisonnement.
- **Suggestion de contre-arguments :** Des contre-arguments et des pistes de réfutation sont proposés pour enrichir le débat.
- **Évaluation formelle :** Intégration des frameworks d'argumentation (comme Tweety) pour une évaluation logique et structurée.
- **Interface interactive :** Une interface web moderne et réactive pour une communication fluide et en temps réel via WebSockets.

## 🛠️ Architecture et Technologies

Ce projet est architecturé autour de trois composants principaux qui communiquent entre eux.

### 1. Frontend

- **Framework :** [Angular](https://angular.io/)
- **Communication :** [WebSockets](https://developer.mozilla.org/fr/docs/Web/API/WebSockets_API) pour la communication bidirectionnelle en temps réel avec le backend.
- **Rôle :** Fournit l'interface utilisateur interactive où se déroulent les débats.

### 2. Backend

- **Langage :** Python
- **Framework :** [FastAPI](https://fastapi.tiangolo.com/) pour des API performantes et la gestion des WebSockets.
- **Rôle :** Fait le lien entre le frontend et les services d'IA. Il gère la logique du débat, les sessions utilisateurs et la persistance des données.

### 3. Logique d'IA et d'Argumentation

- **Analyse et Génération :** Modèles de Langage Larges (LLMs) pour l'analyse sémantique et la génération de suggestions.
- **Évaluation Formelle :** [TweetyProject](http.tweetyproject.org/) et ses bibliothèques associées pour modéliser et évaluer la structure logique des arguments.

### 4. Base de Données

- **Système :** [PostgreSQL](https://www.postgresql.org/)
- **Rôle :** Stocke l'historique des débats, les arguments et les informations des utilisateurs.

## 🚀 Démarrage Rapide

Ce projet est entièrement conteneurisé avec Docker, ce qui simplifie grandement son installation et son lancement.

### Prérequis

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

2. **Configuration de l'environnement :**
   Créez un fichier `.env` à la racine du projet en vous basant sur le fichier `.env.sample`. Il devrait contenir les variables nécessaires pour la base de données :

   ```env
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=debatai
   ```

3. **Lancez l'application :**
   Utilisez Docker Compose pour construire les images et démarrer tous les services.

   ```bash
   docker-compose up -d --build
   ```

4. **Accédez à l'application :**

   - L'interface frontend est disponible à l'adresse [http://localhost:4200](http://localhost:4200).
   - L'API backend est accessible à l'adresse [http://localhost:8000](http://localhost:8000).

## 📁 Structure du Projet

```
.
├── .env.sample
├── .gitignore
├── docker-compose.yml
├── README.md
├── backend/                  # Service Backend (Python/FastAPI)
│   ├── Dockerfile
│   └── ai_model/
├── db/                       # Scripts d'initialisation de la base de données PostgreSQL
└── frontend/                 # Application Frontend (Angular)
```

## 📚 Références

Ce projet s'inspire des recherches et plateformes suivantes :

- **COMMA** : _Computational Models of Argument_ - Pour les bases théoriques de l'argumentation.
- **Plateforme Kialo** : Pour l'étude de cas d'une plateforme de débat structuré.
- **Recherches de Chris Reed** : Sur les technologies de l'argumentation.
- **_AI-Assisted Argumentation and Debate_ (2023)** : Pour les applications pratiques de l'IA dans les débats.

## 📄 Licence

Ce projet est sous licence MIT.
