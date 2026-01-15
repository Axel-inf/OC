from nicegui import ui, app
from components.navbar import create_navbar

def create():
    """Crée la page de profil pour un enseignant"""
    
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
            
            nom_input = ui.input('Nom', value='Martin').props('outlined').classes('w-full q-mb-md')
            prenom_input = ui.input('Prénom', value='Sophie').props('outlined').classes('w-full q-mb-md')
            email_input = ui.input('Email', value='sophie.martin@college.edu').props('outlined readonly').classes('w-full q-mb-md')
            
            # Section École
            ui.html('<div class="section-title">École</div>', sanitize=False)
            
            # Classes enseignées
            classes_container = ui.column().classes('w-full q-mb-md')
            with classes_container:
                ui.label('Mes classes').classes('text-subtitle2 text-grey-7 q-mb-sm')
                with ui.row().classes('w-full gap-2'):
                    ui.chip('9VG1', removable=False).props('color=primary')
                    ui.chip('10VG1', removable=False).props('color=primary')
                    ui.chip('11VG2', removable=False).props('color=primary')
            
            # Branches enseignées
            branches_select = ui.select(
                ['Mathématiques', 'Français', 'Allemand', 'Anglais', 'Histoire', 
                 'Géographie', 'Sciences', 'Physique', 'Chimie', 'Biologie'],
                label='Branches enseignées',
                value='Mathématiques',
                multiple=True
            ).props('outlined').classes('w-full q-mb-md')
            
            # Section Options enseignées
            ui.html('<div class="section-title">Options</div>', sanitize=False)
            
            os_input = ui.input(
                'Option spécifique (OS)',
                value='Physique-Applications'
            ).props('outlined').classes('w-full q-mb-md')
            
            oc_input = ui.input(
                'Option complémentaire (OC)',
                value='Arts visuels'
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.column().classes('w-full gap-2'):
                basic_english = ui.checkbox('Basic English', value=False)
                bilingue = ui.checkbox('Cours bilingues', value=True)
            
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