#aide de l'IA
from nicegui import ui, app

from database.database import get_db
from database.models import Utilisateur, Eleve, Enseignant, RoleEnum
from utils.auth import hash_password
from utils.school import (
    all_school_classes,
    student_language_1_options,
    student_language_options,
    student_oc_options,
    student_os_options,
)
from utils.teacher_assignments import (
    build_subject_options_for_class,
    is_bilingual_choice_token,
    serialize_teacher_assignments,
    subject_from_choice_token,
    token_to_html_label,
)


def is_valid_email(email: str) -> bool:
    if not email or '@' not in email:
        return False
    local_part, _, domain_part = email.partition('@')
    return bool(local_part and domain_part and '.' in domain_part and not domain_part.startswith('.') and not domain_part.endswith('.'))

def create():
    """Crée la page d'inscription"""
    ui.timer(0.05, lambda: ui.run_javascript('window.scrollTo(0, 0);'), once=True)
    ui.add_head_html('<link rel="stylesheet" href="/static/css/custom.css">')
    ui.add_head_html('''
        <style>
            .inscription-container {
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
                background: var(--white);
                overflow-x: hidden;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .inscription-card {
                width: min(370px, 100%);
                max-width: 100%;
                background: transparent;
                padding: 0;
                border-radius: 0;
                border: none;
                box-shadow: none;
                margin: 0 auto;
            }
            .inscription-title {
                text-align: center;
                color: var(--text-dark);
                font-size: 28px;
                font-weight: 700;
                width: 100%;
                display: block;
                margin: 0 auto 16px;
            }
            .inscription-header {
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .inscription-card .q-field--outlined .q-field__label {
                left: 8px !important;
            }
            .section-title {
                color: var(--primary);
                font-size: 16px;
                font-weight: 600;
                margin: 16px 0 10px 0;
                padding-bottom: 6px;
                border-bottom: 2px solid var(--secondary);
            }
            .two-cols {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                width: 100%;
            }
            .inscription-card .q-field {
                padding: 0 8px;
                box-sizing: border-box;
            }
            .inscription-card .q-field__control {
                border-radius: 8px !important;
            }
            @media (max-width: 520px) {
                .inscription-container {
                    padding: 12px 12px 92px 12px;
                }
                .inscription-card {
                    padding: 0;
                    border-radius: 0;
                }
                .two-cols {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    ''')

    student_fields: dict[str, any] = {}
    teacher_fields: dict[str, any] = {}
    classes_catalog = all_school_classes()
    language_1_options = student_language_1_options()
    language_options = student_language_options()
    os_options = student_os_options()
    oc_options = student_oc_options()
    
    with ui.column().classes('inscription-container'):
        with ui.card().classes('inscription-card'):
            with ui.element('div').classes('inscription-header'):
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
            
            with ui.element('div').classes('two-cols'):
                nom_input = ui.input('Nom').props('outlined').classes('flex-1')
                prenom_input = ui.input('Prénom').props('outlined').classes('flex-1')
            
            email_input = ui.input(
                'Email',
                placeholder='votre.email@college.edu'
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.element('div').classes('two-cols'):
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
                student_fields.clear()
                teacher_fields.clear()
                
                with role_specific_container:
                    if role_select.value == 'Élève':
                        create_student_fields()
                    else:
                        create_teacher_fields()
            
            def create_student_fields():
                """Crée les champs spécifiques aux élèves"""
                ui.html('<div class="section-title">Informations scolaires</div>', sanitize=False)

                student_fields['classe'] = ui.select(
                    classes_catalog,
                    label='Classe',
                    value='1GY1'
                ).props('outlined').classes('w-full q-mb-md')

                student_fields['niveau_maths'] = ui.select(
                    ['Mathématiques renforcées', 'Mathématiques standards'],
                    label='Niveau de mathématiques',
                    value='Mathématiques standards'
                ).props('outlined').classes('w-full q-mb-md')

                with ui.element('div').classes('two-cols'):
                    student_fields['langue1'] = ui.select(
                        language_1_options,
                        label='Langue 1',
                        value='Français'
                    ).props('outlined').classes('flex-1')

                    student_fields['langue2'] = ui.select(
                        language_options,
                        label='Langue 2',
                        value='Anglais'
                    ).props('outlined').classes('flex-1')

                student_fields['langue3'] = ui.select(
                    language_options,
                    label='Langue 3',
                    value='Espagnol'
                ).props('outlined').classes('w-full q-mb-md')

                ui.html('<div class="section-title">Options</div>', sanitize=False)

                student_fields['os'] = ui.select(
                    os_options,
                    label='Option spécifique (OS)',
                    value='Physique et application des mathématiques'
                ).props('outlined').classes('w-full q-mb-md')

                student_fields['oc'] = ui.select(
                    oc_options,
                    label='Option complémentaire (OC)',
                    value='Physique'
                ).props('outlined').classes('w-full q-mb-md')

                with ui.element('div').classes('two-cols'):
                    student_fields['basic_english'] = ui.checkbox('Basic English')
                    student_fields['bilingue'] = ui.checkbox('Bilingue')
            
            def create_teacher_fields():
                """Crée les champs spécifiques aux enseignants"""
                ui.html('<div class="section-title">Informations professionnelles</div>', sanitize=False)

                teacher_fields['classes_search'] = ui.input(
                    'Recherche classes',
                    placeholder='Ex: 2GY1'
                ).props('outlined').classes('w-full q-mb-sm')
                teacher_fields['classes_selected'] = set()
                teacher_fields['classes_checkboxes'] = []
                teacher_fields['class_branch_values'] = {}
                teacher_fields['class_branch_selects'] = {}
                teacher_fields['classes_box'] = ui.column().classes('w-full q-mb-md').style('max-height: 180px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;')
                teacher_fields['class_branches_box'] = ui.column().classes('w-full')

                def render_class_branch_sections() -> None:
                    branches_box = teacher_fields['class_branches_box']
                    branch_values = teacher_fields['class_branch_values']
                    teacher_fields['class_branch_selects'] = {}
                    branches_box.clear()

                    selected_classes = sorted(teacher_fields['classes_selected'])
                    for class_name in list(branch_values.keys()):
                        if class_name not in selected_classes:
                            branch_values.pop(class_name, None)

                    if not selected_classes:
                        with branches_box:
                            ui.label('Sélectionnez au moins une classe pour configurer les branches.').classes('field-caption q-mb-md')
                        return

                    with branches_box:
                        for class_name in selected_classes:
                            ui.html(f'<div class="section-title">{class_name}</div>', sanitize=False)
                            options = build_subject_options_for_class(class_name)
                            initial_tokens = set(branch_values.get(class_name, set()))
                            allowed_values = set(options.keys())
                            initial_values = [token for token in initial_tokens if token in allowed_values]

                            class_select = ui.select(
                                options,
                                label=f'Cours donnés en {class_name}',
                                value=initial_values,
                                multiple=True,
                            ).props('outlined options-html').classes('w-full q-mb-md')

                            teacher_fields['class_branch_selects'][class_name] = class_select

                            def on_change(event, cls=class_name):
                                selected_values = event.value or []
                                tokens = {str(token).strip() for token in selected_values if str(token).strip()}
                                branch_values[cls] = tokens

                            class_select.on_value_change(on_change)

                def render_classes(filter_value: str = '') -> None:
                    classes_box = teacher_fields['classes_box']
                    classes_box.clear()
                    teacher_fields['classes_checkboxes'].clear()

                    normalized = (filter_value or '').strip().lower()
                    filtered_classes = [
                        class_name
                        for class_name in classes_catalog
                        if normalized in class_name.lower()
                    ]

                    with classes_box:
                        for class_name in filtered_classes:
                            checkbox = ui.checkbox(
                                class_name,
                                value=class_name in teacher_fields['classes_selected'],
                            )

                            def on_change(event, cls=class_name):
                                if event.value:
                                    teacher_fields['classes_selected'].add(cls)
                                else:
                                    teacher_fields['classes_selected'].discard(cls)
                                    teacher_fields['class_branch_values'].pop(cls, None)
                                render_class_branch_sections()

                            checkbox.on_value_change(on_change)
                            teacher_fields['classes_checkboxes'].append(checkbox)

                teacher_fields['classes_search'].on_value_change(
                    lambda event: render_classes(event.value or '')
                )
                render_classes()
                render_class_branch_sections()
            
            # Initialisation des champs
            role_select.on_value_change(update_role_fields)
            update_role_fields()
            
            # Boutons
            with ui.element('div').classes('two-cols').style('margin-top: 16px;'):
                async def handle_submit():
                    nom_value = (nom_input.value or '').strip()
                    prenom_value = (prenom_input.value or '').strip()
                    email_value = (email_input.value or '').strip().lower()
                    password_value = password_input.value or ''
                    confirm_value = confirm_password.value or ''

                    if not nom_value or not prenom_value or not email_value or not password_value:
                        ui.notify('Merci de remplir tous les champs obligatoires', type='negative')
                        return

                    if not is_valid_email(email_value):
                        ui.notify('Adresse email invalide (format attendu: nom@domaine.xx)', type='negative')
                        return

                    if len(password_value) < 8:
                        ui.notify('Le mot de passe doit contenir au minimum 8 caractères', type='negative')
                        return

                    if password_value != confirm_value:
                        ui.notify('Les mots de passe ne correspondent pas', type='negative')
                        return

                    db = get_db()
                    try:
                        existing_user = db.query(Utilisateur).filter(Utilisateur.email == email_value).first()
                        if existing_user:
                            ui.notify('Un compte existe déjà avec cet email', type='negative')
                            return

                        selected_role = RoleEnum.ELEVE if role_select.value == 'Élève' else RoleEnum.ENSEIGNANT
                        user = Utilisateur(
                            email=email_value,
                            mot_de_passe=hash_password(password_value),
                            nom=nom_value,
                            prenom=prenom_value,
                            role=selected_role,
                        )
                        db.add(user)
                        db.flush()

                        if selected_role == RoleEnum.ELEVE:
                            db.add(Eleve(
                                utilisateur_id=user.id,
                                classe=student_fields['classe'].value,
                                niveau_maths=student_fields['niveau_maths'].value,
                                langue1=student_fields['langue1'].value,
                                langue2=student_fields['langue2'].value,
                                langue3=student_fields['langue3'].value,
                                os=student_fields['os'].value,
                                oc=student_fields['oc'].value,
                                basic_english=bool(student_fields['basic_english'].value),
                                bilingue=bool(student_fields['bilingue'].value),
                            ))
                        else:
                            selected_classes = sorted(teacher_fields['classes_selected'])
                            if not selected_classes:
                                ui.notify('Merci de sélectionner au moins une classe', type='negative')
                                return

                            class_branch_values = teacher_fields['class_branch_values']
                            assignments_by_class: dict[str, list[str]] = {}
                            for class_name in selected_classes:
                                values = sorted(set(class_branch_values.get(class_name, set())))
                                if not values:
                                    ui.notify(f'Sélectionnez au moins une branche pour la classe {class_name}', type='negative')
                                    return
                                assignments_by_class[class_name] = values

                            all_tokens = [token for values in assignments_by_class.values() for token in values]
                            has_basic_english = any(subject_from_choice_token(token) == 'Basic English' for token in all_tokens)
                            has_bilingual_course = any(is_bilingual_choice_token(token) for token in all_tokens)

                            db.add(Enseignant(
                                utilisateur_id=user.id,
                                branches=serialize_teacher_assignments(assignments_by_class),
                                classes=','.join(selected_classes),
                                os='',
                                oc='',
                                basic_english=has_basic_english,
                                bilingue=has_bilingual_course,
                            ))

                        db.commit()
                    except Exception:
                        db.rollback()
                        ui.notify('Erreur lors de la création du compte', type='negative')
                        return
                    finally:
                        db.close()
                    
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