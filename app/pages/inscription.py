#aide de l'IA
from nicegui import ui, app

from database.database import get_db
from database.models import Utilisateur, Eleve, Enseignant, RoleEnum
from utils.auth import hash_password


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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                overflow-x: hidden;
            }
            .inscription-card {
                width: 370px;
                max-width: 100%;
                background: var(--white);
                padding: 20px;
                border-radius: 20px;
                border: 1px solid var(--border-light);
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                margin: 0 auto;
            }
            .inscription-title {
                text-align: center;
                color: var(--text-dark);
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 12px;
            }
            .section-title {
                color: var(--primary);
                font-size: 16px;
                font-weight: 600;
                margin: 16px 0 10px 0;
                padding-bottom: 6px;
                border-bottom: 2px solid var(--secondary);
            }
            .inscription-subtitle {
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
                margin-bottom: 12px;
            }
            .two-cols {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                width: 100%;
            }
            .inscription-card .q-field__control {
                border-radius: 12px !important;
            }
        </style>
    ''')

    student_fields: dict[str, any] = {}
    teacher_fields: dict[str, any] = {}
    
    with ui.column().classes('inscription-container'):
        with ui.card().classes('inscription-card'):
            ui.html('<div class="inscription-title">Inscription</div>', sanitize=False)
            ui.html('<div class="inscription-subtitle">Création de compte</div>', sanitize=False)
            
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
                    [
                        *[f'1GY{i}' for i in range(1, 13)],
                        *[f'4GY{i}' for i in range(1, 13)],
                        *[f'3GY{i}' for i in range(1, 13)],
                        *[f'2GY{i}' for i in range(1, 13)],
                    ],
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
                        ['Français'],
                        label='Langue 1',
                        value='Français'
                    ).props('outlined').classes('flex-1')

                    student_fields['langue2'] = ui.select(
                        ['Allemand', 'Anglais', 'Espagnol', 'Grec', 'Italien', 'Latin (débutants)', 'Latin (avancés)'],
                        label='Langue 2',
                        value='Anglais'
                    ).props('outlined').classes('flex-1')

                student_fields['langue3'] = ui.select(
                    ['Allemand', 'Anglais', 'Espagnol', 'Grec', 'Italien', 'Latin (débutants)', 'Latin (avancés)'],
                    label='Langue 3',
                    value='Espagnol'
                ).props('outlined').classes('w-full q-mb-md')

                ui.html('<div class="section-title">Options</div>', sanitize=False)

                student_fields['os'] = ui.select(
                    ['Arts visuels', 'Anglais', 'Biologie et chimie', 'Économie et droit', 'Espagnol', 'Grec', 'Italien',
                     'Latin (débutants)', 'Latin (avancés)', 'Musique', 'Physique et application des mathématiques'],
                    label='Option spécifique (OS)',
                    value='Physique et application des mathématiques'
                ).props('outlined').classes('w-full q-mb-md')

                student_fields['oc'] = ui.select(
                    ['Applications des mathématiques', 'Arts visuels', 'Biologie', 'Chimie', 'Économie et droit', 'Géographie',
                     'Histoire', 'Informatique', 'Musique', 'Philosophie', 'Physique', 'Psychologie et pédagogie',
                     'Sciences politiques', 'Sciences religieuses', 'Sport'],
                    label='Option complémentaire (OC)',
                    value='Physique'
                ).props('outlined').classes('w-full q-mb-md')

                with ui.element('div').classes('two-cols'):
                    student_fields['basic_english'] = ui.checkbox('Basic English')
                    student_fields['bilingue'] = ui.checkbox('Bilingue')
            
            def create_teacher_fields():
                """Crée les champs spécifiques aux enseignants"""
                ui.html('<div class="section-title">Informations professionnelles</div>', sanitize=False)
                
                teacher_fields['branches'] = ui.input(
                    'Branche(s) enseignée(s)',
                    placeholder='Ex: Mathématiques, Physique'
                ).props('outlined').classes('w-full q-mb-md')
                
                teacher_fields['classes'] = ui.input(
                    'Classe(s)',
                    placeholder='Ex: 9VG1, 10VG2, 11VG3'
                ).props('outlined').classes('w-full q-mb-md')
                
                ui.html('<div class="section-title">Options enseignées</div>')
                
                teacher_fields['os'] = ui.input('Option spécifique (OS)').props('outlined').classes('w-full q-mb-md')
                teacher_fields['oc'] = ui.input('Option complémentaire (OC)').props('outlined').classes('w-full q-mb-md')
                
                with ui.element('div').classes('two-cols'):
                    teacher_fields['basic_english'] = ui.checkbox('Basic English')
                    teacher_fields['bilingue'] = ui.checkbox('Cours bilingues')
            
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
                            db.add(Enseignant(
                                utilisateur_id=user.id,
                                branches=(teacher_fields['branches'].value or '').strip(),
                                classes=(teacher_fields['classes'].value or '').strip(),
                                os=(teacher_fields['os'].value or '').strip(),
                                oc=(teacher_fields['oc'].value or '').strip(),
                                basic_english=bool(teacher_fields['basic_english'].value),
                                bilingue=bool(teacher_fields['bilingue'].value),
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