#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
import re
from datetime import date
import calendar
from database.calendar_repository import create_calendar_event, get_calendar_event_for_user, update_calendar_event
from database.database import get_db
from database.models import Utilisateur, Enseignant, Eleve
from utils.school import all_school_classes, sort_school_classes
from utils.teacher_assignments import (
    build_subject_options_for_class,
    parse_teacher_assignments,
    split_choice_token,
    token_to_label,
)


MONTH_NAMES_FR = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
]
WEEKDAY_INITIALS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']


def parse_date_input(raw_value: str) -> date | None:
    """Parse une date utilisateur (ex: 13.01, 13/01, Mardi 13.01, 13.01.2026)."""
    if not raw_value:
        return None

    match = re.search(r'(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?', raw_value)
    if not match:
        return None

    day_value = int(match.group(1))
    month_value = int(match.group(2))
    year_group = match.group(3)

    if year_group:
        year_value = int(year_group)
        if len(year_group) == 2:
            year_value += 2000
    else:
        year_value = date.today().year

    try:
        return date(year_value, month_value, day_value)
    except ValueError:
        return None


def format_date_for_input(value: date) -> str:
    return value.strftime('%d.%m.%Y')


def parse_estimated_time_to_minutes(raw_value: str) -> int | None:
    if not raw_value:
        return None

    normalized = raw_value.strip().lower().replace(',', '.')

    compact_match = re.search(r'(\d+)\s*h\s*(\d{1,2})\b', normalized)
    if compact_match:
        hours_value = int(compact_match.group(1))
        minutes_value = int(compact_match.group(2))
        if minutes_value >= 60:
            return None
        return (hours_value * 60) + minutes_value

    total_minutes = 0
    has_supported_unit = False

    hour_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:heure|heures|h)\b', normalized)
    if hour_matches:
        has_supported_unit = True
        for hour_raw in hour_matches:
            total_minutes += int(round(float(hour_raw) * 60))

    minute_matches = re.findall(r'(\d+)\s*(?:minute|minutes|min)\b', normalized)
    if minute_matches:
        has_supported_unit = True
        for minute_raw in minute_matches:
            total_minutes += int(minute_raw)

    if not has_supported_unit or total_minutes <= 0:
        return None

    return total_minutes


def parse_estimated_time_to_minutes_strict(raw_value: str) -> int | None:
    if not raw_value:
        return None

    normalized = raw_value.strip().lower().replace(',', '.')

    compact_match = re.fullmatch(r'(\d+)\s*h\s*(\d{1,2})\s*(?:min|minute|minutes)?', normalized)
    if compact_match:
        hours_value = int(compact_match.group(1))
        minutes_value = int(compact_match.group(2))
        if minutes_value >= 60:
            return None
        total = (hours_value * 60) + minutes_value
        return total if total > 0 else None

    long_match = re.fullmatch(r'(\d+)\s*(?:heure|heures|h)\s*(\d{1,2})\s*(?:minute|minutes|min)', normalized)
    if long_match:
        hours_value = int(long_match.group(1))
        minutes_value = int(long_match.group(2))
        if minutes_value >= 60:
            return None
        total = (hours_value * 60) + minutes_value
        return total if total > 0 else None

    hours_only_match = re.fullmatch(r'(\d+)\s*(?:heure|heures|h)', normalized)
    if hours_only_match:
        hours_value = int(hours_only_match.group(1))
        total = hours_value * 60
        return total if total > 0 else None

    minutes_only_match = re.fullmatch(r'(\d+)\s*(?:minute|minutes|min)', normalized)
    if minutes_only_match:
        total = int(minutes_only_match.group(1))
        return total if total > 0 else None

    return None


def format_minutes_for_storage(total_minutes: int) -> str:
    hours_value, minutes_value = divmod(total_minutes, 60)
    if hours_value and minutes_value:
        return f'{hours_value} h {minutes_value} min'
    if hours_value:
        return f'{hours_value} h'
    return f'{minutes_value} min'


def _class_level_label(class_name: str) -> str:
    match = re.match(r'^(\d+)', (class_name or '').strip())
    if not match:
        return class_name
    return f'{match.group(1)}ème'


