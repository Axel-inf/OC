import os
from nicegui import ui, app
from database.database import init_database
from pages import login, inscription, accueil, calendrier, formulaire, profil_eleve, profil_professeur, statistiques
from config.settings import APP_NAME, SECRET_KEY

# Initialisation de la base de données
init_database()

# Configuration de l'application
app.add_static_files('/static', 'static')

# Variable de session pour l'utilisateur connecté
@ui.page('/')
def index():
    """Page d'accueil - redirige vers login ou accueil selon l'état de connexion"""
    if app.storage.user.get('authenticated', False):
        ui.navigate.to('/accueil')
    else:
        ui.navigate.to('/login')

# Routes des pages
@ui.page('/login')
def page_login():
    login.create()

@ui.page('/inscription')
def page_inscription():
    inscription.create()

@ui.page('/accueil')
def page_accueil():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    accueil.create()

@ui.page('/calendrier')
def page_calendrier():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    calendrier.create()

@ui.page('/formulaire')
def page_formulaire():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    formulaire.create()

@ui.page('/profil')
def page_profil():
    if not app.storage.user.get('authenticated', False):
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
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    statistiques.create()

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