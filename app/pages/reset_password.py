from datetime import datetime, timedelta
from email.message import EmailMessage
import secrets
import smtplib
import ssl
import string

from nicegui import ui, app

from config.settings import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    SMTP_USE_TLS,
)
from database.database import get_db
from database.models import Utilisateur
from utils.auth import hash_password


RESET_CODE_LENGTH = 6
RESET_CODE_TTL_MINUTES = 15


def _generate_reset_code(length: int = RESET_CODE_LENGTH) -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def _send_reset_email(recipient_email: str, code: str, full_name: str) -> None:
    if not SMTP_HOST:
        raise RuntimeError('Configuration SMTP manquante (SMTP_HOST).')

    sender = SMTP_FROM_EMAIL or SMTP_USERNAME
    if not sender:
        raise RuntimeError('Configuration SMTP incomplète (SMTP_FROM_EMAIL ou SMTP_USERNAME).')

    message = EmailMessage()
    message['Subject'] = 'Code de réinitialisation du mot de passe'
    message['From'] = sender
    message['To'] = recipient_email
    message.set_content(
        f'Bonjour {full_name},\n\n'
        f'Votre code de réinitialisation est : {code}\n\n'
        f'Saisissez ce code sur la page de réinitialisation.\n'
        f'Ce code expire dans {RESET_CODE_TTL_MINUTES} minutes.\n\n'
        'Si vous n\'êtes pas à l\'origine de cette demande, ignorez cet email.'
    )

    if SMTP_USE_TLS:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls(context=context)
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        return

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)


def _get_reset_store() -> dict:
    store = app.storage.general.get('password_reset_codes')
    if not isinstance(store, dict):
        store = {}
        app.storage.general['password_reset_codes'] = store
    return store


