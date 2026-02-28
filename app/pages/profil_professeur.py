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
            .profil-card .teacher-course-select .q-field__control {
                height: auto !important;
                min-height: 56px !important;
            }
            .profil-card .teacher-course-select .q-chip {
                margin: 2px;
                max-width: 100%;
            }
            .profil-card .teacher-course-select .q-field__control-container {
                padding-top: 8px;
                padding-bottom: 4px;
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
                        
                        # Build options as dict for dropdown display (token -> HTML label)
                        options_for_dropdown = build_subject_options_for_class(class_name)
                        
                        # Convert to simple labels for select values
                        simple_options = []
                        token_to_simple_label = {}
                        for token, html_label in options_for_dropdown.items():
                            simple_label = token_to_label(token)
                            simple_options.append(simple_label)
                            token_to_simple_label[token] = simple_label
                        
                        initial_tokens = class_branch_values.get(class_name, set())
                        initial_simple_labels = [token_to_simple_label.get(token) for token in initial_tokens if token in token_to_simple_label]
                        
                        # Display selected branches as comma-separated text
                        display_text = ', '.join(sorted(initial_simple_labels)) if initial_simple_labels else ''
                        
                        # Create a custom container with label on top and content below
                        with ui.column().classes('w-full q-mb-md').style('gap: 4px;'):
                            ui.label('Branches enseignées').classes('text-caption text-grey-7')
                            display_field = ui.element('div').classes('cursor-pointer').style(
                                'border: 1px solid #ccc; border-radius: 4px; padding: 12px 36px 12px 12px; '
                                'min-height: 40px; position: relative; background: white; word-wrap: break-word;'
                            )
                            with display_field:
                                display_content = ui.label(display_text).classes('text-body2')
                                ui.icon('arrow_drop_down').classes('cursor-pointer').style(
                                    'position: absolute; right: 8px; top: 50%; transform: translateY(-50%); color: #666;'
                                )
                        
                        # Create a hidden select to maintain the actual values
                        class_select = ui.select(
                            sorted(simple_options),
                            value=initial_simple_labels if initial_simple_labels else [],
                            multiple=True,
                        ).style('display: none;')
                        
                        # Dialog for selection
                        with ui.dialog() as branch_dialog, ui.card().style('min-width: 400px; max-width: 600px;'):
                            ui.label(f'{class_name} - Branches enseignées').classes('text-h6 q-mb-md')
                            
                            checkboxes_dict = {}
                            with ui.column().classes('w-full'):
                                for option_label in sorted(simple_options):
                                    cb = ui.checkbox(option_label, value=option_label in initial_simple_labels)
                                    checkboxes_dict[option_label] = cb
                            
                            def update_checkboxes(cls=class_name, label_mapping=dict(token_to_simple_label), cbs=checkboxes_dict):
                                # Get current tokens for this class
                                current_tokens = class_branch_values.get(cls, set())
                                current_labels = {label_mapping.get(token) for token in current_tokens if token in label_mapping}
                                # Update checkbox values
                                for label, cb in cbs.items():
                                    cb.value = label in current_labels
                            
                        from functools import partial
                        
                        # Use partial to bind the variables at creation time
                        def save_branches(e=None, cls=class_name, disp_content=display_content, sel=class_select, label_map=token_to_simple_label.copy(), cbs=checkboxes_dict, dlg=branch_dialog):
                            selected_labels = [lbl for lbl, cb in cbs.items() if cb.value]
                            
                            # Replace whole string value
                            disp_content.set_text(', '.join(sorted(selected_labels)))
                            
                            # Set actual selection array on hidden multi-select
                            sel.set_value(selected_labels)
                            
                            # Build the matching branch tokens
                            tokens = set()
                            for token, label in label_map.items():
                                if label in selected_labels:
                                    tokens.add(token)
                            
                            # IMPORTANT: Update the core dictionary used for saving to DB
                            class_branch_values[cls] = list(tokens) if tokens else []
                            
                            dlg.close()
                            
                        def open_dialog(e=None, update_fn=update_checkboxes, dlg=branch_dialog):
                            update_fn()
                            dlg.open()
                        
                        with ui.row().classes('w-full justify-end q-mt-lg q-mb-sm'):
                            ui.button('Valider', on_click=partial(save_branches)).props('color=primary').style('padding: 8px 24px;')
                        
                        display_field.on('click', partial(open_dialog))

                        class_branch_selects[class_name] = class_select

                        def on_change(event, cls=class_name, label_mapping=dict(token_to_simple_label)):
                            selected_labels = event.value or []
                            # Convert labels back to tokens
                            tokens = set()
                            for token, label in label_mapping.items():
                                if label in selected_labels:
                                    tokens.add(token)
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