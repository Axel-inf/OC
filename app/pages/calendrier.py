#aide de l'IA

from nicegui import ui, app
from components.navbar import create_navbar
from datetime import date, timedelta
from html import escape
import re


DAY_NAMES_FR = {
    0: 'Lundi',
    1: 'Mardi',
    2: 'Mercredi',
    3: 'Jeudi',
    4: 'Vendredi',
    5: 'Samedi',
    6: 'Dimanche',
}


def _format_day_header(current_date: date) -> str:
    return f"{DAY_NAMES_FR[current_date.weekday()]} {current_date.strftime('%d.%m')}"


def _parse_date_from_text(raw_value: str) -> date | None:
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


def _build_default_events() -> list[dict]:
    current_year = date.today().year
    return [
        {
            'type': 'devoir',
            'subject': 'Mathématiques',
            'title': '',
            'description': 'Exercice 1.20',
            'estimated_time': '30 minutes',
            'time_spent': '1 heure',
            'date_obj': date(current_year, 1, 13),
        },
        {
            'type': 'devoir',
            'subject': 'Français',
            'title': '',
            'description': 'Lecture de Théodat',
            'estimated_time': '7 heures',
            'time_spent': '10 heures',
            'date_obj': date(current_year, 1, 13),
        },
        {
            'type': 'examen',
            'subject': 'Physique',
            'title': '',
            'description': 'Magnétisme',
            'estimated_time': '2 heures',
            'time_spent': '8 heures',
            'date_obj': date(current_year, 1, 13),
        },
        {
            'type': 'devoir',
            'subject': 'Chimie',
            'title': '',
            'description': 'Exercice chapitre 5',
            'estimated_time': '1 heure',
            'time_spent': '1h30',
            'date_obj': date(current_year, 1, 15),
        },
        {
            'type': 'examen',
            'subject': 'Anglais',
            'title': '',
            'description': 'Grammaire et vocabulaire',
            'estimated_time': '1 heure',
            'time_spent': '30 minutes',
            'date_obj': date(current_year, 1, 15),
        },
    ]


def _build_custom_events() -> list[dict]:
    custom_events = app.storage.user.get('calendar_events', [])
    normalized_events: list[dict] = []

    for event in custom_events:
        date_obj = None
        date_iso = event.get('date_iso')
        if date_iso:
            try:
                date_obj = date.fromisoformat(date_iso)
            except ValueError:
                date_obj = None

        if date_obj is None:
            date_obj = _parse_date_from_text(event.get('date', ''))

        if date_obj is None:
            continue

        normalized_events.append({
            'type': event.get('type', 'devoir'),
            'subject': event.get('subject', 'Branche non définie'),
            'title': event.get('title', ''),
            'description': event.get('description', ''),
            'estimated_time': event.get('estimated_time', 'Non renseigné'),
            'time_spent': event.get('time_spent', '0 minute'),
            'date_obj': date_obj,
        })

    return normalized_events

