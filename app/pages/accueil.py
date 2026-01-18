#aide de l'IA

from datetime import datetime
from nicegui import ui, app
from components.navbar import create_navbar

def create():
    """Crée la page d'accueil"""
    
    ui.add_head_html('''
    <style>
        /* Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            margin: 0;
            padding: 0;
            /* permettre le scroll global */
            overflow: auto;
            height: 100%;
            width: 100%;
        }

        /* Variables */
        :root {
            --primary: #4E7ED2;
            --secondary: #9BB1E5;
            --tertiary: #BCCBF0;
        }

        /* Container principal */
        .accueil-container {
            height: 100vh;
            background-image: url('/static/images/fond_accueil.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            position: relative;
            margin: 0;
            padding: 0;
            width: 100%;
            display: flex;
            flex-direction: column;
            /* laisser le contenu défiler dans la page */
            overflow: visible;
        }

        /* Contenu central */
        .accueil-content {
            flex: 1;
            max-width: 500px;
            margin: 0 auto;
            text-align: center;
            display: flex;
            flex-direction: column;
            /* packer les éléments en haut pour éviter un grand vide */
            justify-content: flex-start;
            align-items: center;
            position: relative;
            z-index: 2;
            width: 100%;
            /* permettre le scroll interne si nécessaire */
            overflow-y: auto;
            /* espace réservé au bas = hauteur du footer bleu + 32px */
            padding: 0 20px calc(43.7vh + 32px) 20px;
            gap: 2vh;
        }

        /* Titre */
        .welcome-title {
            color: white;
            font-size: 32px;
            font-weight: 700;
            /* responsive : min 48px, preferred 8vh, max 64px */
            margin-top: clamp(48px, 8vh, 64px);
            text-align: center;
            width: 100%;
            display: block;
            flex-shrink: 0;
        }

        /* Icône utilisateur */
        .welcome-icon {
            width: 80px;
            height: 80px;
            background: var(--primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            /* responsive spacing sous le titre */
            margin: clamp(12px, 3vh, 25px) auto 0;
            flex-shrink: 0;
        }

        /* Bouton principal */
        .action-button {
            width: 100%;
            height: 44px;
            padding: 12.5px 16px;
            margin-top: clamp(8px, 2.5vh, 16px);
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
            background-color: var(--primary) !important;
            color: white !important;
            text-align: center;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .action-button:hover {
            transform: translateY(-2px);
        }

        /* Footer bleu */
        .blue-footer {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 43.7vh;
            background: rgba(78, 126, 210, 0.66);
            border-top-left-radius: 32px;
            border-top-right-radius: 32px;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 6vh 34px 3vh 34px;
            overflow: visible;
            gap: 3.1vh;
        }

        /* Cartes blanches */
        .white-card {
            width: 100%;
            max-width: 460px;
            padding: 12px 16px !important;
            border-radius: 16px;
            background-color: white !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 3;
        }

        .white-card div {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
            text-align: center;
            width: 100%;
        }
        .content-top {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
        }


        /* Navbar */
        .navbar-container {
            position: relative;
            z-index: 3;
            margin-top: auto;
            padding-bottom: 8px;
            flex-shrink: 0;
        }
    </style>
    ''')


    
    with ui.column().classes('accueil-container'):
        with ui.column().classes('accueil-content'):
            # Groupe haut (Bienvenue, icône, bouton)
            with ui.column().classes('content-top'):
                # Titre de bienvenue
                user_name = app.storage.user.get('email', 'Utilisateur').split('@')[0]
                ui.html(f'<div class="welcome-title">Bienvenue</div>', sanitize=False)
                
                # Icône utilisateur
                with ui.element('div').classes('welcome-icon'):
                    ui.icon('person', size='60px')
                
                # Bouton "Modifier votre profil"
                ui.button(
                    'MODIFIER VOTRE PROFIL',
                    on_click=lambda: ui.navigate.to('/profil')
                ).props('color=primary').classes('action-button')
        
        # Rectangle bleu en bas (container pour les rectangles blancs)
        with ui.element('div').classes('blue-footer'):
            # Rectangle blanc "Ajouter un événement"
            with ui.card().classes('white-card'):
                ui.html('''
                    <div style="text-align: center; font-size: 16px; font-weight: 600; margin-bottom: 6px; width: 100%;">
                        Ajouter un événement à votre calendrier
                    </div>
                ''', sanitize=False)
                ui.icon('calendar_month', size='32px').style('display: block; margin-left: auto; margin-right: auto;')
            
            # Rectangle blanc "Statistiques"
            with ui.card().classes('white-card'):
                ui.html('''
                    <div style="text-align: center; font-size: 16px; font-weight: 600; margin-bottom: 6px; width: 100%;">
                        Jeter un coup d'œil aux statistiques
                    </div>
                ''', sanitize=False)
                ui.icon('bar_chart', size='32px').style('display: block; margin-left: auto; margin-right: auto;')
        
        # Barre de navigation
        with ui.column().classes('navbar-container'):
            create_navbar()



