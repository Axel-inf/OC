#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
from database.database import get_db
from database.models import Utilisateur, Enseignant
from utils.school import all_school_classes
from utils.school import all_teaching_subjects
from utils.auth import hash_password

def create():
    """Crée la page de profil pour un enseignant"""
    user_id = app.storage.user.get('user_id')

    nom_value = app.storage.user.get('nom', '')
    prenom_value = app.storage.user.get('prenom', '')
    email_value = app.storage.user.get('email', '')
    classes_values: list[str] = []
    branches_values: list[str] = []
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
                bilingue_value = bool(enseignant.bilingue)
        finally:
            db.close()

    class_catalog = all_school_classes()
    teaching_subjects = all_teaching_subjects()
    selected_classes = set(classes_values)
    
    ui.add_head_html('''
        <style>
            .profil-container {
                background: var(--white);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
                overflow-x: hidden;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .profil-card {
                background: transparent;
                padding: 0;
                border-radius: 0;
                box-shadow: none;
                width: min(600px, 100%);
                max-width: 100%;
                margin: 0 auto;
            }
            .profil-header {
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
                margin-bottom: 30px;
            }
            .profil-title {
                font-size: 28px;
                font-weight: 700;
                color: #333;
                margin-top: 0;
                width: 100%;
                text-align: center;
            }
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #667eea;
                margin: 25px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #667eea;
            }
            .profil-card .row {
                width: 100%;
                flex-wrap: wrap;
            }
            .profil-card .row > * {
                min-width: 0;
            }
            .profil-card .q-field__label {
                opacity: 1 !important;
                color: #666 !important;
            }
            .profil-card .q-field--outlined .q-field__label {
                left: 8px !important;
            }
            .profil-card .q-field--outlined .q-field__control::before,
            .profil-card .q-field--outlined .q-field__control::after,
            .profil-card .q-field--outlined.q-field--focused .q-field__control::before,
            .profil-card .q-field--outlined.q-field--focused .q-field__control::after {
                border-color: var(--border-light) !important;
                box-shadow: none !important;
            }
            .profil-card .q-field--focused .q-field__control::after {
                border-width: 1px !important;
                border-color: var(--border-light) !important;
            }
            .profil-card .q-field--focused .q-field__native,
            .profil-card .q-field--focused .q-field__prefix,
            .profil-card .q-field--focused .q-field__suffix,
            .profil-card .q-field--focused .q-field__input {
                color: var(--text-dark) !important;
            }
            .profil-card .q-field--focused .q-field__label,
            .profil-card .q-select--focused .q-field__label,
            .profil-card .q-select--focused .q-select__dropdown-icon {
                color: #666 !important;
            }
            .profil-card .q-field__native,
            .profil-card .q-field__input,
            .profil-card .q-select__selection,
            .profil-card .q-select__dropdown-icon {
                color: var(--text-dark) !important;
                opacity: 1 !important;
            }
            .profil-card .q-select .q-field__native {
                justify-content: center;
            }
            .profil-card .q-select .q-field__native > span {
                width: 100%;
                text-align: center;
            }
            .field-caption {
                width: 100%;
                font-size: 13px;
                color: var(--text-light);
                margin: 0 0 4px 0;
            }
            @media (max-width: 520px) {
                .profil-container {
                    padding: 12px 12px 92px 12px;
                }
                .profil-card {
                    padding: 0;
                    border-radius: 0;
                }
            }
        </style>
    ''')
    
    with ui.column().classes('profil-container'):
        with ui.card().classes('profil-card'):
            # En-tête du profil
            with ui.element('div').classes('profil-header'):
                ui.html('<div class="profil-title">Profil</div>', sanitize=False)
            
            # Section Compte
            ui.html('<div class="section-title">Compte</div>', sanitize=False)
            
            nom_input = ui.input('Nom', value=nom_value).props('outlined stack-label').classes('w-full q-mb-md')
            prenom_input = ui.input('Prénom', value=prenom_value).props('outlined stack-label').classes('w-full q-mb-md')
            email_input = ui.input('Email', value=email_value).props('outlined stack-label readonly').classes('w-full q-mb-md')
            password_input = ui.input('Mot de passe', password=True, password_toggle_button=True).props('outlined stack-label').classes('w-full q-mb-md')
            
            # Section École
            ui.html('<div class="section-title">École</div>', sanitize=False)
            
            classes_search = ui.input('Recherche classes', placeholder='Ex: 2GY1').props('outlined').classes('w-full q-mb-sm')
            classes_box = ui.column().classes('w-full q-mb-md').style('max-height: 180px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;')

            def render_classes(filter_value: str = '') -> None:
                classes_box.clear()
                normalized = (filter_value or '').strip().lower()
                filtered_classes = [
                    class_name
                    for class_name in class_catalog
                    if normalized in class_name.lower()
                ]

                with classes_box:
                    for class_name in filtered_classes:
                        checkbox = ui.checkbox(class_name, value=class_name in selected_classes)

                        def on_change(event, cls=class_name):
                            if event.value:
                                selected_classes.add(cls)
                            else:
                                selected_classes.discard(cls)

                        checkbox.on_value_change(on_change)

            classes_search.on_value_change(lambda event: render_classes(event.value or ''))
            render_classes()
            
            # Branches enseignées
            ui.label('Branches enseignées').classes('field-caption')
            branches_select = ui.select(
                teaching_subjects,
                label='Branches enseignées',
                value=branches_values,
                multiple=True
            ).props('outlined stack-label').classes('w-full q-mb-md')

            bilingue = ui.checkbox('Cours bilingues', value=bilingue_value).classes('q-mb-md')
            
            # Boutons d'action
            with ui.row().classes('w-full gap-4 q-mt-lg'):
                async def handle_save():
                    db = get_db()
                    try:
                        user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
                        enseignant = db.query(Enseignant).filter(Enseignant.utilisateur_id == user_id).first()
                        if user is None or enseignant is None:
                            ui.notify('Profil introuvable', type='negative')
                            return

                        user.nom = (nom_input.value or '').strip() or user.nom
                        user.prenom = (prenom_input.value or '').strip() or user.prenom
                        new_password = (password_input.value or '').strip()
                        if new_password:
                            if len(new_password) < 8:
                                ui.notify('Le mot de passe doit contenir au minimum 8 caractères', type='negative')
                                return
                            user.mot_de_passe = hash_password(new_password)

                        enseignant.classes = ','.join(sorted(selected_classes))
                        selected_branches = branches_select.value or []
                        enseignant.branches = ','.join(selected_branches)
                        enseignant.os = ''
                        enseignant.oc = ''
                        enseignant.basic_english = ('Basic English' in selected_branches)
                        enseignant.bilingue = bool(bilingue.value)

                        db.commit()
                        app.storage.user['nom'] = user.nom
                        app.storage.user['prenom'] = user.prenom
                        ui.notify('Profil mis à jour avec succès!', type='positive')
                    except Exception:
                        db.rollback()
                        ui.notify('Erreur lors de la sauvegarde du profil', type='negative')
                    finally:
                        db.close()
                
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