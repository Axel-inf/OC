from nicegui import ui, app
from components.navbar import create_navbar

def create():
    """Crée la page d'accueil"""
    
    ui.add_head_html('''
        <style>
            .accueil-container {
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .accueil-content {
                padding: 40px 20px;
                max-width: 500px;
                margin: 0 auto;
            }
            .welcome-card {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            .welcome-icon {
                width: 100px;
                height: 100px;
                background: #667eea;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 30px;
            }
            .welcome-title {
                color: #333;
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 20px;
            }
            .welcome-subtitle {
                color: #666;
                font-size: 18px;
                line-height: 1.6;
                margin-bottom: 40px;
            }
            .action-button {
                width: 100%;
                padding: 16px;
                margin: 10px 0;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s;
            }
            .action-button:hover {
                transform: translateY(-2px);
            }
        </style>
    ''')
    
    with ui.column().classes('accueil-container'):
        # Navbar en haut
        create_navbar()
        
        with ui.column().classes('accueil-content'):
            with ui.card().classes('welcome-card'):
                # Icône utilisateur
                with ui.element('div').classes('welcome-icon'):
                    ui.icon('person', size='60px', color='white')
                
                # Titre de bienvenue
                user_name = app.storage.user.get('email', 'Utilisateur').split('@')[0]
                ui.html(f'<div class="welcome-title">Bienvenue</div>', sanitize=False)
                
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