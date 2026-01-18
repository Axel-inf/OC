#aide de l'IA

from nicegui import ui, app
from components.navbar import create_navbar
from datetime import datetime, timedelta

def create():
    """Crée la page calendrier"""
    
    ui.add_head_html('<link rel="stylesheet" href="/static/css/custom.css">')
    
    with ui.column().classes('page-container'):
        # Titre principal
        ui.html('<div class="titre-container">Calendrier</div>', sanitize=False)
        
        # Barre "Charge de travail"
        ui.html('<div class="charge-travail-container">Charge de travail</div>', sanitize=False)
        
        # Conteneur des jours
        with ui.column().classes('days-list-container'):
            # ========== JOUR 1: MARDI 13.01 (avec devoirs) ==========
            with ui.column().classes('day-container'):
                ui.html('<div class="day-header-container">Mardi 13.01</div>', sanitize=False)
                
                with ui.column().classes('day-content-container'):
                    # Temps total estimé
                    ui.html('<div class="total-time-container">Temps total estimé : 3h30</div>', sanitize=False)
                    
                    # Conteneur des devoirs
                    with ui.column().classes('homework-list-container'):
                        # Devoir 1: Mathématiques
                        ui.html('''
                            <div class="homework-card-container">
                                <div class="subject">Mathématiques</div>
                                <div class="description">Exercice 1.20</div>
                                <div class="time-info">Temps estimé : 30 minutes</div>
                                <div class="time-info">Temps passé : 1 heure</div>
                            </div>
                        ''', sanitize=False)
                        
                        # Séparateur
                        ui.html('<div class="separator"></div>', sanitize=False)
                        
                        # Devoir 2: Français
                        ui.html('''
                            <div class="homework-card-container">
                                <div class="subject">Français</div>
                                <div class="description">Lecture de Théodat</div>
                                <div class="time-info">Temps estimé : 7 heures</div>
                                <div class="time-info">Temps passé : 10 heures</div>
                            </div>
                        ''', sanitize=False)
                    
                    # Séparateur entre devoirs et examens
                    ui.html('<div class="separator"></div>', sanitize=False)
                    
                    # Conteneur des examens
                    with ui.column().classes('exams-list-container'):
                        ui.html('''
                            <div class="exam-card-container">
                                <div class="subject">Physique</div>
                                <div class="description">Magnétisme</div>
                                <div class="time-info">Temps de révision estimé : 2 heures</div>
                                <div class="time-info">Temps passé : 8 heures</div>
                            </div>
                        ''', sanitize=False)
            
            # ========== JOUR 2: MERCREDI 14.01 (sans devoir) ==========
            with ui.column().classes('day-container'):
                ui.html('<div class="day-header-container">Mercredi 14.01</div>', sanitize=False)
                
                with ui.column().classes('day-content-container empty tertiary'):
                    ui.html('Aucun devoir ou examen ce jour-ci', sanitize=False)
            
            # ========== JOUR 3: JEUDI 15.01 (avec devoirs) ==========
            with ui.column().classes('day-container'):
                ui.html('<div class="day-header-container">Jeudi 15.01</div>', sanitize=False)
                
                with ui.column().classes('day-content-container'):
                    # Temps total estimé
                    ui.html('<div class="total-time-container">Temps total estimé : 2h</div>', sanitize=False)
                    
                    # Conteneur des devoirs
                    with ui.column().classes('homework-list-container'):
                        # Devoir 1: Chimie
                        ui.html('''
                            <div class="homework-card-container">
                                <div class="subject">Chimie</div>
                                <div class="description">Exercice chapitre 5</div>
                                <div class="time-info">Temps estimé : 1 heure</div>
                                <div class="time-info">Temps passé : 1h30</div>
                            </div>
                        ''', sanitize=False)
                    
                    # Séparateur entre devoirs et examens
                    ui.html('<div class="separator"></div>', sanitize=False)
                    
                    # Conteneur des examens
                    with ui.column().classes('exams-list-container'):
                        ui.html('''
                            <div class="exam-card-container">
                                <div class="subject">Anglais</div>
                                <div class="description">Grammaire et vocabulaire</div>
                                <div class="time-info">Temps de révision estimé : 1 heure</div>
                                <div class="time-info">Temps passé : 30 minutes</div>
                            </div>
                        ''', sanitize=False)
        
        # Bouton Ajouter un événement
        ui.button(
            '+ Ajouter un événement',
            on_click=lambda: ui.navigate.to('/formulaire')
        ).classes('add-button-container')
        
        # Navbar en bas
        create_navbar()