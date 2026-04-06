#aide de l'IA
import os
import asyncio
from datetime import datetime
from nicegui import ui, app
from fastapi import Body, HTTPException
from database.database import get_db
from database.models import Utilisateur, CalendarEvent
from database.database import init_database
from database.calendar_repository import (
    delete_calendar_event,
    move_unfinished_events_to_next_day,
    normalize_time_spent_strict,
    update_calendar_event_done,
    update_calendar_event_time_spent,
)
from pages import login, inscription, accueil, calendrier, formulaire, profil_eleve, profil_professeur, statistiques, reset_password
from pages import charge_eleve
from database.seed_demo_data import seed_demo_school_data
from config.settings import (
    APP_NAME,
    CALENDAR_AUTO_ROLLOVER_HOUR,
    CALENDAR_AUTO_ROLLOVER_MINUTE,
    SEED_DEMO_DATA_ON_STARTUP,
    SECRET_KEY,
)

# Initialisation de la base de données
init_database()
if SEED_DEMO_DATA_ON_STARTUP:
    seed_demo_school_data()

# Configuration de l'application
# Utiliser le chemin absolu pour servir les fichiers statiques
static_path = os.path.join(os.path.dirname(__file__), 'static')
app.add_static_files('/static', static_path)


def _process_calendar_rollover_if_due() -> None:
    now = datetime.now()
    current_marker = now.date().isoformat()
    threshold = (CALENDAR_AUTO_ROLLOVER_HOUR, CALENDAR_AUTO_ROLLOVER_MINUTE)

    if (now.hour, now.minute) < threshold:
        return

    last_processed_marker = app.storage.general.get('calendar_rollover_last_processed_date')
    if last_processed_marker == current_marker:
        return

    moved_count = move_unfinished_events_to_next_day(now.date())
    app.storage.general['calendar_rollover_last_processed_date'] = current_marker

    if moved_count > 0:
        print(f'[calendrier] {moved_count} événement(s) non réalisé(s) reporté(s) au jour suivant.')


async def _calendar_rollover_loop() -> None:
    while True:
        _process_calendar_rollover_if_due()
        await asyncio.sleep(30.0)


@app.on_event('startup')
async def _start_calendar_rollover_loop() -> None:
    app.storage.general['server_boot_id'] = datetime.now().isoformat()
    app.state.calendar_rollover_task = asyncio.create_task(_calendar_rollover_loop())


@app.on_event('shutdown')
async def _stop_calendar_rollover_loop() -> None:
    task = getattr(app.state, 'calendar_rollover_task', None)
    if task:
        task.cancel()


@app.post('/api/calendar-events/delete')
async def api_delete_calendar_event(payload: dict = Body(...)):
    # Aide IA: sécurisation de la suppression via identité de session (pas de user_identifier client)
    event_id = int(payload.get('event_id', 0))
    if event_id <= 0:
        raise HTTPException(status_code=400, detail='Paramètres invalides')

    if not _is_session_authenticated():
        raise HTTPException(status_code=401, detail='Session non authentifiée')

    user_identifier = str(app.storage.user.get('email') or '').strip()
    user_role = str(app.storage.user.get('role') or '').strip().lower()
    if not user_identifier:
        raise HTTPException(status_code=401, detail='Session invalide')

    db = get_db()
    try:
        owned_event = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.id == event_id,
                CalendarEvent.user_identifier == user_identifier,
                CalendarEvent.is_hidden.is_(False),
            )
            .first()
        )
    finally:
        db.close()

    if owned_event is None:
        raise HTTPException(status_code=404, detail='Événement introuvable')

    if user_role == 'eleve' and owned_event.source_event_id is not None:
        raise HTTPException(status_code=403, detail='Suppression non autorisée pour cet événement partagé')

    deleted = delete_calendar_event(event_id, user_identifier)
    if not deleted:
        raise HTTPException(status_code=404, detail='Événement introuvable')

    return {'success': True}