def create():
    """Crée la page calendrier"""
    events = _build_default_events() + _build_custom_events()
    events_by_date: dict[date, list[dict]] = {}
    for event in events:
        event_date = event['date_obj']
        events_by_date.setdefault(event_date, []).append(event)

    start_date = date.today()
    visible_days = 5
    past_days_pool = 30
    all_days = [
        start_date - timedelta(days=offset)
        for offset in range(past_days_pool, 0, -1)
    ] + [
        start_date + timedelta(days=offset)
        for offset in range(visible_days)
    ]

    def open_form_for_day(target_date: date) -> None:
        app.storage.user['calendar_prefill_date_iso'] = target_date.isoformat()
        ui.navigate.to('/formulaire')

    def open_form_without_prefill() -> None:
        app.storage.user.pop('calendar_prefill_date_iso', None)
        ui.navigate.to('/formulaire')
    
    ui.add_head_html('<link rel="stylesheet" href="/static/css/custom.css">')
    ui.add_head_html('''
        <script>
            window.markCalendarDone = function(id, checkbox) {
                const card = document.getElementById(id);
                if (!card) return;
                card.classList.toggle('is-completed', checkbox.checked);
            }

            window.deleteCalendarItem = function(id) {
                const card = document.getElementById(id);
                if (!card) return;

                const dayContent = card.closest('.day-content-container');
                if (!dayContent) {
                    card.remove();
                    return;
                }

                const previous = card.previousElementSibling;
                const next = card.nextElementSibling;

                if (previous && previous.classList.contains('separator')) {
                    previous.remove();
                } else if (next && next.classList.contains('separator')) {
                    next.remove();
                }

                card.remove();

                const remainingCards = dayContent.querySelectorAll('.calendar-task-card').length;
                if (remainingCards <= 0) {
                    dayContent.classList.add('empty', 'tertiary');
                    dayContent.innerHTML = 'Aucun devoir ou examen ce jour-ci';
                    return;
                }

                const totalElement = dayContent.querySelector('.total-time-container');
                if (totalElement) {
                    totalElement.textContent = `Nombre d'éléments : ${remainingCards}`;
                }

                dayContent.querySelectorAll('.separator').forEach((separator) => separator.remove());
            }

            window.showPastDays = function() {
                const hiddenDays = Array.from(document.querySelectorAll('.past-day-hidden'));
                hiddenDays.slice(-5).forEach((dayElement) => {
                    dayElement.classList.remove('past-day-hidden');
                });

                const remainingHidden = document.querySelectorAll('.past-day-hidden').length;
                const button = document.getElementById('past-days-btn');
                if (button && remainingHidden === 0) {
                    button.style.display = 'none';
                }
            }

        </script>
    ''')
    
    with ui.column().classes('page-container'):
        ui.html('<div class="titre-container">Calendrier</div>', sanitize=False)
        ui.html('<div class="charge-travail-container">Charge de travail</div>', sanitize=False)
        ui.button(
            'Tâches passées',
            on_click=lambda: ui.run_javascript('showPastDays()')
        ).props('id=past-days-btn').classes('past-tasks-button-container')

        with ui.column().classes('days-list-container'):
            for day_index, current_date in enumerate(all_days):
                day_events = events_by_date.get(current_date, [])
                day_header = _format_day_header(current_date)
                if current_date == start_date:
                    day_header = f"{day_header} (Aujourd'hui)"

                day_container_classes = 'day-container'
                if day_index < past_days_pool:
                    day_container_classes += ' past-day-hidden'

                with ui.column().classes(day_container_classes):
                    with ui.row().classes('day-header-container day-header-row no-wrap'):
                        ui.label(day_header).classes('day-header-text')
                        ui.button(
                            icon='add',
                            on_click=lambda event, selected_date=current_date: open_form_for_day(selected_date),
                        ).props('flat round dense').classes('day-add-button')

                    if not day_events:
                        with ui.column().classes('day-content-container empty tertiary'):
                            ui.html('Aucun devoir ou examen ce jour-ci', sanitize=False)
                    else:
                        with ui.column().classes('day-content-container'):
                            ui.html(
                                f'<div class="total-time-container">Nombre d\'éléments : {len(day_events)}</div>',
                                sanitize=False,
                            )

                            sorted_day_events = sorted(
                                day_events,
                                key=lambda item: 0 if item.get('type') == 'devoir' else 1,
                            )

                            with ui.column().classes('homework-list-container'):
                                for index, event in enumerate(sorted_day_events):
                                    item_id = f"task-{current_date.strftime('%Y%m%d')}-{index}"
                                    event_type = event.get('type', 'devoir')
                                    card_class = (
                                        'exam-card-container'
                                        if event_type == 'examen'
                                        else 'homework-card-container'
                                    )

                                    subject = escape(event.get('subject', 'Branche non définie'))
                                    title = escape(event.get('title', ''))
                                    details = escape(event.get('description', ''))
                                    if title and details:
                                        full_description = f'{title} — {details}'
                                    elif title:
                                        full_description = title
                                    else:
                                        full_description = details

                                    estimated_time = escape(event.get('estimated_time', 'Non renseigné'))
                                    time_spent = escape(event.get('time_spent', '0 minute'))
                                    time_label = (
                                        'Temps de révision estimé'
                                        if event_type == 'examen'
                                        else 'Temps estimé'
                                    )

                                    ui.html(
                                        f'''
                                            <div id="{item_id}" class="{card_class} calendar-task-card">
                                                <div class="task-card-layout">
                                                    <div class="task-actions-left">
                                                        <input type="checkbox" class="task-check" onchange="markCalendarDone('{item_id}', this)">
                                                        <button type="button" class="task-delete-button" onclick="deleteCalendarItem('{item_id}')" aria-label="Supprimer"><span class="task-delete-icon material-icons">delete</span></button>
                                                    </div>
                                                    <div class="task-content">
                                                        <div class="subject">{subject}</div>
                                                        <div class="description">{full_description}</div>
                                                        <div class="time-info">{time_label} : {estimated_time}</div>
                                                        <div class="time-info time-spent-row">Temps passé :
                                                            <input type="text" class="time-spent-input" value="À compléter" aria-label="Temps passé">
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ''',
                                        sanitize=False,
                                    )

                                    if index < len(sorted_day_events) - 1:
                                        ui.html('<div class="separator"></div>', sanitize=False)

        ui.button(
            '+ Ajouter un événement',
            on_click=open_form_without_prefill
        ).classes('add-button-container')

        create_navbar()