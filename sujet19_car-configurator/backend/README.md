# Backend - Car Configurator (CSP avec OR-Tools)

Ce backend implémente un petit configurateur de voiture basé sur la **programmation par contraintes** avec **OR-Tools CP-SAT**.

## Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Lancement de l'API

```bash
uvicorn main:app --reload
```

L'API sera disponible sur `http://127.0.0.1:8000`.

Endpoints principaux :

- `POST /propagate` : renvoie, pour des choix partiels, les domaines encore possibles.
- `POST /solve` : tente de compléter la configuration.
- `GET /ping` : test simple.

Ce backend est conçu pour être utilisé avec le front contenu dans le dossier `frontend/`.