@app.post('/api/calendar-events/time-spent')
async def api_update_calendar_time_spent(payload: dict = Body(...)):
    # Aide IA: sécurisation de la mise à jour du temps passé via identité de session
    event_id = int(payload.get('event_id', 0))
    time_spent_raw = str(payload.get('time_spent', '')).strip()
    if event_id <= 0:
        raise HTTPException(status_code=400, detail='Paramètres invalides')

    if not _is_session_authenticated():
        raise HTTPException(status_code=401, detail='Session non authentifiée')

    user_identifier = str(app.storage.user.get('email') or '').strip()
    if not user_identifier:
        raise HTTPException(status_code=401, detail='Session invalide')

    time_spent = normalize_time_spent_strict(time_spent_raw)
    if time_spent is None:
        raise HTTPException(status_code=400, detail='Format invalide: utilisez min, h, ou h+min (ex: 30 min, 1 h, 1 h 30 min)')

    updated = update_calendar_event_time_spent(event_id, user_identifier, time_spent)
    if not updated:
        raise HTTPException(status_code=404, detail='Événement introuvable')

    return {'success': True}


@app.post('/api/calendar-events/done')
async def api_update_calendar_done(payload: dict = Body(...)):
    # Met à jour l'état fait/non fait d'un événement du calendrier pour l'utilisateur connecté.
    event_id = int(payload.get('event_id', 0))
    is_done = bool(payload.get('is_done', False))
    if event_id <= 0:
        raise HTTPException(status_code=400, detail='Paramètres invalides')

    if not _is_session_authenticated():
        raise HTTPException(status_code=401, detail='Session non authentifiée')

    user_identifier = str(app.storage.user.get('email') or '').strip()
    if not user_identifier:
        raise HTTPException(status_code=401, detail='Session invalide')

    updated = update_calendar_event_done(event_id, user_identifier, is_done)
    if not updated:
        raise HTTPException(status_code=404, detail='Événement introuvable')

    return {'success': True}

# Variable de session pour l'utilisateur connecté
def _is_session_authenticated() -> bool:
    if not app.storage.user.get('authenticated', False):
        return False

    user_id = app.storage.user.get('user_id')
    email = app.storage.user.get('email')
    if user_id is None or not email:
        app.storage.user.clear()
        return False

    current_boot_id = app.storage.general.get('server_boot_id')
    user_boot_id = app.storage.user.get('auth_boot_id')
    if current_boot_id and user_boot_id != current_boot_id:
        app.storage.user.clear()
        return False

    db = get_db()
    try:
        user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
        if user is None or user.email != email:
            app.storage.user.clear()
            return False
    finally:
        db.close()

    return True


@ui.page('/')
def index():
    """Page d'accueil - redirige vers login"""
    ui.navigate.to('/login')

# Routes des pages
@ui.page('/login')
def page_login():
    login.create()

@ui.page('/inscription')
def page_inscription():
    inscription.create()

@ui.page('/reinitialisation-mot-de-passe')
def page_reset_password():
    reset_password.create()

@ui.page('/accueil')
def page_accueil():
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    accueil.create()

@ui.page('/calendrier')
def page_calendrier():
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    calendrier.create()

@ui.page('/formulaire')
def page_formulaire():
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    formulaire.create()


@ui.page('/formulaire/modifier/{event_id}')
def page_formulaire_modifier(event_id: str):
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    try:
        parsed_event_id = int(event_id)
    except (TypeError, ValueError):
        ui.navigate.to('/calendrier')
        return
    formulaire.create(edit_event_id=parsed_event_id)

@ui.page('/profil')
def page_profil():
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    
    # Affiche le profil selon le rôle
    role = app.storage.user.get('role')
    if role == 'eleve':
        profil_eleve.create()
    elif role == 'enseignant':
        profil_professeur.create()

@ui.page('/statistiques')
def page_statistiques():
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    if app.storage.user.get('role') == 'enseignant':
        charge_eleve.create()
    else:
        statistiques.create()


@ui.page('/charge-eleve')
def page_charge_eleve():
    if not _is_session_authenticated():
        ui.navigate.to('/login')
        return
    if app.storage.user.get('role') != 'enseignant':
        ui.navigate.to('/accueil')
        return
    ui.navigate.to('/statistiques')

# Lancement de l'application
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title=APP_NAME,
        favicon='🎓',
        dark=False,
        reload=True,
        show=True,
        port=8080,
        storage_secret=SECRET_KEY,
    )