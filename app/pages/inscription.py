from nicegui import ui, app

def create():
    """Crée la page d'inscription"""
    
    ui.add_head_html('''
        <style>
            .inscription-container {
                min-height: 100vh;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .inscription-card {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                margin: 0 auto;
            }
            .inscription-title {
                text-align: center;
                color: #333;
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 30px;
            }
            .section-title {
                color: #667eea;
                font-size: 18px;
                font-weight: 600;
                margin: 20px 0 15px 0;
            }
        </style>
    ''')
    
    with ui.column().classes('inscription-container'):
        with ui.card().classes('inscription-card'):
            ui.html('<div class="inscription-title">Inscription</div>', sanitize=False)
            
            # Choix du rôle
            ui.html('<div class="section-title">Choisissez votre rôle</div>', sanitize=False)
            role_select = ui.select(
                ['Élève', 'Enseignant'],
                label='Rôle',
                value='Élève'
            ).props('outlined').classes('w-full q-mb-md')
            
            # Informations de base
            ui.html('<div class="section-title">Informations personnelles</div>', sanitize=False)
            
            with ui.row().classes('w-full gap-4'):
                nom_input = ui.input('Nom').props('outlined').classes('flex-1')
                prenom_input = ui.input('Prénom').props('outlined').classes('flex-1')
            
            email_input = ui.input(
                'Email',
                placeholder='votre.email@college.edu'
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.row().classes('w-full gap-4'):
                password_input = ui.input(
                    'Mot de passe',
                    password=True,
                    password_toggle_button=True
                ).props('outlined').classes('flex-1')
                
                confirm_password = ui.input(
                    'Confirmer mot de passe',
                    password=True,
                    password_toggle_button=True
                ).props('outlined').classes('flex-1')
            
            # Conteneur pour les champs spécifiques au rôle
            role_specific_container = ui.column().classes('w-full')
            
            def update_role_fields():
                """Met à jour les champs selon le rôle sélectionné"""
                role_specific_container.clear()
                
                with role_specific_container:
                    if role_select.value == 'Élève':
                        create_student_fields()
                    else:
                        create_teacher_fields()
            
            def create_student_fields():
                """Crée les champs spécifiques aux élèves"""
                ui.html('<div class="section-title">Informations scolaires</div>', sanitize=False)
                
                classe = ui.input('Classe').props('outlined').classes('w-full q-mb-md')
                
                niveau_maths = ui.select(
                    ['Mathématiques renforcées', 'Mathématiques standards'],
                    label='Niveau de mathématiques'
                ).props('outlined').classes('w-full q-mb-md')
                
                with ui.row().classes('w-full gap-4'):
                    langue1 = ui.select(
                        ['Allemand', 'Anglais', 'Italien'],
                        label='Langue 1'
                    ).props('outlined').classes('flex-1')
                    
                    langue2 = ui.select(
                        ['Allemand', 'Anglais', 'Italien'],
                        label='Langue 2'
                    ).props('outlined').classes('flex-1')
                
                langue3 = ui.select(
                    ['Aucune', 'Allemand', 'Anglais', 'Italien', 'Espagnol'],
                    label='Langue 3',
                    value='Aucune'
                ).props('outlined').classes('w-full q-mb-md')
                
                ui.html('<div class="section-title">Options</div>', sanitize=False)
                
                os = ui.input('Option spécifique (OS)').props('outlined').classes('w-full q-mb-md')
                oc = ui.input('Option complémentaire (OC)').props('outlined').classes('w-full q-mb-md')
                
                with ui.row().classes('w-full gap-4'):
                    basic_english = ui.checkbox('Basic English')
                    bilingue = ui.checkbox('Bilingue')
            
            def create_teacher_fields():
                """Crée les champs spécifiques aux enseignants"""
                ui.html('<div class="section-title">Informations professionnelles</div>', sanitize=False)
                
                branches = ui.input(
                    'Branche(s) enseignée(s)',
                    placeholder='Ex: Mathématiques, Physique'
                ).props('outlined').classes('w-full q-mb-md')
                
                classes = ui.input(
                    'Classe(s)',
                    placeholder='Ex: 9VG1, 10VG2, 11VG3'
                ).props('outlined').classes('w-full q-mb-md')
                
                ui.html('<div class="section-title">Options enseignées</div>')
                
                os = ui.input('Option spécifique (OS)').props('outlined').classes('w-full q-mb-md')
                oc = ui.input('Option complémentaire (OC)').props('outlined').classes('w-full q-mb-md')
                
                with ui.row().classes('w-full gap-4'):
                    basic_english = ui.checkbox('Basic English')
                    bilingue = ui.checkbox('Cours bilingues')
            
            # Initialisation des champs
            role_select.on_value_change(update_role_fields)
            update_role_fields()
            
            # Boutons
            with ui.row().classes('w-full gap-4 q-mt-lg'):
                async def handle_submit():
                    # TODO: Implémenter l'enregistrement dans la BD
                    if password_input.value != confirm_password.value:
                        ui.notify('Les mots de passe ne correspondent pas', type='negative')
                        return
                    
                    ui.notify('Inscription réussie!', type='positive')
                    ui.navigate.to('/login')
                
                ui.button(
                    'CRÉER MON COMPTE',
                    on_click=handle_submit
                ).props('color=primary').classes('flex-1')
                
                ui.button(
                    'Déjà un compte? Se connecter',
                    on_click=lambda: ui.navigate.to('/login')
                ).props('flat color=primary').classes('flex-1')