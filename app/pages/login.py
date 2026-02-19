#aide de l'IA
from nicegui import ui, app
from utils.auth import authenticate_user

def create():
    """Crée la page de connexion"""
    ui.timer(0.05, lambda: ui.run_javascript('window.scrollTo(0, 0);'), once=True)
    ui.add_head_html('<link rel="stylesheet" href="/static/css/custom.css">')
    ui.add_head_html('''
        <style>
            .login-container {
                min-height: 100vh;
                background: var(--white);
                padding: 20px 20px 32px 20px;
                overflow-x: hidden;
            }
            .login-card {
                width: 370px;
                max-width: 100%;
                background: var(--white);
                padding: 20px;
                border-radius: 20px;
                border: 1px solid var(--border-light);
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            }
            .login-icon {
                width: 64px;
                height: 64px;
                background: var(--primary);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 12px;
            }
            .login-title {
                text-align: center;
                color: var(--text-dark);
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 16px;
            }
            .login-input {
                width: 100%;
                margin-bottom: 12px;
            }
            .login-button {
                width: 100%;
                background: var(--primary);
                color: var(--white);
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 6px;
            }
            .login-links {
                text-align: center;
                margin-top: 14px;
                font-size: 14px;
                color: var(--text-light);
            }
            .login-links a {
                color: var(--primary);
                text-decoration: none;
            }
            .login-subtitle {
                width: 100%;
                height: 32px;
                background-color: var(--secondary);
                border-radius: 8px;
                display: flex;
                justify-content: center;
                align-items: center;
                color: var(--white);
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 16px;
            }
        </style>
    ''')
    
    with ui.column().classes('login-container items-center justify-start'):
        with ui.card().classes('login-card'):
            with ui.element('div').classes('login-icon'):
                ui.icon('lock', size='48px', color='white')

            ui.html('<div class="login-title">Connexion</div>', sanitize=False)
            ui.html('<div class="login-subtitle">Accès à votre espace</div>', sanitize=False)
            
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
            
            remember_checkbox = ui.checkbox('Rester connecté').classes('q-mb-md')
            
            async def handle_login():
                email = email_input.value
                password = password_input.value
                if not email or not password:
                    ui.notify('Veuillez remplir tous les champs', type='negative')
                    return

                user = authenticate_user(email, password)
                if user:
                    app.storage.user['authenticated'] = True
                    app.storage.user['email'] = user.email
                    app.storage.user['role'] = user.role.value if hasattr(user.role, 'value') else user.role
                    app.storage.user['user_id'] = user.id
                    app.storage.user['nom'] = user.nom
                    app.storage.user['prenom'] = user.prenom
                    ui.notify('Connexion réussie!', type='positive')
                    ui.navigate.to('/accueil')
                else:
                    ui.notify('Email ou mot de passe incorrect', type='negative')
            
            ui.button('SE CONNECTER', on_click=handle_login).classes('login-button')
            
            with ui.element('div').classes('login-links'):
                ui.label('Pas de compte? ')
                ui.link('Créer un compte', '/inscription').style('color: var(--primary); font-weight: 600;')
                ui.label(' | ')
                ui.link('Mot de passe oublié?', '#').style('color: var(--primary);')
            
            