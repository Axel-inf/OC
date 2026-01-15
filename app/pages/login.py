from nicegui import ui, app

def create():
    """Crée la page de connexion"""
    
    # Style personnalisé
    ui.add_head_html('''
        <style>
            .login-container {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .login-card {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 400px;
            }
            .login-icon {
                width: 80px;
                height: 80px;
                background: #667eea;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 30px;
            }
            .login-title {
                text-align: center;
                color: #333;
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 30px;
            }
            .login-input {
                width: 100%;
                margin-bottom: 20px;
            }
            .login-button {
                width: 100%;
                background: #667eea;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 10px;
            }
            .login-links {
                text-align: center;
                margin-top: 20px;
                font-size: 14px;
            }
            .login-links a {
                color: #667eea;
                text-decoration: none;
            }
        </style>
    ''')
    
    with ui.column().classes('login-container'):
        with ui.card().classes('login-card'):
            # Icône de cadenas
            with ui.element('div').classes('login-icon'):
                ui.icon('lock', size='48px', color='white')
            
            # Titre
            ui.html('<div class="login-title">Connexion</div>', sanitize=False)
            
            # Formulaire
            email_input = ui.input(
                label='Email',
                placeholder='john@college.edu'
            ).classes('login-input').props('outlined')
            
            password_input = ui.input(
                label='Mot de passe',
                placeholder='Entrez votre mot de passe',
                password=True,
                password_toggle_button=True
            ).classes('login-input').props('outlined')
            
            # Case à cocher "Rester connecté"
            remember_checkbox = ui.checkbox('Rester connecté').classes('q-mb-md')
            
            # Bouton de connexion
            async def handle_login():
                # TODO: Implémenter la logique d'authentification avec la BD
                email = email_input.value
                password = password_input.value
                
                if email and password:
                    # Simulation d'authentification (à remplacer par vraie logique)
                    app.storage.user['authenticated'] = True
                    app.storage.user['email'] = email
                    app.storage.user['role'] = 'eleve'  # À déterminer depuis la BD
                    
                    ui.notify('Connexion réussie!', type='positive')
                    ui.navigate.to('/accueil')
                else:
                    ui.notify('Veuillez remplir tous les champs', type='negative')
            
            ui.button('SE CONNECTER', on_click=handle_login).classes('login-button')
            
            # Liens
            with ui.element('div').classes('login-links'):
                ui.label('Pas de compte? ')
                ui.link('Créer un compte', '/inscription').style('color: #667eea; font-weight: 600;')
                ui.label(' | ')
                ui.link('Mot de passe oublié?', '#').style('color: #667eea;')
            
            # Lien de retour
            with ui.element('div').classes('login-links').style('margin-top: 30px;'):
                ui.label('Déjà un compte? ')
                ui.link('Pourquoi ne pas le créer?', '/inscription').style('color: #667eea; font-weight: 600;')