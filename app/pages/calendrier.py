from nicegui import ui, app
from components.navbar import create_navbar
from datetime import datetime, timedelta

def create():
    """Crée la page calendrier"""
    
    ui.add_head_html('''
        <style>
            .calendrier-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding-bottom: 80px;
            }
            .calendar-header {
                background: white;
                padding: 20px;
                margin: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .calendar-title {
                font-size: 24px;
                font-weight: 700;
                color: #333;
                margin-bottom: 5px;
            }
            .calendar-subtitle {
                color: #666;
                font-size: 14px;
            }
            .workload-indicator {
                background: white;
                padding: 15px;
                margin: 0 20px 20px 20px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .workload-title {
                font-size: 16px;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
            }
            .workload-bar {
                height: 30px;
                background: #e0e0e0;
                border-radius: 15px;
                overflow: hidden;
                position: relative;
            }
            .workload-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50 0%, #FFC107 50%, #F44336 100%);
                transition: width 0.3s ease;
            }
            .workload-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-weight: 600;
                color: #333;
            }
            .event-card {
                background: #667eea;
                color: white;
                padding: 15px;
                margin: 10px 20px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .event-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .event-details {
                font-size: 14px;
                opacity: 0.9;
            }
            .add-button {
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: #667eea;
                color: white;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
                z-index: 100;
            }
        </style>
    ''')
    
    with ui.column().classes('calendrier-container'):
        # Header avec date et heure
        with ui.element('div').classes('calendar-header'):
            current_date = datetime.now()
            ui.html(f'<div class="calendar-title">Mercredi 15.01</div>', sanitize=False)
            ui.html(f'<div class="calendar-subtitle">Aujourd\'hui à {current_date.strftime("%H:%M")}</div>', sanitize=False)
        
        # Indicateur de charge de travail
        with ui.element('div').classes('workload-indicator'):
            ui.html('<div class="workload-title">Temps total estimé : 5h</div>', sanitize=False)
            with ui.element('div').classes('workload-bar'):
                # Barre de progression (5h sur 10h max = 50%)
                ui.html('<div class="workload-fill" style="width: 50%;"></div>', sanitize=False)
                ui.html('<div class="workload-text">5h / 10h</div>', sanitize=False)
        
        # Liste des devoirs/examens
        with ui.column().classes('w-full'):
            # Exemple: Mathématiques
            with ui.element('div').classes('event-card').style('background: #FF6B6B;'):
                ui.html('<div class="event-title">Mathématiques</div>', sanitize=False)
                ui.html('''
                    <div class="event-details">
                        Devoir 6 du cahier d'exercices<br>
                        Pour le: Mercredi 15.01<br>
                        Temps estimé : 1h30
                    </div>
                ''', sanitize=False)
            
            # Exemple: Français
            with ui.element('div').classes('event-card').style('background: #4ECDC4;'):
                ui.html('<div class="event-title">Français</div>', sanitize=False)
                ui.html('''
                    <div class="event-details">
                        Lecture 4-7<br>
                        Pour le: Mercredi 15.01<br>
                        Temps estimé : 2h
                    </div>
                ''', sanitize=False)
            
            # Exemple: Physique
            with ui.element('div').classes('event-card').style('background: #95E1D3;'):
                ui.html('<div class="event-title">Physique</div>', sanitize=False)
                ui.html('''
                    <div class="event-details">
                        Exercices chimie chap. 3<br>
                        Pour le: Mercredi 15.01<br>
                        Temps estimé : 1h30
                    </div>
                ''', sanitize=False)
        
        # Bouton flottant pour ajouter un événement
        ui.button(
            icon='add',
            on_click=lambda: ui.navigate.to('/formulaire')
        ).classes('add-button').props('fab')
        
        # Navbar en bas
        create_navbar()