def create_date_picker(label: str, initial_date: date) -> ui.input:
    selected_date = initial_date
    view_year = initial_date.year
    view_month = initial_date.month

    date_input = ui.input(label, value=format_date_for_input(initial_date)).props('outlined readonly').classes('w-full q-mb-md')

    with ui.dialog() as calendar_dialog, ui.card().classes('mini-calendar-card'):
        with ui.row().classes('items-center justify-between w-full q-mb-sm'):
            ui.button(icon='chevron_left', on_click=lambda: change_month(-1)).props('flat round dense')
            month_title = ui.label('').classes('text-subtitle1 text-weight-bold')
            ui.button(icon='chevron_right', on_click=lambda: change_month(1)).props('flat round dense')

        with ui.grid(columns=7).classes('w-full mini-calendar-weekdays'):
            for day_name in WEEKDAY_INITIALS:
                ui.label(day_name).classes('mini-weekday text-center')

        days_grid = ui.grid(columns=7).classes('w-full mini-calendar-days')

        ui.button('Fermer', on_click=calendar_dialog.close).props('flat').classes('self-end q-mt-sm')

    def refresh_title() -> None:
        month_title.text = f'{MONTH_NAMES_FR[view_month - 1]} {view_year}'

    def select_day(chosen_date: date) -> None:
        nonlocal selected_date, view_year, view_month
        selected_date = chosen_date
        view_year = chosen_date.year
        view_month = chosen_date.month
        date_input.value = format_date_for_input(chosen_date)
        render_days()
        calendar_dialog.close()

    def render_days() -> None:
        days_grid.clear()
        refresh_title()

        first_day = date(view_year, view_month, 1)
        first_weekday = first_day.weekday()
        days_in_month = calendar.monthrange(view_year, view_month)[1]

        with days_grid:
            for _ in range(first_weekday):
                ui.element('div').classes('mini-day-cell mini-day-empty')

            for day_number in range(1, days_in_month + 1):
                current_date = date(view_year, view_month, day_number)
                is_selected = current_date == selected_date
                button_classes = 'mini-day-button mini-day-selected' if is_selected else 'mini-day-button'
                ui.button(
                    str(day_number),
                    on_click=lambda d=current_date: select_day(d),
                ).props('flat dense').classes(button_classes)

            total_cells = first_weekday + days_in_month
            trailing_cells = (7 - (total_cells % 7)) % 7
            for _ in range(trailing_cells):
                ui.element('div').classes('mini-day-cell mini-day-empty')

    def change_month(step: int) -> None:
        nonlocal view_year, view_month
        view_month += step
        if view_month == 0:
            view_month = 12
            view_year -= 1
        elif view_month == 13:
            view_month = 1
            view_year += 1
        render_days()

    date_input.on('click', lambda _: calendar_dialog.open())
    render_days()
    return date_input

