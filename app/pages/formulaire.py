from nicegui import ui, app
from components.navbar import create_navbar

def create():
    """Crée la page de formulaire pour ajouter un devoir ou examen"""
    
    ui.add_head_html('''
        <style>
            .formulaire-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
            }
            .formulaire-card {
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 600px;
                margin: 0 auto;
            }
            .form-title {
                text-align: center;
                font-size: 28px;
                font-weight: 700;
                color: #333;
                margin-bottom: 30px;
            }
            .add-icon-container {
                width: 80px;
                height: 80px;
                background: #667eea;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
            }
        </style>
    ''')
    
    with ui.column().classes('formulaire-container'):
        with ui.card().classes('formulaire-card'):
            # Icône d'ajout
            with ui.element('div').classes('add-icon-container'):
                ui.icon('add', size='48px', color='white')
            
            ui.html('<div class="form-title">Nouvel événement</div>', sanitize=False)
            
            # Sélecteur de type (devoir ou examen)
            type_event = ui.toggle(
                ['Devoir', 'Examen'],
                value='Devoir'
            ).classes('w-full q-mb-lg')
            
            # Conteneur pour les champs du formulaire
            form_container = ui.column().classes('w-full')
            
            def update_form():
                """Met à jour le formulaire selon le type sélectionné"""
                form_container.clear()
                
                with form_container:
                    # Champs communs
                    titre = ui.input('Titre').props('outlined').classes('w-full q-mb-md')
                    
                    branche = ui.select(
                        ['Mathématiques', 'Français', 'Allemand', 'Anglais', 'Histoire', 
                         'Géographie', 'Sciences', 'Physique', 'Chimie', 'Biologie',
                         'Arts visuels', 'Éducation physique', 'Musique'],
                        label='Branche'
                    ).props('outlined').classes('w-full q-mb-md')
                    
                    description = ui.textarea(
                        'Description',
                        placeholder='Ex: Exercices 1-5, p.42'
                    ).props('outlined').classes('w-full q-mb-md')
                    
                    if type_event.value == 'Devoir':
                        # Champs spécifiques au devoir
                        date_rendu = ui.input(
                            'Date de rendu',
                            value='Mercredi 15.01'
                        ).props('outlined').classes('w-full q-mb-md')
                        
                        temps_estime = ui.input(
                            'Estimation du temps',
                            placeholder='Ex: 1h30'
                        ).props('outlined').classes('w-full q-mb-md')
                        
                    else:
                        # Champs spécifiques à l'examen
                        date_examen = ui.input(
                            'Date de l\'examen',
                            value='Vendredi 17.01'
                        ).props('outlined').classes('w-full q-mb-md')
                        
                        temps_revision = ui.input(
                            'Temps de révision estimé',
                            placeholder='Ex: 3h'
                        ).props('outlined').classes('w-full q-mb-md')
                    
                    # Bouton d'enregistrement
                    async def handle_submit():
                        # TODO: Sauvegarder dans la base de données
                        event_type = type_event.value.lower()
                        ui.notify(f'{type_event.value} ajouté avec succès!', type='positive')
                        ui.navigate.to('/calendrier')
                    
                    ui.button(
                        'ENREGISTRER',
                        icon='check',
                        on_click=handle_submit
                    ).props('color=primary').classes('w-full q-mt-md').style('padding: 12px;')
                    
                    # Bouton annuler
                    ui.button(
                        'ANNULER',
                        icon='close',
                        on_click=lambda: ui.navigate.to('/calendrier')
                    ).props('flat color=negative').classes('w-full q-mt-sm')
            
            # Mise à jour lors du changement de type
            type_event.on_value_change(update_form)
            update_form()
        
        # Navbar en bas
        create_navbar()