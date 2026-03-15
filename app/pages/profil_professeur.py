#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
from database.database import get_db
from database.models import Utilisateur, Enseignant
from utils.school import all_school_classes, os_subjects, oc_subjects
from utils.teacher_assignments import (
    build_subject_options_for_class,
    is_bilingual_choice_token,
    make_choice_token,
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
    ui.add_head_html('''
        <script>
            window.__profileDirty = false;
            window.addEventListener('beforeunload', function (event) {
                if (window.__profileDirty) {
                    event.preventDefault();
                    event.returnValue = '';
                }
            });
        </script>
    ''')

    nom_value = app.storage.user.get('nom', '')
    prenom_value = app.storage.user.get('prenom', '')
    email_value = app.storage.user.get('email', '')
    classes_values: list[str] = []
    class_branch_values: dict[str, set[str]] = {}
    class_os_values: dict[str, set[str]] = {}
    class_oc_values: dict[str, set[str]] = {}

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
                for class_name, tokens in parsed_assignments.items():
                    branch_tokens: set[str] = set()
                    os_tokens: set[str] = set()
                    oc_tokens: set[str] = set()
                    for token in tokens:
                        subject_name = subject_from_choice_token(token)
                        if subject_name.startswith('OS '):
                            os_tokens.add(token)
                        elif subject_name.startswith('OC '):
                            oc_tokens.add(token)
                        else:
                            branch_tokens.add(token)
                    class_branch_values[class_name] = branch_tokens
                    class_os_values[class_name] = os_tokens
                    class_oc_values[class_name] = oc_tokens
        finally:
            db.close()

    class_catalog = all_school_classes()
    selected_classes = set(classes_values)

    app.storage.user['profile_dirty'] = False

    def mark_profile_dirty() -> None:
        app.storage.user['profile_dirty'] = True
        ui.run_javascript('window.__profileDirty = true;')

    def mark_profile_clean() -> None:
        app.storage.user['profile_dirty'] = False
        ui.run_javascript('window.__profileDirty = false;')
    
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
            with ui.row().classes('w-full q-mb-md items-center justify-between').style('padding: 0 8px;'):
                ui.label('Mot de passe').classes('text-body2')
                ui.link('Réinitialiser le mot de passe', '/reinitialisation-mot-de-passe').classes('text-primary')
            
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
                for class_name in list(class_os_values.keys()):
                    if class_name not in ordered_classes:
                        class_os_values.pop(class_name, None)
                for class_name in list(class_oc_values.keys()):
                    if class_name not in ordered_classes:
                        class_oc_values.pop(class_name, None)

                if not ordered_classes:
                    with class_branches_box:
                        ui.label('Sélectionnez au moins une classe pour configurer les branches.').classes('field-caption q-mb-md')
                    return

                with class_branches_box:
                    for class_name in ordered_classes:
                        ui.html(f'<div class="section-title">{class_name}</div>', sanitize=False)
                        options_for_dropdown = build_subject_options_for_class(class_name)
                        branch_options: dict[str, str] = {}
                        # OS/OC must always be available, regardless of selected class.
                        os_options: dict[str, str] = {
                            make_choice_token(subject, 'standard'): subject
                            for subject in sorted(os_subjects())
                        }
                        oc_options: dict[str, str] = {
                            make_choice_token(subject, 'standard'): subject
                            for subject in sorted(oc_subjects())
                        }

                        for token in sorted(options_for_dropdown.keys()):
                            label = token_to_label(token)
                            if label.startswith('OS '):
                                os_options[token] = label
                            elif label.startswith('OC '):
                                oc_options[token] = label
                            else:
                                branch_options[token] = label

                        def render_selector_block(
                            field_label: str,
                            dialog_title: str,
                            option_map: dict[str, str],
                            values_store: dict[str, set[str]],
                        ) -> None:
                            current_tokens = set(values_store.get(class_name, set()))
                            selected_labels = [option_map[token] for token in current_tokens if token in option_map]
                            display_text = ', '.join(sorted(selected_labels)) if selected_labels else 'Aucune sélection'

                            with ui.column().classes('w-full q-mb-md').style('gap: 4px;'):
                                ui.label(field_label).classes('text-caption text-grey-7')
                                display_field = ui.element('div').classes('cursor-pointer').style(
                                    'border: 1px solid #ccc; border-radius: 4px; padding: 12px 36px 12px 12px; '
                                    'min-height: 40px; position: relative; background: white; word-wrap: break-word;'
                                )
                                with display_field:
                                    display_content = ui.label(display_text).classes('text-body2')
                                    ui.icon('arrow_drop_down').classes('cursor-pointer').style(
                                        'position: absolute; right: 8px; top: 50%; transform: translateY(-50%); color: #666;'
                                    )

                            sorted_items = sorted(option_map.items(), key=lambda item: item[1])

                            with ui.dialog().props('persistent') as selector_dialog:
                                with ui.card().style('min-width: 400px; max-width: 600px;'):
                                    ui.label(f'{class_name} - {dialog_title}').classes('text-h6 q-mb-md')

                                    with ui.row().classes('w-full justify-end q-mb-sm'):
                                        ui.button('Annuler', on_click=selector_dialog.close).props('flat')
                                        save_button = ui.button('Valider').props('color=primary')

                                    checkboxes_dict: dict[str, any] = {}
                                    with ui.column().classes('w-full'):
                                        for token, label in sorted_items:
                                            cb = ui.checkbox(label, value=token in current_tokens)
                                            checkboxes_dict[token] = cb

                                def update_checkboxes() -> None:
                                    latest_tokens = set(values_store.get(class_name, set()))
                                    for token, cb in checkboxes_dict.items():
                                        cb.value = token in latest_tokens

                            def save_selection() -> None:
                                selected_tokens = {token for token, cb in checkboxes_dict.items() if cb.value}
                                values_store[class_name] = selected_tokens
                                selected_display = [option_map[token] for token in selected_tokens if token in option_map]
                                display_content.set_text(', '.join(sorted(selected_display)) if selected_display else 'Aucune sélection')
                                mark_profile_dirty()
                                selector_dialog.close()

                            def open_dialog() -> None:
                                update_checkboxes()
                                selector_dialog.open()

                            save_button.on_click(save_selection)
                            display_field.on('click', lambda _e: open_dialog())

                        render_selector_block(
                            field_label='Branches enseignées',
                            dialog_title='Branches enseignées',
                            option_map=branch_options,
                            values_store=class_branch_values,
                        )
                        render_selector_block(
                            field_label='OS enseignées',
                            dialog_title='OS enseignées',
                            option_map=os_options,
                            values_store=class_os_values,
                        )
                        render_selector_block(
                            field_label='OC enseignées',
                            dialog_title='OC enseignées',
                            option_map=oc_options,
                            values_store=class_oc_values,
                        )

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
                                class_os_values.pop(cls, None)
                                class_oc_values.pop(cls, None)
                            mark_profile_dirty()
                            render_class_branch_sections()

                        checkbox.on_value_change(on_change)

            classes_search.on_value_change(lambda event: render_classes(event.value or ''))
            nom_input.on_value_change(lambda _e: mark_profile_dirty())
            prenom_input.on_value_change(lambda _e: mark_profile_dirty())
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
                            values = sorted(
                                set(class_branch_values.get(class_name, set()))
                                | set(class_os_values.get(class_name, set()))
                                | set(class_oc_values.get(class_name, set()))
                            )
                            if not values:
                                ui.notify(f'Sélectionnez au moins une branche/OS/OC pour la classe {class_name}', type='negative')
                                return
                            assignments_by_class[class_name] = values

                        all_tokens = [token for values in assignments_by_class.values() for token in values]
                        has_basic_english = any(subject_from_choice_token(token) == 'Basic English' for token in all_tokens)
                        has_bilingual_course = any(is_bilingual_choice_token(token) for token in all_tokens)

                        user.nom = (nom_input.value or '').strip() or user.nom
                        user.prenom = (prenom_input.value or '').strip() or user.prenom
                        enseignant.classes = ','.join(sorted(selected_classes))
                        enseignant.branches = serialize_teacher_assignments(assignments_by_class)
                        selected_os_subjects = sorted({
                            subject_from_choice_token(token).removeprefix('OS ').strip()
                            for values in class_os_values.values()
                            for token in values
                            if subject_from_choice_token(token).startswith('OS ')
                        })
                        selected_oc_subjects = sorted({
                            subject_from_choice_token(token).removeprefix('OC ').strip()
                            for values in class_oc_values.values()
                            for token in values
                            if subject_from_choice_token(token).startswith('OC ')
                        })
                        enseignant.os = ','.join(selected_os_subjects)
                        enseignant.oc = ','.join(selected_oc_subjects)
                        enseignant.basic_english = has_basic_english
                        enseignant.bilingue = has_bilingual_course

                        db.commit()
                        app.storage.user['nom'] = user.nom
                        app.storage.user['prenom'] = user.prenom
                        mark_profile_clean()
                        ui.notify('Profil mis à jour avec succès!', type='positive')
                    except Exception:
                        db.rollback()
                        ui.notify('Erreur lors de la sauvegarde du profil', type='negative')
                    finally:
                        db.close()
                
                async def handle_logout():
                    if app.storage.user.get('profile_dirty', False):
                        ui.notify('Veuillez enregistrer vos modifications', type='warning', timeout=3)
                        ui.run_javascript(
                            '''
                            const saveBtn = document.getElementById('profile-save-button');
                            if (saveBtn) saveBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            '''
                        )
                        return
                    app.storage.user.clear()
                    ui.notify('Déconnexion réussie', type='info')
                    ui.navigate.to('/login')
                
                save_button = ui.button(
                    'ENREGISTRER',
                    icon='save',
                    on_click=handle_save
                ).props('color=primary').classes('flex-1')
                save_button.props('id=profile-save-button')
                
                ui.button(
                    'SE DÉCONNECTER',
                    icon='logout',
                    on_click=handle_logout
                ).props('color=negative flat').classes('flex-1')
        
        # Navbar
        create_navbar()