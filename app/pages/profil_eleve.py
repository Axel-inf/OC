#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
from database.database import get_db
from database.models import Utilisateur, Eleve

def create():
    """Crée la page de profil pour un élève"""
    user_id = app.storage.user.get('user_id')

    nom_value = app.storage.user.get('nom', '')
    prenom_value = app.storage.user.get('prenom', '')
    email_value = app.storage.user.get('email', '')
    classe_value = '1GY1'
    niveau_maths_value = 'Mathématiques standards'
    langue1_value = 'Français'
    langue2_value = 'Anglais'
    langue3_value = 'Espagnol'
    os_value = 'Physique et application des mathématiques'
    oc_value = 'Physique'
    basic_english_value = False
    bilingue_value = False

    if user_id is not None:
        db = get_db()
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if user is not None:
                nom_value = user.nom or nom_value
                prenom_value = user.prenom or prenom_value
                email_value = user.email or email_value

            eleve = db.query(Eleve).filter(Eleve.utilisateur_id == user_id).first()
            if eleve is not None:
                classe_value = eleve.classe or classe_value
                niveau_maths_value = eleve.niveau_maths or niveau_maths_value
                langue1_value = eleve.langue1 or langue1_value
                langue2_value = eleve.langue2 or langue2_value
                langue3_value = eleve.langue3 or langue3_value
                os_value = eleve.os or os_value
                oc_value = eleve.oc or oc_value
                basic_english_value = bool(eleve.basic_english)
                bilingue_value = bool(eleve.bilingue)
        finally:
            db.close()
    
    ui.add_head_html('''
        <style>
            .profil-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
            }
            .profil-card {
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 600px;
                margin: 0 auto;
            }
            .profil-header {
                text-align: center;
                margin-bottom: 30px;
            }
            .profil-title {
                font-size: 28px;
                font-weight: 700;
                color: #333;
                margin-top: 15px;
            }
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #667eea;
                margin: 25px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #667eea;
            }
            .info-row {
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            .info-label {
                font-weight: 600;
                color: #666;
            }
            .info-value {
                color: #333;
            }
        </style>
    ''')
    
    with ui.column().classes('profil-container'):
        with ui.card().classes('profil-card'):
            # En-tête du profil
            with ui.element('div').classes('profil-header'):
                # Avatar
                with ui.element('div').style('width: 80px; height: 80px; background: #667eea; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;'):
                    ui.icon('person', size='48px', color='white')
                
                ui.html('<div class="profil-title">Profil</div>', sanitize=False)
            
            # Section Compte
            ui.html('<div class="section-title">Compte</div>', sanitize=False)
            
            nom_input = ui.input('Nom', value=nom_value).props('outlined').classes('w-full q-mb-md')
            prenom_input = ui.input('Prénom', value=prenom_value).props('outlined').classes('w-full q-mb-md')
            email_input = ui.input('Email', value=email_value).props('outlined').classes('w-full q-mb-md')
            password_input = ui.input('Mot de passe', password=True, password_toggle_button=True).props('outlined').classes('w-full q-mb-md')
            
            # Section École
            ui.html('<div class="section-title">École</div>', sanitize=False)
            
            classe_select = ui.select(
                [
                    *[f'1GY{i}' for i in range(1, 13)],
                    *[f'4GY{i}' for i in range(1, 13)],
                    *[f'3GY{i}' for i in range(1, 13)],
                    *[f'2GY{i}' for i in range(1, 13)],
                ],
                label='Classe',
                value=classe_value
            ).props('outlined').classes('w-full q-mb-md')
            
            maths_select = ui.select(
                ['Mathématiques renforcées', 'Mathématiques standards'],
                label='Niveau de mathématiques',
                value=niveau_maths_value
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.row().classes('w-full gap-2'):
                langue1 = ui.select(
                    ['Français'],
                    label='Langue 1',
                    value=langue1_value
                ).props('outlined').classes('flex-1')

                langue2 = ui.select(
                    ['Allemand', 'Anglais', 'Espagnol', 'Grec', 'Italien', 'Latin (débutants)', 'Latin (avancés)'],
                    label='Langue 2',
                    value=langue2_value
                ).props('outlined').classes('flex-1')
            
            ui.space().classes('h-4')
            
            langue3 = ui.select(
                ['Allemand', 'Anglais', 'Espagnol', 'Grec', 'Italien', 'Latin (débutants)', 'Latin (avancés)'],
                label='Langue 3',
                value=langue3_value
            ).props('outlined').classes('w-full q-mb-md')
            
            # Section Options
            ui.html('<div class="section-title">Options</div>', sanitize=False)
            
            os_input = ui.select(
                ['Arts visuels', 'Anglais', 'Biologie et chimie', 'Économie et droit', 'Espagnol', 'Grec', 'Italien',
                 'Latin (débutants)', 'Latin (avancés)', 'Musique', 'Physique et application des mathématiques'],
                label='Option spécifique (OS)',
                value=os_value
            ).props('outlined').classes('w-full q-mb-md')

            oc_input = ui.select(
                ['Applications des mathématiques', 'Arts visuels', 'Biologie', 'Chimie', 'Économie et droit', 'Géographie',
                 'Histoire', 'Informatique', 'Musique', 'Philosophie', 'Physique', 'Psychologie et pédagogie',
                 'Sciences politiques', 'Sciences religieuses', 'Sport'],
                label='Option complémentaire (OC)',
                value=oc_value
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.column().classes('w-full gap-2'):
                basic_english = ui.checkbox('Basic English', value=basic_english_value)
                bilingue = ui.checkbox('Bilingue', value=bilingue_value)
            
            # Boutons d'action
            with ui.row().classes('w-full gap-4 q-mt-lg'):
                async def handle_save():
                    # TODO: Sauvegarder les modifications
                    ui.notify('Profil mis à jour avec succès!', type='positive')
                
                async def handle_logout():
                    app.storage.user.clear()
                    ui.notify('Déconnexion réussie', type='info')
                    ui.navigate.to('/login')
                
                ui.button(
                    'ENREGISTRER',
                    icon='save',
                    on_click=handle_save
                ).props('color=primary').classes('flex-1')
                
                ui.button(
                    'SE DÉCONNECTER',
                    icon='logout',
                    on_click=handle_logout
                ).props('color=negative flat').classes('flex-1')
        
        # Navbar
        create_navbar()