def create(edit_event_id: int | None = None):
    """Crée la page de formulaire pour ajouter un devoir ou examen"""
    # Aide IA: formulaire enrichi (multi-classes, options OS/OC, sécurité édition élève)
    prefill_date_iso = app.storage.user.get('calendar_prefill_date_iso')
    prefill_date = date.today()
    if prefill_date_iso:
        try:
            prefill_date = date.fromisoformat(prefill_date_iso)
        except ValueError:
            prefill_date = date.today()

    user_identifier = (
        app.storage.user.get('email')
        or str(app.storage.user.get('user_id') or '')
        or 'anonymous'
    )
    class_catalog = all_school_classes()
    class_lookup = {class_name.lower(): class_name for class_name in class_catalog}

    def normalize_class_name(class_name: str) -> str:
        raw_value = (class_name or '').strip()
        if not raw_value:
            return ''
        return class_lookup.get(raw_value.lower(), raw_value)

    edit_event: dict | None = None
    if edit_event_id is not None:
        db_event = get_calendar_event_for_user(edit_event_id, user_identifier)
        if db_event is None:
            ui.notify('Événement introuvable', type='negative')
            ui.navigate.to('/calendrier')
            return

        current_role = str(app.storage.user.get('role') or '').strip().lower()
        if current_role == 'eleve' and db_event.source_event_id is not None:
            ui.notify('Modification non autorisée pour un devoir partagé', type='warning')
            ui.navigate.to('/calendrier')
            return

        try:
            prefill_date = date.fromisoformat(db_event.date_iso)
        except ValueError:
            prefill_date = date.today()

        edit_event = {
            'id': int(db_event.id),
            'type': db_event.event_type,
            'subject': db_event.subject,
            'title': db_event.title or '',
            'description': db_event.description or '',
            'date_iso': db_event.date_iso,
            'estimated_time': db_event.estimated_time,
            'exam_coefficient': db_event.exam_coefficient,
            'exam_duration': db_event.exam_duration or '',
            'target_class': db_event.target_class or '',
        }
    
    ui.add_head_html('''
        <style>
            .formulaire-container {
                background: var(--white);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .formulaire-card {
                background: transparent;
                padding: 0;
                border-radius: 0;
                box-shadow: none;
                width: min(370px, 100%);
                max-width: 100%;
                margin: 0 auto;
                overflow-x: hidden;
            }
            .form-title {
                text-align: center;
                font-size: 28px;
                font-weight: 700;
                color: var(--text-dark);
                margin-bottom: 16px;
            }
            .add-icon-container {
                width: 80px;
                height: 80px;
                background: var(--primary);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
            }
            .mini-calendar-card {
                width: 320px;
                padding: 14px;
                border-radius: 14px;
            }
            .mini-calendar-weekdays {
                gap: 6px;
            }
            .mini-weekday {
                font-weight: 700;
                color: #555;
                width: 100%;
            }
            .mini-calendar-days {
                gap: 6px;
            }
            .mini-day-cell {
                width: 36px;
                height: 36px;
            }
            .mini-day-empty {
                opacity: 0;
            }
            .mini-day-button {
                width: 36px;
                height: 36px;
                min-height: 36px !important;
                border-radius: 8px;
                font-weight: 600;
            }
            .mini-day-selected {
                background: #667eea !important;
                color: white !important;
            }
            .formulaire-card .q-field__native,
            .formulaire-card .q-field__input,
            .formulaire-card .q-field__label {
                white-space: normal !important;
                overflow-wrap: anywhere;
                word-break: break-word;
            }
            .formulaire-card .q-field,
            .formulaire-card .q-select,
            .formulaire-card .q-field__control,
            .formulaire-card .q-field__control-container {
                max-width: 100% !important;
            }
            .formulaire-card .q-field__native,
            .formulaire-card .q-field__native-row,
            .formulaire-card .q-select__selection {
                min-width: 0 !important;
                width: 100% !important;
                flex-wrap: wrap !important;
            }
            .formulaire-card .q-chip {
                max-width: 100% !important;
                white-space: normal !important;
                height: auto !important;
            }
        </style>
    ''')
    
    role = app.storage.user.get('role')
    teacher_assignments_by_class: dict[str, list[str]] = {}
    class_to_students: dict[str, list[dict]] = {}
    student_allowed_subjects: list[str] = []
    student_allowed_subjects_set: set[str] = set()
    if role == 'enseignant':
        user_email = app.storage.user.get('email')
        db = get_db()
        try:
            teacher_user = db.query(Utilisateur).filter(Utilisateur.email == user_email).first()
            if teacher_user is not None:
                teacher_profile = db.query(Enseignant).filter(Enseignant.utilisateur_id == teacher_user.id).first()
                if teacher_profile is not None:
                    raw_assignments_by_class = parse_teacher_assignments(teacher_profile.branches, teacher_profile.classes)
                    for class_name, tokens in raw_assignments_by_class.items():
                        normalized_class_name = normalize_class_name(class_name)
                        if not normalized_class_name:
                            continue
                        teacher_assignments_by_class.setdefault(normalized_class_name, []).extend(tokens)

            all_students = (
                db.query(Eleve, Utilisateur)
                .join(Utilisateur, Utilisateur.id == Eleve.utilisateur_id)
                .all()
            )
            for student, user in all_students:
                normalized_student_class = normalize_class_name(student.classe or '')
                student_item = {
                    'email': user.email,
                    'profile': student,
                }
                class_to_students.setdefault(normalized_student_class, []).append(student_item)
        finally:
            db.close()
    else:
        db = get_db()
        try:
            student_user = db.query(Utilisateur).filter(Utilisateur.email == user_identifier).first()
            if student_user is not None:
                student_profile = db.query(Eleve).filter(Eleve.utilisateur_id == student_user.id).first()
                if student_profile is not None:
                    student_class = (student_profile.classe or '').strip()
                    option_tokens = build_subject_options_for_class(student_class).keys() if student_class else []
                    student_allowed_subjects_set = {
                        subject
                        for token in option_tokens
                        for subject, track in [split_choice_token(token)]
                        if track == 'standard' and subject
                    }
                    student_allowed_subjects = sorted(student_allowed_subjects_set)
        finally:
            db.close()

    teacher_subject_index: dict[str, dict[str, list[str]]] = {}
    # Aide IA: index par branche -> classes/tokens pour piloter les choix enseignants
    for class_name, tokens in teacher_assignments_by_class.items():
        for token in tokens:
            subject_name, _ = split_choice_token(token)
            by_class = teacher_subject_index.setdefault(subject_name, {})
            by_class.setdefault(class_name, []).append(token)

    def _student_has_subject(student_profile: Eleve, subject: str) -> bool:
        normalized_subject = (subject or '').strip()
        if not normalized_subject:
            return False

        if normalized_subject == 'Basic English':
            return bool(student_profile.basic_english)

        available = {
            (student_profile.langue1 or '').strip(),
            (student_profile.langue2 or '').strip(),
            (student_profile.langue3 or '').strip(),
            (student_profile.os or '').strip(),
            (student_profile.oc or '').strip(),
        }
        available = {item for item in available if item}

        if normalized_subject.startswith('OS '):
            return (student_profile.os or '').strip() == normalized_subject.removeprefix('OS ').strip()
        if normalized_subject.startswith('OC '):
            return (student_profile.oc or '').strip() == normalized_subject.removeprefix('OC ').strip()

        if normalized_subject in available:
            return True

        common_subjects = {
            'Mathématiques', 'Français', 'Histoire', 'Géographie',
            'Physique', 'Chimie', 'Biologie', 'Arts visuels', 'Éducation physique', 'Musique',
        }
        return normalized_subject in common_subjects

    def _student_matches_assignment(student_profile: Eleve, subject_token: str) -> bool:
        subject_name, track = split_choice_token(subject_token)
        if track == 'bilingue' and not bool(student_profile.bilingue):
            return False
        return _student_has_subject(student_profile, subject_name)

    with ui.column().classes('formulaire-container'):
        with ui.card().classes('formulaire-card'):
            # Icône d'ajout
            with ui.element('div').classes('add-icon-container'):
                ui.icon('add', size='48px', color='white')
            
            ui.html('<div class="form-title">Nouvel événement</div>', sanitize=False)
            
            # Sélecteur de type (devoir ou examen)
            type_event = ui.toggle(
                ['Devoir', 'Examen'],
                value=('Examen' if (edit_event and edit_event.get('type') == 'examen') else 'Devoir')
            ).classes('w-full q-mb-lg')
            
            # Conteneur pour les champs du formulaire
            form_container = ui.column().classes('w-full')
            
            def update_form():
                """Met à jour le formulaire selon le type sélectionné"""
                form_container.clear()
                
                with form_container:
                    # Champs communs
                    titre = ui.input('Titre', value=(edit_event.get('title', '') if edit_event else '')).props('outlined').classes('w-full q-mb-md')

                    teacher_target_mode = {'value': 'standard'}
                    teacher_class_select = None
                    teacher_option_select = None
                    teacher_option_index: dict[str, tuple[str, str]] = {}
                    if role == 'enseignant':
                        available_subjects = sorted(teacher_subject_index.keys())
                        edit_subject = (edit_event.get('subject', '') if edit_event else '').strip()
                        if edit_subject and edit_subject not in available_subjects:
                            available_subjects.append(edit_subject)
                            available_subjects = sorted(available_subjects)

                        branche = ui.select(
                            available_subjects,
                            label='Branche',
                            value=(edit_subject or (available_subjects[0] if available_subjects else None)),
                        ).props('outlined').classes('w-full q-mb-md')

                        teacher_target_container = ui.column().classes('w-full')

                        def refresh_teacher_target_selector() -> None:
                            # Aide IA: logique d'affichage conditionnelle (branche standard vs OS/OC)
                            nonlocal teacher_class_select, teacher_option_select
                            teacher_class_select = None
                            teacher_option_select = None
                            teacher_option_index.clear()
                            teacher_target_container.clear()

                            selected_subject = (branche.value or '').strip()
                            subject_classes = teacher_subject_index.get(selected_subject, {})
                            is_option_subject = selected_subject.startswith('OS ') or selected_subject.startswith('OC ')
                            teacher_target_mode['value'] = 'option' if is_option_subject else 'standard'

                            with teacher_target_container:
                                if is_option_subject:
                                    option_choices: dict[str, str] = {}
                                    for class_name in sort_school_classes(sorted(subject_classes.keys())):
                                        tokens = sorted(set(subject_classes.get(class_name, [])))
                                        for token in tokens:
                                            option_key = f'{class_name}|||{token}'
                                            teacher_option_index[option_key] = (class_name, token)
                                            option_choices[option_key] = f'{_class_level_label(class_name)} — {token_to_label(token)}'

                                    default_option_values: list[str] = []
                                    if edit_event is not None:
                                        edit_target_class = (edit_event.get('target_class', '') or '').strip()
                                        for key, (class_name, _) in teacher_option_index.items():
                                            if class_name == edit_target_class:
                                                default_option_values = [key]
                                                break
                                    elif option_choices:
                                        default_option_values = [next(iter(option_choices.keys()))]

                                    option_value = (
                                        default_option_values[0]
                                        if edit_event is not None and default_option_values
                                        else default_option_values
                                    )

                                    teacher_option_select = ui.select(
                                        option_choices,
                                        label=('Option concernée' if edit_event else 'Options concernées'),
                                        value=option_value,
                                        multiple=(edit_event is None),
                                    ).props('outlined').classes('w-full q-mb-md')
                                else:
                                    class_choices = sort_school_classes(sorted(subject_classes.keys()))
                                    default_class_values: list[str] = []
                                    if edit_event is not None:
                                        edit_target_class = (edit_event.get('target_class', '') or '').strip()
                                        if edit_target_class and edit_target_class in class_choices:
                                            default_class_values = [edit_target_class]
                                    elif class_choices:
                                        default_class_values = [class_choices[0]]

                                    class_value = (
                                        default_class_values[0]
                                        if edit_event is not None and default_class_values
                                        else default_class_values
                                    )

                                    teacher_class_select = ui.select(
                                        class_choices,
                                        label=('Classe concernée' if edit_event else 'Classes concernées'),
                                        value=class_value,
                                        multiple=(edit_event is None),
                                    ).props('outlined').classes('w-full q-mb-md')

                        branche.on_value_change(lambda _: refresh_teacher_target_selector())
                        refresh_teacher_target_selector()
                    else:
                        edit_subject = (edit_event.get('subject', '') if edit_event else '').strip()
                        student_subject_choices = list(student_allowed_subjects)
                        if edit_subject and edit_subject not in student_subject_choices:
                            student_subject_choices.append(edit_subject)
                            student_subject_choices = sorted(student_subject_choices)

                        branche = ui.select(
                            student_subject_choices,
                            label='Branche',
                            value=(edit_subject or (student_subject_choices[0] if student_subject_choices else None)),
                        ).props('outlined').classes('w-full q-mb-md')
                    
                    description = ui.textarea(
                        'Description',
                        placeholder='Ex: Exercices 1-5, p.42'
                    , value=(edit_event.get('description', '') if edit_event else '')).props('outlined').classes('w-full q-mb-md')
                    
                    if type_event.value == 'Devoir':
                        # Champs spécifiques au devoir
                        date_rendu = create_date_picker('Date de rendu', prefill_date)
                        
                        temps_estime = ui.input(
                            'Temps de révision estimé',
                            placeholder='Ex: 1h30',
                            value=(edit_event.get('estimated_time', '') if edit_event and edit_event.get('type') == 'devoir' else ''),
                        ).props('outlined').classes('w-full q-mb-md')
                        
                    else:
                        # Champs spécifiques à l'examen
                        date_examen = create_date_picker('Date de l\'examen', prefill_date)
                        
                        temps_revision = ui.input(
                            'Temps de révision estimé',
                            placeholder='Ex: 3h',
                            value=(edit_event.get('estimated_time', '') if edit_event and edit_event.get('type') == 'examen' else ''),
                        ).props('outlined').classes('w-full q-mb-md')
                        coefficient_input = None
                        duree_evaluation_input = None
                        if role == 'enseignant':
                            coefficient_input = ui.input(
                                'Coefficient',
                                placeholder='Ex: 2',
                                value=(str(edit_event.get('exam_coefficient')) if edit_event and edit_event.get('type') == 'examen' and edit_event.get('exam_coefficient') is not None else ''),
                            ).props('outlined').classes('w-full q-mb-md')

                            duree_evaluation_input = ui.input(
                                'Durée de l\'évaluation',
                                placeholder='Ex: 45 min, 1h30',
                                value=(edit_event.get('exam_duration', '') if edit_event and edit_event.get('type') == 'examen' else ''),
                            ).props('outlined').classes('w-full q-mb-md')
                    
                    # Bouton d'enregistrement
                    async def handle_submit():
                        # Aide IA: validations + création/propagation multi-classes + métadonnées examen
                        titre_value = (titre.value or '').strip()
                        branche_value = (branche.value or '').strip()
                        description_value = (description.value or '').strip()

                        if type_event.value == 'Devoir':
                            date_value = (date_rendu.value or '').strip()
                            estimation_value = (temps_estime.value or '').strip()
                            coefficient_value = None
                            evaluation_duration_value = None
                        else:
                            date_value = (date_examen.value or '').strip()
                            estimation_value = (temps_revision.value or '').strip()
                            coefficient_raw_value = ((coefficient_input.value if coefficient_input is not None else '') or '').strip()
                            evaluation_duration_raw_value = ((duree_evaluation_input.value if duree_evaluation_input is not None else '') or '').strip()

                            if role == 'enseignant':
                                if not coefficient_raw_value or not evaluation_duration_raw_value:
                                    ui.notify('Merci de renseigner coefficient et durée de l\'évaluation', type='negative')
                                    return

                            try:
                                coefficient_value = float(coefficient_raw_value) if coefficient_raw_value else None
                            except ValueError:
                                ui.notify('Coefficient invalide (ex: 1, 1.5, 2)', type='negative')
                                return

                            if coefficient_value is not None and coefficient_value <= 0:
                                ui.notify('Le coefficient doit être supérieur à 0', type='negative')
                                return

                            parsed_evaluation_duration_minutes = parse_estimated_time_to_minutes_strict(evaluation_duration_raw_value) if evaluation_duration_raw_value else None
                            if evaluation_duration_raw_value and parsed_evaluation_duration_minutes is None:
                                ui.notify('Durée d\'évaluation invalide (ex: 30 min, 1h, 1h30)', type='negative')
                                return
                            evaluation_duration_value = (
                                format_minutes_for_storage(parsed_evaluation_duration_minutes)
                                if parsed_evaluation_duration_minutes is not None
                                else None
                            )

                        if not titre_value or not branche_value or not date_value or not estimation_value:
                            ui.notify('Merci de remplir tous les champs obligatoires', type='negative')
                            return

                        parsed_date = parse_date_input(date_value)
                        if parsed_date is None:
                            ui.notify('Format de date invalide (ex: 13.01 ou 13.01.2026)', type='negative')
                            return

                        parsed_estimation_minutes = parse_estimated_time_to_minutes_strict(estimation_value)
                        if parsed_estimation_minutes is None:
                            ui.notify('Format du temps invalide: utilisez min, h, ou h+min (ex: 30 min, 1h, 1h30, 1 h 30 min)', type='negative')
                            return

                        normalized_estimation = format_minutes_for_storage(parsed_estimation_minutes)

                        event_type = type_event.value.lower()
                        is_edit_mode = edit_event is not None
                        if role == 'enseignant':
                            subject_name = branche_value
                            if subject_name not in teacher_subject_index:
                                ui.notify('Vous ne pouvez pas publier un devoir pour cette branche', type='negative')
                                return
                            subject_classes = teacher_subject_index.get(subject_name, {})
                            assignments_to_publish: list[tuple[str, str]] = []

                            def _as_list(raw_value: object) -> list[str]:
                                if raw_value is None:
                                    return []
                                if isinstance(raw_value, list):
                                    return [str(item) for item in raw_value]
                                if isinstance(raw_value, tuple):
                                    return [str(item) for item in raw_value]
                                return [str(raw_value)]

                            def _prefer_token(tokens: list[str]) -> str | None:
                                ordered_tokens = sorted(set(tokens))
                                for token in ordered_tokens:
                                    _, track = split_choice_token(token)
                                    if track != 'bilingue':
                                        return token
                                return ordered_tokens[0] if ordered_tokens else None

                            if teacher_target_mode['value'] == 'option':
                                selected_option_values = []
                                if teacher_option_select is not None:
                                    selected_option_values = _as_list(teacher_option_select.value)
                                for option_key in selected_option_values:
                                    assignment = teacher_option_index.get(str(option_key))
                                    if assignment is not None:
                                        assignments_to_publish.append(assignment)
                            else:
                                selected_classes = []
                                if teacher_class_select is not None:
                                    selected_classes = _as_list(teacher_class_select.value)
                                for class_name in selected_classes:
                                    selected_token = _prefer_token(subject_classes.get(class_name, []))
                                    if selected_token is not None:
                                        assignments_to_publish.append((class_name, selected_token))

                            if not assignments_to_publish:
                                if teacher_target_mode['value'] == 'option':
                                    ui.notify('Merci de sélectionner au moins une option', type='negative')
                                else:
                                    ui.notify('Merci de sélectionner au moins une classe', type='negative')
                                return

                            assignments_to_publish = list(dict.fromkeys(assignments_to_publish))

                            teacher_identifier = (
                                app.storage.user.get('email')
                                or str(app.storage.user.get('user_id') or '')
                                or 'anonymous'
                            )

                            if is_edit_mode:
                                edit_target_class = assignments_to_publish[0][0]
                                updated = update_calendar_event(
                                    event_id=int(edit_event['id']),
                                    user_identifier=teacher_identifier,
                                    event_type=event_type,
                                    subject=subject_name,
                                    title=titre_value,
                                    description=description_value,
                                    date_iso=parsed_date.isoformat(),
                                    estimated_time=normalized_estimation,
                                    exam_coefficient=coefficient_value,
                                    exam_duration=evaluation_duration_value,
                                    target_class=edit_target_class,
                                    propagate_to_linked=True,
                                )
                                if not updated:
                                    ui.notify('Impossible de modifier cet événement', type='negative')
                                    return
                                ui.notify('Événement modifié avec succès!', type='positive')
                            else:
                                total_students = 0
                                for selected_class_name, selected_token in assignments_to_publish:
                                    teacher_event_id = create_calendar_event(
                                        user_identifier=teacher_identifier,
                                        event_type=event_type,
                                        subject=subject_name,
                                        title=titre_value,
                                        description=description_value,
                                        date_iso=parsed_date.isoformat(),
                                        estimated_time=normalized_estimation,
                                        exam_coefficient=coefficient_value,
                                        exam_duration=evaluation_duration_value,
                                        time_spent='0 minute',
                                        source_event_id=None,
                                        target_class=selected_class_name,
                                    )

                                    students = class_to_students.get(selected_class_name, [])
                                    matching_students = [
                                        student
                                        for student in students
                                        if _student_matches_assignment(student['profile'], selected_token)
                                    ]
                                    if not matching_students:
                                        matching_students = students

                                    for student in matching_students:
                                        total_students += 1
                                        create_calendar_event(
                                            user_identifier=student['email'],
                                            event_type=event_type,
                                            subject=subject_name,
                                            title=titre_value,
                                            description=description_value,
                                            date_iso=parsed_date.isoformat(),
                                            estimated_time=normalized_estimation,
                                            exam_coefficient=coefficient_value,
                                            exam_duration=evaluation_duration_value,
                                            time_spent='0 minute',
                                            source_event_id=teacher_event_id,
                                            target_class=selected_class_name,
                                        )

                                ui.notify(
                                    f'{type_event.value} ajouté pour {len(assignments_to_publish)} classe(s) et {total_students} élève(s)',
                                    type='positive',
                                )
                        else:
                            if branche_value not in student_allowed_subjects_set:
                                ui.notify('Cette branche n\'est pas autorisée pour votre classe', type='negative')
                                return

                            if is_edit_mode:
                                # Aide IA: propager les mises à jour des devoirs à tous les élèves de la classe
                                student_current_class = None
                                db = get_db()
                                try:
                                    student_user = db.query(Utilisateur).filter(Utilisateur.email == user_identifier).first()
                                    if student_user:
                                        student_profile = db.query(Eleve).filter(Eleve.utilisateur_id == student_user.id).first()
                                        if student_profile:
                                            student_current_class = student_profile.classe
                                finally:
                                    db.close()

                                updated = update_calendar_event(
                                    event_id=int(edit_event['id']),
                                    user_identifier=user_identifier,
                                    event_type=event_type,
                                    subject=branche_value,
                                    title=titre_value,
                                    description=description_value,
                                    date_iso=parsed_date.isoformat(),
                                    estimated_time=normalized_estimation,
                                    exam_coefficient=coefficient_value,
                                    exam_duration=evaluation_duration_value,
                                    target_class=student_current_class,
                                    propagate_to_linked=True,
                                )
                                if not updated:
                                    ui.notify('Impossible de modifier cet événement', type='negative')
                                    return
                                ui.notify('Événement modifié avec succès!', type='positive')
                            else:
                                # Aide IA: partage des devoirs d'élèves avec les autres élèves de la même classe
                                # Récupérer la classe actuelle de l'élève
                                student_class = None
                                db = get_db()
                                try:
                                    student_user = db.query(Utilisateur).filter(Utilisateur.email == user_identifier).first()
                                    if student_user:
                                        student_profile = db.query(Eleve).filter(Eleve.utilisateur_id == student_user.id).first()
                                        if student_profile:
                                            student_class = student_profile.classe
                                finally:
                                    db.close()

                                # Créer un événement source pour la classe
                                source_event_id = create_calendar_event(
                                    user_identifier=user_identifier,
                                    event_type=event_type,
                                    subject=branche_value,
                                    title=titre_value,
                                    description=description_value,
                                    date_iso=parsed_date.isoformat(),
                                    estimated_time=normalized_estimation,
                                    exam_coefficient=coefficient_value,
                                    exam_duration=evaluation_duration_value,
                                    time_spent='0 minute',
                                    source_event_id=None,
                                    target_class=student_class,
                                )

                                # Propager aux autres élèves de la même classe
                                if student_class:
                                    db = get_db()
                                    try:
                                        classmates = (
                                            db.query(Eleve, Utilisateur)
                                            .join(Utilisateur, Utilisateur.id == Eleve.utilisateur_id)
                                            .filter(
                                                Eleve.classe == student_class,
                                                Utilisateur.email != user_identifier
                                            )
                                            .all()
                                        )
                                        for classmate_student, classmate_user in classmates:
                                            create_calendar_event(
                                                user_identifier=classmate_user.email,
                                                event_type=event_type,
                                                subject=branche_value,
                                                title=titre_value,
                                                description=description_value,
                                                date_iso=parsed_date.isoformat(),
                                                estimated_time=normalized_estimation,
                                                exam_coefficient=coefficient_value,
                                                exam_duration=evaluation_duration_value,
                                                time_spent='0 minute',
                                                source_event_id=source_event_id,
                                                target_class=student_class,
                                            )
                                    finally:
                                        db.close()

                                ui.notify(f'{type_event.value} ajouté avec succès!', type='positive')
                        ui.navigate.to('/calendrier')
                    
                    ui.button(
                        'MODIFIER' if edit_event else 'ENREGISTRER',
                        icon='check',
                        on_click=handle_submit
                    ).props('color=primary').classes('w-full q-mt-md').style('padding: 12px;')
                    
                    # Bouton annuler
                    ui.button(
                        'ANNULER',
                        icon='close',
                        on_click=lambda: ui.navigate.to('/calendrier')
                    ).props('flat color=negative').classes('w-full q-mt-sm')
            
            # Mise à jour lors du changement de type
            type_event.on_value_change(update_form)
            update_form()
        
        # Navbar en bas
        create_navbar()