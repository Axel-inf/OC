#aide de l'IA
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from nicegui import ui, app
from components.navbar import create_navbar
from database.database import get_db
from database.models import Utilisateur, Eleve, EleveChangementClasse
from database.calendar_repository import sync_student_calendar_for_class_change
from utils.school import (
    all_school_classes,
    student_language_1_options,
    student_language_options,
    student_oc_options,
    student_os_options,
)

def create():
    """Crée la page de profil pour un élève"""
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
    classe_value = '1GY1'
    niveau_maths_value = 'Mathématiques standards'
    langue1_value = 'Français'
    langue2_value = 'Anglais'
    langue3_value = 'Espagnol'
    os_value = 'Physique et application des mathématiques'
    oc_value = 'Physique'
    basic_english_value = False
    bilingue_value = False
    classes_catalog = all_school_classes()
    language_1_options = student_language_1_options()
    language_options = student_language_options()
    os_options = student_os_options()
    oc_options = student_oc_options()

    app.storage.user['profile_dirty'] = False

    def mark_profile_dirty() -> None:
        app.storage.user['profile_dirty'] = True
        ui.run_javascript('window.__profileDirty = true;')

    def mark_profile_clean() -> None:
        app.storage.user['profile_dirty'] = False
        ui.run_javascript('window.__profileDirty = false;')

    if user_id is not None:
        db = get_db()
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if user is not None:
                nom_value = user.nom or nom_value
                prenom_value = user.prenom or prenom_value
                email_value = user.email or email_value

            eleve = db.query(Eleve).filter(Eleve.utilisateur_id == user_id).first()
            if eleve is not None:
                classe_value = eleve.classe or classe_value
                niveau_maths_value = eleve.niveau_maths or niveau_maths_value
                langue1_value = eleve.langue1 or langue1_value
                langue2_value = eleve.langue2 or langue2_value
                langue3_value = eleve.langue3 or langue3_value
                os_value = eleve.os or os_value
                oc_value = eleve.oc or oc_value
                basic_english_value = bool(eleve.basic_english)
                bilingue_value = bool(eleve.bilingue)
        finally:
            db.close()
    
    ui.add_head_html('''
        <style>
            .inscription-container {
                background: var(--white);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
                overflow-x: hidden;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .inscription-card {
                background: transparent;
                padding: 0;
                border-radius: 0;
                border: none;
                box-shadow: none;
                width: min(370px, 100%);
                max-width: 100%;
                margin: 0 auto;
            }
            .inscription-header {
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .inscription-title {
                text-align: center;
                font-size: 28px;
                font-weight: 700;
                color: var(--text-dark);
                width: 100%;
                display: block;
                margin: 0 auto;
                margin: 0 auto 16px;
            }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                color: var(--primary);
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
            .inscription-card .q-field--outlined .q-field__label {
                left: 8px !important;
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
    
    with ui.column().classes('inscription-container'):
        with ui.card().classes('inscription-card'):
            # En-tête du profil
            with ui.element('div').classes('inscription-header'):
                ui.html('<div class="inscription-title">Profil</div>', sanitize=False)
            
            # Section Compte
            ui.html('<div class="section-title">Informations personnelles</div>', sanitize=False)

            with ui.element('div').classes('two-cols'):
                nom_input = ui.input('Nom', value=nom_value).props('outlined').classes('flex-1')
                prenom_input = ui.input('Prénom', value=prenom_value).props('outlined').classes('flex-1')

            email_input = ui.input('Email', value=email_value).props('outlined').classes('w-full q-mb-md')
            with ui.row().classes('w-full q-mb-md items-center justify-between').style('padding: 0 8px;'):
                ui.label('Mot de passe').classes('text-body2')
                ui.link('Réinitialiser le mot de passe', '/reinitialisation-mot-de-passe').classes('text-primary')
            
            # Section École
            ui.html('<div class="section-title">Informations scolaires</div>', sanitize=False)

            if classe_value and classe_value not in classes_catalog:
                classes_catalog = classes_catalog + [classe_value]

            classe_select = ui.select(
                classes_catalog,
                label='Classe',
                value=classe_value
            ).props('outlined').classes('w-full q-mb-md')
            
            maths_select = ui.select(
                ['Mathématiques renforcées', 'Mathématiques standards'],
                label='Niveau de mathématiques',
                value=niveau_maths_value
            ).props('outlined').classes('w-full q-mb-md')
            
            if langue1_value and langue1_value not in language_1_options:
                language_1_options = language_1_options + [langue1_value]
            if langue2_value and langue2_value not in language_options:
                language_options = language_options + [langue2_value]
            if langue3_value and langue3_value not in language_options:
                language_options = language_options + [langue3_value]

            with ui.element('div').classes('two-cols'):
                langue1 = ui.select(
                    language_1_options,
                    label='Langue 1',
                    value=langue1_value
                ).props('outlined').classes('flex-1')

                langue2 = ui.select(
                    language_options,
                    label='Langue 2',
                    value=langue2_value
                ).props('outlined').classes('flex-1')
            
            langue3 = ui.select(
                language_options,
                label='Langue 3',
                value=langue3_value
            ).props('outlined').classes('w-full q-mb-md')
            
            # Section Options
            ui.html('<div class="section-title">Options</div>', sanitize=False)
            
            if os_value and os_value not in os_options:
                os_options = os_options + [os_value]
            if oc_value and oc_value not in oc_options:
                oc_options = oc_options + [oc_value]

            os_input = ui.select(
                os_options,
                label='Option spécifique (OS)',
                value=os_value
            ).props('outlined').classes('w-full q-mb-md')

            oc_input = ui.select(
                oc_options,
                label='Option complémentaire (OC)',
                value=oc_value
            ).props('outlined').classes('w-full q-mb-md')
            
            with ui.element('div').classes('two-cols'):
                basic_english = ui.checkbox('Basic English', value=basic_english_value)
                bilingue = ui.checkbox('Bilingue', value=bilingue_value)

            nom_input.on_value_change(lambda _e: mark_profile_dirty())
            prenom_input.on_value_change(lambda _e: mark_profile_dirty())
            classe_select.on_value_change(lambda _e: mark_profile_dirty())
            maths_select.on_value_change(lambda _e: mark_profile_dirty())
            langue1.on_value_change(lambda _e: mark_profile_dirty())
            langue2.on_value_change(lambda _e: mark_profile_dirty())
            langue3.on_value_change(lambda _e: mark_profile_dirty())
            os_input.on_value_change(lambda _e: mark_profile_dirty())
            oc_input.on_value_change(lambda _e: mark_profile_dirty())
            basic_english.on_value_change(lambda _e: mark_profile_dirty())
            bilingue.on_value_change(lambda _e: mark_profile_dirty())
            
            # Boutons d'action
            with ui.row().classes('w-full gap-4 q-mt-lg'):
                async def handle_save():
                    db = get_db()
                    try:
                        user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
                        eleve = db.query(Eleve).filter(Eleve.utilisateur_id == user_id).first()
                        if user is None or eleve is None:
                            ui.notify('Profil introuvable', type='negative')
                            return

                        user.nom = (nom_input.value or '').strip() or user.nom
                        user.prenom = (prenom_input.value or '').strip() or user.prenom
                        previous_class = (eleve.classe or '').strip()
                        selected_class = (classe_select.value or '').strip()
                        updated_class = selected_class or previous_class
                        # Aide IA: enregistrement du changement de classe dans la BD pour traçabilité historique
                        if updated_class and updated_class != previous_class:
                            db.add(EleveChangementClasse(
                                eleve_id=eleve.id,
                                ancienne_classe=previous_class,
                                nouvelle_classe=updated_class,
                            ))
                        eleve.classe = updated_class
                        eleve.niveau_maths = (maths_select.value or '').strip() or eleve.niveau_maths
                        eleve.langue1 = (langue1.value or '').strip() or eleve.langue1
                        eleve.langue2 = (langue2.value or '').strip() or eleve.langue2
                        eleve.langue3 = (langue3.value or '').strip() or eleve.langue3
                        eleve.os = (os_input.value or '').strip() or eleve.os
                        eleve.oc = (oc_input.value or '').strip() or eleve.oc
                        eleve.basic_english = bool(basic_english.value)
                        eleve.bilingue = bool(bilingue.value)

                        db.commit()

                        if updated_class and updated_class != previous_class:
                            try:
                                hidden_count, created_count = sync_student_calendar_for_class_change(
                                    user_identifier=user.email,
                                    new_class=updated_class,
                                    langue1=(eleve.langue1 or ''),
                                    langue2=(eleve.langue2 or ''),
                                    langue3=(eleve.langue3 or ''),
                                    os_value=(eleve.os or ''),
                                    oc_value=(eleve.oc or ''),
                                    basic_english=bool(eleve.basic_english),
                                )
                                ui.notify(
                                    f'Calendrier synchronisé: {created_count} événement(s) ajouté(s), {hidden_count} masqué(s)',
                                    type='info',
                                )
                            except Exception:
                                ui.notify('Classe mise à jour, mais la synchronisation du calendrier a échoué', type='warning')

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