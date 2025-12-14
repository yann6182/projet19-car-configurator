# Frontend - Car Configurator

Ce dossier contient un front minimaliste en **HTML/CSS/JS** pur, qui consomme l'API FastAPI
du dossier `backend/`.

## Utilisation

1. Lancer le backend (voir `backend/README.md`), en général sur `http://127.0.0.1:8000`.
2. Ouvrir simplement `index.html` dans un navigateur (double-clic ou via un petit serveur statique).

À chaque changement d'option :

- Le front envoie la configuration partielle à `POST /propagate`.
- Le backend renvoie les valeurs encore possibles pour chaque variable.
- Les options incompatibles sont désactivées dans les menus déroulants.

Le bouton « Trouver une configuration complète » appelle `POST /solve` pour obtenir
une configuration cohérente complète à partir des choix partiels.
