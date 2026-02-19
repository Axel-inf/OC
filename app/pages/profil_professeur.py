#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
from database.database import get_db
from database.models import Utilisateur, Enseignant

def create():
    """Crée la page de profil pour un enseignant"""
    user_id = app.storage.user.get('user_id')

    nom_value = app.storage.user.get('nom', '')
    prenom_value = app.storage.user.get('prenom', '')
    email_value = app.storage.user.get('email', '')
    classes_values: list[str] = []
    branches_values: list[str] = []
    os_value = ''
    oc_value = ''
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

            enseignant = db.query(Enseignant).filter(Enseignant.utilisateur_id == user_id).first()
            if enseignant is not None:
                classes_values = [item.strip() for item in (enseignant.classes or '').split(',') if item.strip()]
                branches_values = [item.strip() for item in (enseignant.branches or '').split(',') if item.strip()]
                os_value = enseignant.os or ''
                oc_value = enseignant.oc or ''
                basic_english_value = bool(enseignant.basic_english)
                bilingue_value = bool(enseignant.bilingue)
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
            email_input = ui.input('Email', value=email_value).props('outlined readonly').classes('w-full q-mb-md')
            
            # Section École
            ui.html('<div class="section-title">École</div>', sanitize=False)
            
            # Classes enseignées
            classes_container = ui.column().classes('w-full q-mb-md')
            with classes_container:
                ui.label('Mes classes').classes('text-subtitle2 text-grey-7 q-mb-sm')
                with ui.row().classes('w-full gap-2'):
                    if classes_values:
                        for classe in classes_values:
                            ui.chip(classe, removable=False).props('color=primary')
                    else:
                        ui.chip('Aucune classe', removable=False).props('color=grey-6 text-color=white')
            
            # Branches enseignées
            branches_select = ui.select(
                ['Mathématiques', 'Français', 'Allemand', 'Anglais', 'Histoire', 
                 'Géographie', 'Sciences', 'Physique', 'Chimie', 'Biologie'],
                label='Branches enseignées',
                value=branches_values,
                multiple=True
            ).props('outlined').classes('w-full q-mb-md')
            
            # Section Options enseignées
            ui.html('<div class="section-title">Options</div>', sanitize=False)
            
            os_input = ui.input(
                'Option spécifique (OS)',
                value=os_value
            ).props('outlined').classes('w-full q-mb-md')
            
            oc_input = ui.input(
                'Option complémentaire (OC)',
                value=oc_value
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.column().classes('w-full gap-2'):
                basic_english = ui.checkbox('Basic English', value=basic_english_value)
                bilingue = ui.checkbox('Cours bilingues', value=bilingue_value)
            
            # Section Cours complémentaires enseignés
            ui.html('<div class="section-title">Cours complémentaires</div>', sanitize=False)
            
            with ui.column().classes('w-full'):
                ui.checkbox('OCOM').classes('q-mb-sm')
                ui.checkbox('IVEO').classes('q-mb-sm')
                ui.checkbox('4-OS Ec 2', value=True).classes('q-mb-sm')
                ui.checkbox('4-OC Ec 2').classes('q-mb-sm')
                ui.checkbox('4-OC Ec 3').classes('q-mb-sm')
                ui.checkbox('4-OS Ec 3', value=True).classes('q-mb-sm')
            
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