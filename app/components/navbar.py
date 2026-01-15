from nicegui import ui

def create_navbar():
    """Crée la barre de navigation en bas de page"""
    
    ui.add_head_html('''
        <style>
            :root {
                --primary: #4E7ED2;
                --secondary: #9BB1E5;
                --tertiary: #BCCBF0;
            }
            
            .navbar-container {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: var(--primary);
                box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
                z-index: 1000;
            }
            .navbar-content {
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 10px 0;
                max-width: 600px;
                margin: 0 auto;
            }
            .nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                padding: 8px 16px;
                border-radius: 12px;
                transition: background 0.2s;
            }
            .nav-item:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            .nav-item.active {
                background: rgba(255, 255, 255, 0.3);
            }
            .nav-icon {
                font-size: 24px;
                margin-bottom: 4px;
                color: white;
            }
            .nav-label {
                font-size: 12px;
                font-weight: 500;
                color: white;
            }
            .nav-item.active .nav-icon,
            .nav-item.active .nav-label {
                color: white;
            }
        </style>
    ''')
    
    with ui.element('div').classes('navbar-container'):
        with ui.element('div').classes('navbar-content'):
            # Bouton Accueil
            with ui.element('div').classes('nav-item').on('click', lambda: ui.navigate.to('/accueil')):
                ui.icon('home').classes('nav-icon')
                ui.label('Accueil').classes('nav-label')
            
            # Bouton Calendrier
            with ui.element('div').classes('nav-item').on('click', lambda: ui.navigate.to('/calendrier')):
                ui.icon('calendar_month').classes('nav-icon')
                ui.label('Calendrier').classes('nav-label')
            
            # Bouton Statistiques
            with ui.element('div').classes('nav-item').on('click', lambda: ui.navigate.to('/statistiques')):
                ui.icon('bar_chart').classes('nav-icon')
                ui.label('Statistiques').classes('nav-label')
            
            # Bouton Profil
            with ui.element('div').classes('nav-item').on('click', lambda: ui.navigate.to('/profil')):
                ui.icon('person').classes('nav-icon')
                ui.label('Moi').classes('nav-label')