def create():
    """Crée la page de réinitialisation du mot de passe."""
    ui.add_head_html('<link rel="stylesheet" href="/static/css/custom.css">')
    ui.add_head_html('''
        <style>
            .reset-container {
                min-height: 100vh;
                background: var(--white);
                padding: 20px;
                overflow-x: hidden;
                width: 100%;
            }
            .reset-card {
                width: min(370px, 100%);
                max-width: 100%;
                background: var(--white);
                padding: 20px;
                border-radius: 20px;
                border: 1px solid var(--border-light);
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                margin: 0 auto;
            }
            .reset-title {
                text-align: center;
                color: var(--text-dark);
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 10px;
            }
            .reset-subtitle {
                color: var(--text-light);
                font-size: 14px;
                margin-bottom: 14px;
                text-align: center;
            }
            .reset-button {
                width: 100%;
                background: var(--primary);
                color: var(--white);
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 4px;
            }
            .back-link {
                margin-top: 14px;
                text-align: center;
                font-size: 14px;
            }
            .back-link a {
                color: var(--primary);
                text-decoration: underline;
            }
        </style>
    ''')

    with ui.column().classes('reset-container items-center justify-start'):
        with ui.card().classes('reset-card'):
            ui.html('<div class="reset-title">Réinitialisation</div>', sanitize=False)
            ui.html('<div class="reset-subtitle">Entrez votre email pour recevoir les instructions</div>', sanitize=False)

            email_input = ui.input(
                label='Email',
                placeholder='john@college.edu',
            ).classes('w-full q-mb-md').props('outlined')

            verification_container = ui.column().classes('w-full').style('display: none;')

            with verification_container:
                code_input = ui.input(
                    label='Code de vérification',
                    placeholder='6 chiffres',
                ).classes('w-full q-mb-md').props('outlined maxlength=6')

                new_password_input = ui.input(
                    label='Nouveau mot de passe',
                    password=True,
                    password_toggle_button=True,
                ).classes('w-full q-mb-md').props('outlined')

                confirm_password_input = ui.input(
                    label='Confirmer le nouveau mot de passe',
                    password=True,
                    password_toggle_button=True,
                ).classes('w-full q-mb-md').props('outlined')

                validate_button = ui.button('VALIDER LE CODE').classes('reset-button q-mt-sm')

            async def handle_reset():
                email = (email_input.value or '').strip().lower()
                if not email:
                    ui.notify('Merci de saisir votre email', type='negative')
                    return

                db = get_db()
                try:
                    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
                    if user is None:
                        ui.notify('Aucun compte trouvé avec cet email.', type='negative')
                        return
                finally:
                    db.close()

                code = _generate_reset_code()
                expires_at = (datetime.utcnow() + timedelta(minutes=RESET_CODE_TTL_MINUTES)).isoformat()
                reset_store = _get_reset_store()
                reset_store[email] = {
                    'code': code,
                    'expires_at': expires_at,
                }
                app.storage.general['password_reset_codes'] = reset_store

                try:
                    full_name = f'{user.prenom} {user.nom}'.strip()
                    _send_reset_email(email, code, full_name or 'utilisateur')
                except Exception as exc:
                    ui.notify(f"Impossible d'envoyer l'email: {exc}", type='negative')
                    return

                verification_container.style('display: block;')
                ui.notify('Code envoyé par email. Vérifiez votre boîte de réception.', type='positive')

            async def handle_confirm_reset():
                email = (email_input.value or '').strip().lower()
                code_value = (code_input.value or '').strip()
                new_password = new_password_input.value or ''
                confirm_password = confirm_password_input.value or ''

                if not email or not code_value or not new_password or not confirm_password:
                    ui.notify('Merci de remplir tous les champs.', type='negative')
                    return

                if len(code_value) != RESET_CODE_LENGTH or not code_value.isdigit():
                    ui.notify('Le code doit contenir exactement 6 chiffres.', type='negative')
                    return

                if len(new_password) < 8:
                    ui.notify('Le mot de passe doit contenir au minimum 8 caractères.', type='negative')
                    return

                if new_password != confirm_password:
                    ui.notify('Les mots de passe ne correspondent pas.', type='negative')
                    return

                reset_store = _get_reset_store()
                code_payload = reset_store.get(email)
                if not code_payload:
                    ui.notify('Aucun code actif pour cet email. Demandez un nouveau code.', type='negative')
                    return

                expires_at_raw = code_payload.get('expires_at', '')
                try:
                    expires_at = datetime.fromisoformat(expires_at_raw)
                except ValueError:
                    expires_at = datetime.utcnow() - timedelta(seconds=1)

                if datetime.utcnow() > expires_at:
                    reset_store.pop(email, None)
                    app.storage.general['password_reset_codes'] = reset_store
                    ui.notify('Le code a expiré. Merci de demander un nouveau code.', type='negative')
                    return

                if code_payload.get('code') != code_value:
                    ui.notify('Code invalide.', type='negative')
                    return

                db = get_db()
                try:
                    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
                    if user is None:
                        ui.notify('Aucun compte trouvé avec cet email.', type='negative')
                        return

                    user.mot_de_passe = hash_password(new_password)
                    db.commit()
                    db.refresh(user)
                finally:
                    db.close()

                reset_store.pop(email, None)
                app.storage.general['password_reset_codes'] = reset_store

                app.storage.user['authenticated'] = True
                app.storage.user['email'] = user.email
                app.storage.user['role'] = user.role.value if hasattr(user.role, 'value') else user.role
                app.storage.user['user_id'] = user.id
                app.storage.user['nom'] = user.nom
                app.storage.user['prenom'] = user.prenom

                ui.notify('Mot de passe réinitialisé. Connexion réussie.', type='positive')
                ui.navigate.to('/accueil')

            ui.button('RENVOYER LE CODE', on_click=handle_reset).classes('reset-button')
            validate_button.on('click', handle_confirm_reset)
            ui.html('<div class="back-link"><a href="/login">Retour à la connexion</a></div>', sanitize=False)
