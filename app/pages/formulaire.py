#aide de l'IA
from nicegui import ui, app
from components.navbar import create_navbar
import re
from datetime import date
import calendar
from database.calendar_repository import create_calendar_event
from utils.school import all_teaching_subjects


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


def format_minutes_for_storage(total_minutes: int) -> str:
    hours_value, minutes_value = divmod(total_minutes, 60)
    if hours_value and minutes_value:
        return f'{hours_value} h {minutes_value} min'
    if hours_value:
        return f'{hours_value} h'
    return f'{minutes_value} min'


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

def create():
    """Crée la page de formulaire pour ajouter un devoir ou examen"""
    prefill_date_iso = app.storage.user.get('calendar_prefill_date_iso')
    prefill_date = date.today()
    if prefill_date_iso:
        try:
            prefill_date = date.fromisoformat(prefill_date_iso)
        except ValueError:
            prefill_date = date.today()
    
    ui.add_head_html('''
        <style>
            .formulaire-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
            }
            .formulaire-card {
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 600px;
                margin: 0 auto;
            }
            .form-title {
                text-align: center;
                font-size: 28px;
                font-weight: 700;
                color: #333;
                margin-bottom: 30px;
            }
            .add-icon-container {
                width: 80px;
                height: 80px;
                background: #667eea;
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
        </style>
    ''')
    
    teaching_subjects = all_teaching_subjects()

    with ui.column().classes('formulaire-container'):
        with ui.card().classes('formulaire-card'):
            # Icône d'ajout
            with ui.element('div').classes('add-icon-container'):
                ui.icon('add', size='48px', color='white')
            
            ui.html('<div class="form-title">Nouvel événement</div>', sanitize=False)
            
            # Sélecteur de type (devoir ou examen)
            type_event = ui.toggle(
                ['Devoir', 'Examen'],
                value='Devoir'
            ).classes('w-full q-mb-lg')
            
            # Conteneur pour les champs du formulaire
            form_container = ui.column().classes('w-full')
            
            def update_form():
                """Met à jour le formulaire selon le type sélectionné"""
                form_container.clear()
                
                with form_container:
                    # Champs communs
                    titre = ui.input('Titre').props('outlined').classes('w-full q-mb-md')
                    
                    branche = ui.select(
                        teaching_subjects,
                        label='Branche'
                    ).props('outlined').classes('w-full q-mb-md')
                    
                    description = ui.textarea(
                        'Description',
                        placeholder='Ex: Exercices 1-5, p.42'
                    ).props('outlined').classes('w-full q-mb-md')
                    
                    if type_event.value == 'Devoir':
                        # Champs spécifiques au devoir
                        date_rendu = create_date_picker('Date de rendu', prefill_date)
                        
                        temps_estime = ui.input(
                            'Estimation du temps',
                            placeholder='Ex: 1h30'
                        ).props('outlined').classes('w-full q-mb-md')
                        
                    else:
                        # Champs spécifiques à l'examen
                        date_examen = create_date_picker('Date de l\'examen', prefill_date)
                        
                        temps_revision = ui.input(
                            'Temps de révision estimé',
                            placeholder='Ex: 3h'
                        ).props('outlined').classes('w-full q-mb-md')
                    
                    # Bouton d'enregistrement
                    async def handle_submit():
                        titre_value = (titre.value or '').strip()
                        branche_value = (branche.value or '').strip()
                        description_value = (description.value or '').strip()

                        if type_event.value == 'Devoir':
                            date_value = (date_rendu.value or '').strip()
                            estimation_value = (temps_estime.value or '').strip()
                        else:
                            date_value = (date_examen.value or '').strip()
                            estimation_value = (temps_revision.value or '').strip()

                        if not titre_value or not branche_value or not date_value or not estimation_value:
                            ui.notify('Merci de remplir tous les champs obligatoires', type='negative')
                            return

                        parsed_date = parse_date_input(date_value)
                        if parsed_date is None:
                            ui.notify('Format de date invalide (ex: 13.01 ou 13.01.2026)', type='negative')
                            return

                        parsed_estimation_minutes = parse_estimated_time_to_minutes(estimation_value)
                        if parsed_estimation_minutes is None:
                            ui.notify('Format du temps invalide (ex: 1h30, 2 h, 45 min, 1 heure 15 min)', type='negative')
                            return

                        normalized_estimation = format_minutes_for_storage(parsed_estimation_minutes)

                        event_type = type_event.value.lower()
                        user_identifier = (
                            app.storage.user.get('email')
                            or str(app.storage.user.get('user_id') or '')
                            or 'anonymous'
                        )
                        create_calendar_event(
                            user_identifier=user_identifier,
                            event_type=event_type,
                            subject=branche_value,
                            title=titre_value,
                            description=description_value,
                            date_iso=parsed_date.isoformat(),
                            estimated_time=normalized_estimation,
                            time_spent='0 minute',
                        )

                        ui.notify(f'{type_event.value} ajouté avec succès!', type='positive')
                        ui.navigate.to('/calendrier')
                    
                    ui.button(
                        'ENREGISTRER',
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