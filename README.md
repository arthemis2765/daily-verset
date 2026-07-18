# Verset du jour — appli web

Petite appli web qui affiche un verset biblique différent chaque jour,
avec la même base SQLite (`verset_du_jour.py`) que la version CLI.

## Notifications navigateur (push)

Un bouton « Activer les notifications » sur la page permet à chaque visiteur
de s'abonner. Chaque jour à 08:00 (heure du serveur), le site envoie
automatiquement le verset du jour à tous les abonnés, même si le site est
fermé.

- Heure d'envoi modifiable via la variable d'environnement `PUSH_TIME`
  (ex: `PUSH_TIME=07:30`).
- Une paire de clés VAPID est générée automatiquement au premier lancement
  dans `vapid_private.pem` — **ne pas supprimer ce fichier après que des
  gens se sont abonnés**, sinon leurs abonnements deviennent invalides.
- Les notifications ne fonctionnent que sur un site servi en HTTPS (ou en
  local sur `127.0.0.1`/`localhost`, tolérés comme "contexte sécurisé").
  Vérifie donc que ton hébergeur (Render, Railway...) sert bien le site en
  HTTPS — c'est le cas par défaut sur ces deux plateformes.

## Lancer en local

```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

Puis ouvrir http://127.0.0.1:8000

Au premier lancement, `verset_du_jour.db` est créé automatiquement et
rempli avec les versets. La page appelle `/api/verset`, qui renvoie
toujours le même verset pour la journée en cours (nouveau verset chaque
jour, via l'anti-répétition déjà en place).

## Déployer (Render / Railway / Fly.io)

Ces plateformes fonctionnent toutes de la même façon pour ce projet :

1. Pousser ce dossier sur un dépôt Git.
2. Créer un service web, langage Python.
3. Build command : `pip install -r requirements.txt`
4. Start command : `uvicorn server:app --host 0.0.0.0 --port $PORT`

⚠️ Point d'attention : `verset_du_jour.db` **et** `vapid_private.pem` sont
des fichiers stockés sur disque. Sur la plupart des hébergeurs gratuits, le
disque est éphémère (remis à zéro à chaque redéploiement). Si tu veux que
l'historique persiste dans la durée :
- Render/Railway : ajouter un "disque persistant" (souvent payant) monté
  sur le dossier du projet, ou
- passer à une base hébergée (PostgreSQL géré, gratuit sur ces deux
  plateformes) — migration à prévoir si ce besoin se confirme.

Pour un usage personnel avec redéploiements rares, le SQLite local
suffit largement pour commencer.
