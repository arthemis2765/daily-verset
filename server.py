import os

from apscheduler.schedulers.background import BackgroundScheduler#explication: ce fichier est le fichier qui permet de planifier des tâches
from fastapi import FastAPI, Request#explication: ce fichier est le fichier qui permet de créer une API
from fastapi.responses import FileResponse, JSONResponse#explication: ce fichier est le fichier qui permet de renvoyer des réponses HTTP
from fastapi.staticfiles import StaticFiles#explication: ce fichier est le fichier qui permet de servir des fichiers statiques

#explication: ce fichier est le fichier qui permet d'envoyer les notifications push
import push
from verset_du_jour import (
    DB_FILE,
    get_daily_verse,
    init_db,
    list_subscriptions,
    remove_subscriptions,
    save_subscription,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Heure quotidienne d'envoi de la notification (24h, heure du serveur).
# Modifiable via la variable d'environnement PUSH_TIME, ex: "07:30".
PUSH_HOUR, PUSH_MINUTE = (int(p) for p in os.environ.get("PUSH_TIME", "08:00").split(":"))
#explication: ce fichier est le fichier qui permet de créer une API
app = FastAPI(title="Verset du jour")
#explication: ce fichier est le fichier qui permet de planifier des tâches
scheduler = BackgroundScheduler()

#explication: ce fichier est le fichier qui permet d'envoyer la notification quotidienne
def send_daily_notification() -> None:
    verse = get_daily_verse(DB_FILE)
    subscriptions = list_subscriptions(DB_FILE)
    if not subscriptions:
        return
    dead_endpoints = push.send_push_to_all(
        subscriptions,
        payload={
            "title": "Verset du jour",
            "body": f"{verse['text']}  — {verse['reference']}",
        },
    )
    remove_subscriptions(dead_endpoints, DB_FILE)


@app.on_event("startup")#explication: ce fichier est le fichier qui permet de démarrer le serveur
def on_startup() -> None:
    init_db(DB_FILE)
    scheduler.add_job(
        send_daily_notification,
        trigger="cron",
        hour=PUSH_HOUR,
        minute=PUSH_MINUTE,
        id="daily_push",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")#explication: ce fichier est le fichier qui permet d'arrêter le serveur
def on_shutdown() -> None:
    scheduler.shutdown(wait=False)


@app.get("/api/verset")#explication: ce fichier est le fichier qui permet de récupérer le verset du jour
def api_verset() -> dict[str, str]:
    return get_daily_verse(DB_FILE)
def api_verset() -> dict[str, str]:
    return get_daily_verse(DB_FILE)


@app.get("/api/vapid-public-key")#explication: ce fichier est le fichier qui permet de récupérer la clé publique VAPID
def api_vapid_public_key() -> dict[str, str]:
    return {"publicKey": push.get_vapid_public_key()}


#explication: ce fichier est le fichier qui permet d'abonner un utilisateur
@app.post("/api/subscribe")#explication: ce fichier est le fichier qui permet d'abonner un utilisateur
async def api_subscribe(request: Request) -> JSONResponse:
    subscription = await request.json()
    save_subscription(subscription, DB_FILE)
    return JSONResponse({"status": "ok"})

#explication: ce fichier est le fichier qui permet de désabonner un utilisateur
@app.post("/api/unsubscribe")#explication: ce fichier est le fichier qui permet de désabonner un utilisateur
async def api_unsubscribe(request: Request) -> JSONResponse:
    body = await request.json()
    endpoint = body.get("endpoint")
    if endpoint:
        remove_subscriptions([endpoint], DB_FILE)
    return JSONResponse({"status": "ok"})

#explication: ce fichier est le fichier qui permet de servir la page d'accueil
@app.get("/")#explication: ce fichier est le fichier qui permet de servir la page d'accueil
def index() -> FileResponse:
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))#explication: ce fichier est le fichier qui permet de servir la page d'accueil


app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")#explication: ce fichier est le fichier qui permet de servir les fichiers statiques