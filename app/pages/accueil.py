#aide de Claude pour le style et la structure de la page accueil
from datetime import datetime
from nicegui import ui, app
from components.navbar import create_navbar

def create():
    """Crée la page d'accueil"""
    
    ui.add_head_html('''
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            
            :root {
                --primary: #4E7ED2;
                --secondary: #9BB1E5;
                --tertiary: #BCCBF0;
            }
            
            .accueil-container {
                min-height: 100vh;
                background-image: url('/static/images/fond_accueil.png');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                position: relative;
                margin: 0;
                padding: 0;
                width: 100%;
            }
            
            .accueil-container::after {
                content: '';
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                height: 200px;
                background: rgba(78, 126, 210, 0.66);
                pointer-events: none;
                z-index: 1;
            }
            
            .accueil-content {
                padding: 40px 20px;
                max-width: 500px;
                margin: 0 auto;
                text-align: center;
                display: flex;
                justify-content: center;
                position: relative;
                z-index: 2;
            }
            .welcome-card {
                background: transparent;
                padding: 40px;
                border-radius: 20px;
                box-shadow: None;
                text-align: center;
            }
            .welcome-icon {
                width: 100px;
                height: 100px;
                background: var(--primary);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 30px;
            }
            .welcome-title {
                color: white;
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 20px;
                text-align: center;
                width: 100%;
                display: block;
            }
            .welcome-subtitle {
                color: white;
                font-size: 18px;
                line-height: 1.6;
                margin-bottom: 40px;
                text-align: center;
            }
            .action-button, {
                width: 100%;
                padding: 16px;
                margin: 10px 0;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s;
                background-color: var(--primary) !important;
                color: white !important;
            }
                     
            .titre{
                width: 100%;
                padding: 16px;
                margin: 10px 0;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s;
                color: white !important;
            }
                     
            .action-button:hover {
                transform: translateY(-2px);
            }
    ''')
    
    with ui.column().classes('accueil-container'):
        # Navbar en haut
        create_navbar()
        
        with ui.column().classes('accueil-content'):
            with ui.card().classes('welcome-card'):
                # Icône utilisateur
                with ui.element('div').classes('welcome-icon'):
                    ui.icon('person', size='60px')
                
                # Titre de bienvenue
                user_name = app.storage.user.get('email', 'Utilisateur').split('@')[0]
                ui.html(f'<div class="welcome-title">Bienvenue</div>', sanitize=False).classes('titre')
                
                # Sous-titre explicatif
                ui.html('''
                    <div class="welcome-subtitle">
                        Ajoutez un événement à votre calendrier
                    </div>
                ''', sanitize=False)
                
                # Message motivant
                ui.html('''
                    <div style="color: #667eea; font-size: 16px; font-style: italic; margin-bottom: 30px;">
                        "Jetez un coup d'œil au calendrier"
                    </div>
                ''', sanitize=False)
                
                # Boutons d'action
                ui.button(
                    'ACCUEIL',
                    icon='home',
                    on_click=lambda: ui.navigate.to('/accueil')
                ).props('color=primary').classes('action-button')
                
                ui.button(
                    'CALENDRIER',
                    icon='calendar_month',
                    on_click=lambda: ui.navigate.to('/calendrier')
                ).props('color=primary').classes('action-button')
                
                ui.button(
                    'STATISTIQUES',
                    icon='bar_chart',
                    on_click=lambda: ui.navigate.to('/statistiques')
                ).props('color=primary').classes('action-button')
                
                ui.button(
                    'MOI',
                    icon='person',
                    on_click=lambda: ui.navigate.to('/profil')
                ).props('color=primary').classes('action-button')