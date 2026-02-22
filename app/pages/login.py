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
                width: 100%;
                display: flex;
                align-items: flex-start;
                justify-content: center;
            }
            .login-card {
                width: min(370px, 100%);
                max-width: 100%;
                background: var(--white);
                padding: 20px;
                border-radius: 20px;
                border: 1px solid var(--border-light);
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                margin: 0 auto;
                align-self: center;
            }
            .login-icon {
                width: 64px;
                height: 64px;
                background: var(--primary);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 14px;
            }
            .login-title {
                text-align: center;
                color: var(--text-dark);
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 14px;
            }
            .login-input {
                width: 100%;
                margin-bottom: 12px;
                padding: 0 8px;
                box-sizing: border-box;
            }
            .password-help {
                width: 100%;
                text-align: left;
                color: var(--text-light);
                font-size: 12px;
                margin-top: -6px;
                margin-bottom: 10px;
                padding: 0 8px;
            }
            .forgot-row {
                width: 100%;
                text-align: right;
                margin-bottom: 14px;
                padding: 0 8px;
                box-sizing: border-box;
            }
            .forgot-link {
                color: var(--primary);
                text-decoration: underline;
                font-size: 14px;
                font-weight: 500;
            }
            .login-button {
                width: 100%;
                background: var(--primary);
                color: var(--white);
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 0;
            }
            .login-divider {
                width: 100%;
                display: flex;
                align-items: center;
                margin: 16px 0 12px 0;
            }
            .login-divider::before,
            .login-divider::after {
                content: '';
                flex: 1;
                height: 1px;
                background: #c8c8c8;
            }
            .login-divider span {
                color: var(--text-light);
                font-size: 13px;
                margin: 0 10px;
            }
            .signup-row {
                width: 100%;
                text-align: right;
                color: var(--text-light);
                font-size: 14px;
                padding: 0 8px;
                box-sizing: border-box;
            }
            .signup-link {
                color: var(--primary);
                text-decoration: underline;
                font-weight: 600;
            }
            @media (max-width: 420px) {
                .login-container {
                    padding: 12px 12px 24px 12px;
                }
                .login-card {
                    padding: 16px;
                    border-radius: 14px;
                }
            }
        </style>
    ''')
    
    with ui.column().classes('login-container items-center justify-start'):
        with ui.card().classes('login-card'):
            ui.html('<div class="login-title">Connexion</div>', sanitize=False)

            with ui.element('div').classes('login-icon'):
                ui.icon('lock', size='48px', color='white')
            
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

            ui.html('<div class="password-help">8 caractères minimum</div>', sanitize=False)

            ui.html('<div class="forgot-row"><a class="forgot-link" href="/reinitialisation-mot-de-passe">Mot de passe oublié?</a></div>', sanitize=False)
            
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

            ui.html('<div class="login-divider"><span>ou</span></div>', sanitize=False)


            ui.html('<div class="signup-row">Pas de compte? <a class="signup-link" href="/inscription">Inscrivez-vous</a></div>', sanitize=False)
            
            