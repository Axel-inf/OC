#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
from database.database import get_db
from database.models import Utilisateur, Enseignant
from utils.school import all_school_classes
from utils.auth import hash_password
from utils.teacher_assignments import (
    build_subject_options_for_class,
    is_bilingual_choice_token,
    parse_teacher_assignments,
    serialize_teacher_assignments,
    subject_from_choice_token,
    token_to_html_label,
    token_to_label,
)

def create():
    """Crée la page de profil pour un enseignant"""
    user_id = app.storage.user.get('user_id')

    ui.add_head_html('<link rel="stylesheet" href="/static/css/custom.css">')

    nom_value = app.storage.user.get('nom', '')
    prenom_value = app.storage.user.get('prenom', '')
    email_value = app.storage.user.get('email', '')
    classes_values: list[str] = []
    class_branch_values: dict[str, set[str]] = {}

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
                parsed_assignments = parse_teacher_assignments(enseignant.branches, enseignant.classes)
                classes_values = sorted(parsed_assignments.keys())
                class_branch_values = {
                    class_name: set(tokens)
                    for class_name, tokens in parsed_assignments.items()
                }
        finally:
            db.close()

    class_catalog = all_school_classes()
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
                color: var(--text-dark);
                margin-top: 0;
                width: 100%;
                text-align: center;
            }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                color: var(--primary);
                margin: 16px 0 10px 0;
                padding-bottom: 6px;
                border-bottom: 2px solid var(--secondary);
            }
            .profil-card .row {
                width: 100%;
                flex-wrap: wrap;
            }
            .profil-card .row > * {
                min-width: 0;
            }
            .profil-card .q-field--outlined .q-field__label {
                left: 8px !important;
            }
            .profil-card .q-field {
                padding: 0 8px;
                box-sizing: border-box;
            }
            .profil-card .q-field__control {
                border-radius: 8px !important;
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
            
            nom_input = ui.input('Nom', value=nom_value).props('outlined').classes('w-full q-mb-md')
            prenom_input = ui.input('Prénom', value=prenom_value).props('outlined').classes('w-full q-mb-md')
            email_input = ui.input('Email', value=email_value).props('outlined readonly').classes('w-full q-mb-md')
            password_input = ui.input('Mot de passe', password=True, password_toggle_button=True).props('outlined').classes('w-full q-mb-md')
            
            # Section École
            ui.html('<div class="section-title">École</div>', sanitize=False)
            
            classes_search = ui.input('Recherche classes', placeholder='Ex: 2GY1').props('outlined').classes('w-full q-mb-sm')
            classes_box = ui.column().classes('w-full q-mb-md').style('max-height: 180px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;')
            class_branches_box = ui.column().classes('w-full')
            class_branch_selects: dict[str, any] = {}

            def render_class_branch_sections() -> None:
                class_branches_box.clear()
                class_branch_selects.clear()

                ordered_classes = sorted(selected_classes)
                for class_name in list(class_branch_values.keys()):
                    if class_name not in ordered_classes:
                        class_branch_values.pop(class_name, None)

                if not ordered_classes:
                    with class_branches_box:
                        ui.label('Sélectionnez au moins une classe pour configurer les branches.').classes('field-caption q-mb-md')
                    return

                with class_branches_box:
                    for class_name in ordered_classes:
                        ui.html(f'<div class="section-title">{class_name}</div>', sanitize=False)
                        options = build_subject_options_for_class(class_name)
                        initial_tokens = set(class_branch_values.get(class_name, set()))
                        allowed_values = set(options.keys())
                        initial_values = [token for token in initial_tokens if token in allowed_values]

                        class_select = ui.select(
                            options,
                            label=f'Cours donnés en {class_name}',
                            value=initial_values,
                            multiple=True,
                        ).props('outlined options-html use-chips').classes('w-full q-mb-md')

                        class_branch_selects[class_name] = class_select

                        def on_change(event, cls=class_name):
                            selected_values = event.value or []
                            tokens = {str(token).strip() for token in selected_values if str(token).strip()}
                            class_branch_values[cls] = tokens

                        class_select.on_value_change(on_change)

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
                                class_branch_values.pop(cls, None)
                            render_class_branch_sections()

                        checkbox.on_value_change(on_change)

            classes_search.on_value_change(lambda event: render_classes(event.value or ''))
            render_classes()
            render_class_branch_sections()
            
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

                        if not selected_classes:
                            ui.notify('Merci de sélectionner au moins une classe', type='negative')
                            return

                        assignments_by_class: dict[str, list[str]] = {}
                        for class_name in sorted(selected_classes):
                            values = sorted(set(class_branch_values.get(class_name, set())))
                            if not values:
                                ui.notify(f'Sélectionnez au moins une branche pour la classe {class_name}', type='negative')
                                return
                            assignments_by_class[class_name] = values

                        all_tokens = [token for values in assignments_by_class.values() for token in values]
                        has_basic_english = any(subject_from_choice_token(token) == 'Basic English' for token in all_tokens)
                        has_bilingual_course = any(is_bilingual_choice_token(token) for token in all_tokens)

                        user.nom = (nom_input.value or '').strip() or user.nom
                        user.prenom = (prenom_input.value or '').strip() or user.prenom
                        new_password = (password_input.value or '').strip()
                        if new_password:
                            if len(new_password) < 8:
                                ui.notify('Le mot de passe doit contenir au minimum 8 caractères', type='negative')
                                return
                            user.mot_de_passe = hash_password(new_password)

                        enseignant.classes = ','.join(sorted(selected_classes))
                        enseignant.branches = serialize_teacher_assignments(assignments_by_class)
                        enseignant.os = ''
                        enseignant.oc = ''
                        enseignant.basic_english = has_basic_english
                        enseignant.bilingue = has_bilingual_course

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