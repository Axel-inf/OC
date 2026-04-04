#aide de l'IA

from nicegui import ui, app
from components.navbar import create_navbar
from datetime import date, timedelta
from html import escape
from pathlib import Path
import re
from database.calendar_repository import (
    average_student_time_spent_for_event,
    create_calendar_event,
    list_calendar_events_for_user,
    seed_default_calendar_events_for_user,
    sync_student_calendar_for_class_change,
)
from database.database import get_db
from database.models import Eleve, Enseignant, Utilisateur
from utils.teacher_assignments import split_choice_token


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


def _format_target_scope_label(subject: str, target_class: str) -> str:
    raw_subject = (subject or '').strip()
    raw_class = (target_class or '').strip()

    if not raw_class:
        return 'Classe non définie'

    class_level_match = re.match(r'^(\d+)', raw_class)
    if class_level_match and (raw_subject.startswith('OC ') or raw_subject.startswith('OS ')):
        return f"{class_level_match.group(1)}ème {raw_subject}"

    return raw_class


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


def _duration_to_minutes(raw_value: str) -> int:
    if not raw_value:
        return 0

    normalized = raw_value.strip().lower().replace(',', '.')

    compact_match = re.search(r'(\d+)\s*h\s*(\d{1,2})', normalized)
    if compact_match:
        hours_value = int(compact_match.group(1))
        minutes_value = int(compact_match.group(2))
        return (hours_value * 60) + minutes_value

    total_minutes = 0

    hour_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:heure|heures|h)\b', normalized)
    for hour_raw in hour_matches:
        total_minutes += int(round(float(hour_raw) * 60))

    minute_matches = re.findall(r'(\d+)\s*(?:minute|minutes|min)\b', normalized)
    for minute_raw in minute_matches:
        total_minutes += int(minute_raw)

    if total_minutes > 0:
        return total_minutes

    if normalized.isdigit():
        return int(normalized)

    return 0


def _format_duration(total_minutes: int) -> str:
    if total_minutes <= 0:
        return '0 min'

    hours_value, minutes_value = divmod(total_minutes, 60)
    if hours_value and minutes_value:
        return f'{hours_value} h {minutes_value} min'
    if hours_value:
        return f'{hours_value} h'
    return f'{minutes_value} min'


def _format_percentage(value: float) -> str:
    rounded_value = int(round(value))
    return f'{rounded_value}%'


def _build_workload_display(total_minutes: int, target_minutes: int) -> tuple[float, str, str]:
    if target_minutes <= 0:
        return 0.0, '0%', 'workload-low'

    ratio = (total_minutes / target_minutes) * 100

    if ratio >= 100:
        label = 'Surchargé' if total_minutes > target_minutes else '100%'
        return 100.0, label, 'workload-critical'

    if ratio < 50:
        return ratio, _format_percentage(ratio), 'workload-low'

    return ratio, _format_percentage(ratio), 'workload-high'


def _get_user_identifier() -> str:
    return (
        app.storage.user.get('email')
        or str(app.storage.user.get('user_id') or '')
        or 'anonymous'
    )


def _load_events_from_database(user_identifier: str) -> list[dict]:
    # Aide IA: normalisation des événements avec champs supplémentaires (classe, examen, lien source)
    db_events = list_calendar_events_for_user(user_identifier)
    normalized_events: list[dict] = []

    for event in db_events:
        try:
            date_obj = date.fromisoformat(event.date_iso)
        except ValueError:
            continue

        normalized_events.append({
            'id': int(event.id),
            'type': event.event_type,
            'subject': event.subject,
            'title': event.title or '',
            'description': event.description or '',
            'estimated_time': event.estimated_time,
            'exam_coefficient': event.exam_coefficient,
            'exam_duration': event.exam_duration or '',
            'time_spent': event.time_spent or '0 minute',
            'is_done': bool(event.is_done),
            'source_event_id': event.source_event_id,
            'target_class': event.target_class or '',
            'date_obj': date_obj,
        })

    return normalized_events


def _migrate_legacy_storage_events(user_identifier: str) -> None:
    legacy_events = app.storage.user.get('calendar_events', [])
    if not legacy_events:
        return

    for event in legacy_events:
        parsed_date = None
        date_iso = event.get('date_iso')
        if date_iso:
            try:
                parsed_date = date.fromisoformat(date_iso)
            except ValueError:
                parsed_date = None

        if parsed_date is None:
            parsed_date = _parse_date_from_text(event.get('date', ''))

        if parsed_date is None:
            continue

        create_calendar_event(
            user_identifier=user_identifier,
            event_type=event.get('type', 'devoir'),
            subject=event.get('subject', 'Branche non définie'),
            title=event.get('title', ''),
            description=event.get('description', ''),
            date_iso=parsed_date.isoformat(),
            estimated_time=event.get('estimated_time', 'Non renseigné'),
            time_spent=event.get('time_spent', '0 minute'),
        )

    app.storage.user['calendar_events'] = []

def create():
    """Crée la page calendrier"""
    user_identifier = _get_user_identifier()
    user_role = str(app.storage.user.get('role') or '').strip().lower()
    is_teacher = user_role == 'enseignant'

    # Aide IA: synchroniser les devoirs de classe avant affichage du calendrier élève
    if user_role == 'eleve':
        db = get_db()
        try:
            user = db.query(Utilisateur).filter(Utilisateur.email == user_identifier).first()
            if user is not None:
                eleve = db.query(Eleve).filter(Eleve.utilisateur_id == user.id).first()
                if eleve is not None:
                    sync_student_calendar_for_class_change(
                        user_identifier=user_identifier,
                        new_class=(eleve.classe or ''),
                        langue1=(eleve.langue1 or ''),
                        langue2=(eleve.langue2 or ''),
                        langue3=(eleve.langue3 or ''),
                        os_value=(eleve.os or ''),
                        oc_value=(eleve.oc or ''),
                        basic_english=bool(eleve.basic_english),
                    )
        finally:
            db.close()
    
    # Load teacher's subjects if teacher
    teacher_subjects: set[str] = set()
    if is_teacher:
        db = get_db()
        try:
            user = db.query(Utilisateur).filter(Utilisateur.email == user_identifier).first()
            if user:
                enseignant = db.query(Enseignant).filter(Enseignant.utilisateur_id == user.id).first()
                if enseignant and enseignant.branches:
                    # Parse branches to extract subject names
                    for token in enseignant.branches.split(','):
                        token = token.strip()
                        if '||' in token:
                            subject, _ = split_choice_token(token)
                            teacher_subjects.add(subject.lower())
                        else:
                            # Handle legacy format or simple subject names
                            teacher_subjects.add(token.lower())
        finally:
            db.close()
    
    _migrate_legacy_storage_events(user_identifier)
    seed_default_calendar_events_for_user(user_identifier)
    events = _load_events_from_database(user_identifier)
    events_by_date: dict[date, list[dict]] = {}
    for event in events:
        event_date = event['date_obj']
        events_by_date.setdefault(event_date, []).append(event)

    workload_window_days = 7
    workload_target_minutes = 18 * 60
    workload_total_minutes = 0
    for offset in range(workload_window_days):
        current_day = date.today() + timedelta(days=offset)
        day_events = events_by_date.get(current_day, [])
        workload_total_minutes += sum(
            _duration_to_minutes(event.get('estimated_time', ''))
            for event in day_events
        )

    workload_percentage, workload_label, workload_state_class = _build_workload_display(
        workload_total_minutes,
        workload_target_minutes,
    )

    start_date = date.today()
    visible_days = 5
    past_days_pool = 30
    future_event_dates = [event['date_obj'] for event in events if event['date_obj'] >= start_date]
    furthest_future_date = max(future_event_dates, default=(start_date + timedelta(days=visible_days - 1)))
    future_days_span = max(visible_days, (furthest_future_date - start_date).days + 1)
    all_days = [
        start_date - timedelta(days=offset)
        for offset in range(past_days_pool, 0, -1)
    ] + [
        start_date + timedelta(days=offset)
        for offset in range(future_days_span)
    ]

    def open_form_for_day(target_date: date) -> None:
        app.storage.user['calendar_prefill_date_iso'] = target_date.isoformat()
        ui.navigate.to('/formulaire')

    def open_form_without_prefill() -> None:
        app.storage.user.pop('calendar_prefill_date_iso', None)
        ui.navigate.to('/formulaire')
    
    css_path = Path(__file__).resolve().parents[1] / 'static' / 'css' / 'custom.css'
    css_version = int(css_path.stat().st_mtime) if css_path.exists() else 0
    ui.add_head_html(f'<link rel="stylesheet" href="/static/css/custom.css?v={css_version}">')
    ui.add_head_html('''
        <script>
            window.updateWorkloadBar = function(deltaMinutes) {
                const targetMinutes = parseInt(document.body.dataset.workloadTargetMinutes || '0', 10);
                const currentTotal = parseInt(document.body.dataset.workloadTotalMinutes || '0', 10);
                const nextTotal = Math.max(0, currentTotal + deltaMinutes);

                document.body.dataset.workloadTotalMinutes = String(nextTotal);

                const fill = document.getElementById('workload-fill');
                const text = document.getElementById('workload-text');
                const container = document.getElementById('workload-container');
                if (!fill || !text || !container) {
                    return;
                }

                container.classList.remove('workload-low', 'workload-high', 'workload-critical');

                if (targetMinutes <= 0) {
                    fill.style.width = '0%';
                    text.textContent = '0%';
                    container.classList.add('workload-low');
                    return;
                }

                if (nextTotal >= targetMinutes) {
                    fill.style.width = '100%';
                    text.textContent = nextTotal > targetMinutes ? 'Surchargé' : '100%';
                    container.classList.add('workload-critical');
                    return;
                }

                const ratio = (nextTotal / targetMinutes) * 100;
                fill.style.width = `${ratio}%`;
                text.textContent = `${Math.round(ratio)}%`;
                if (ratio < 50) {
                    container.classList.add('workload-low');
                } else {
                    container.classList.add('workload-high');
                }
            }

            window.markCalendarDone = async function(id, eventId, checkbox) {
                const card = document.getElementById(id);
                if (!card) return;
                card.classList.toggle('is-completed', checkbox.checked);

                try {
                    const response = await fetch('/api/calendar-events/done', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            event_id: eventId,
                            is_done: !!checkbox.checked,
                        }),
                    });
                    if (!response.ok) {
                        checkbox.checked = !checkbox.checked;
                        card.classList.toggle('is-completed', checkbox.checked);
                    }
                } catch (error) {
                    checkbox.checked = !checkbox.checked;
                    card.classList.toggle('is-completed', checkbox.checked);
                    console.error('Erreur de sauvegarde de la coche', error);
                }
            }

            window.clearTimeSpentInput = function(inputElement) {
                inputElement.dataset.lastSavedValue = inputElement.value || 'À compléter';
                if (inputElement.value === 'À compléter') {
                    inputElement.value = '';
                }
            }

            window.normalizeTimeSpentInput = function(rawValue) {
                const normalized = (rawValue || '').trim().toLowerCase().replace(',', '.');
                if (!normalized || normalized === 'a completer' || normalized === 'à compléter') {
                    return '0 minute';
                }

                const compact = normalized.match(/^(\d+)\s*h\s*(\d{1,2})\s*(?:min|minute|minutes)?$/);
                if (compact) {
                    const hours = parseInt(compact[1], 10);
                    const minutes = parseInt(compact[2], 10);
                    if (minutes >= 60) return null;
                    const total = (hours * 60) + minutes;
                    if (total <= 0) return null;
                    const h = Math.floor(total / 60);
                    const m = total % 60;
                    if (h && m) return `${h} h ${m} min`;
                    if (h) return `${h} h`;
                    return `${m} min`;
                }

                const long = normalized.match(/^(\d+)\s*(?:heure|heures|h)\s*(\d{1,2})\s*(?:minute|minutes|min)$/);
                if (long) {
                    const hours = parseInt(long[1], 10);
                    const minutes = parseInt(long[2], 10);
                    if (minutes >= 60) return null;
                    const total = (hours * 60) + minutes;
                    if (total <= 0) return null;
                    const h = Math.floor(total / 60);
                    const m = total % 60;
                    if (h && m) return `${h} h ${m} min`;
                    if (h) return `${h} h`;
                    return `${m} min`;
                }

                const hoursOnly = normalized.match(/^(\d+)\s*(?:heure|heures|h)$/);
                if (hoursOnly) {
                    const total = parseInt(hoursOnly[1], 10) * 60;
                    return total > 0 ? `${Math.floor(total / 60)} h` : null;
                }

                const minutesOnly = normalized.match(/^(\d+)\s*(?:minute|minutes|min)$/);
                if (minutesOnly) {
                    const total = parseInt(minutesOnly[1], 10);
                    return total > 0 ? `${total} min` : null;
                }

                return null;
            }

            window.updateCalendarTimeSpent = async function(eventId, inputElement) {
                // Aide IA: appel API sans identifiant utilisateur côté client
                const enteredValue = (inputElement.value || '').trim();
                const valueToSave = window.normalizeTimeSpentInput(enteredValue);
                if (valueToSave === null) {
                    inputElement.value = inputElement.dataset.lastSavedValue || 'À compléter';
                    alert('Format invalide: utilisez uniquement min, h, ou h+min (ex: 30 min, 1 h, 1 h 30 min).');
                    return;
                }

                try {
                    const response = await fetch('/api/calendar-events/time-spent', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            event_id: eventId,
                            time_spent: valueToSave,
                        }),
                    });

                    if (!response.ok) {
                        inputElement.value = inputElement.dataset.lastSavedValue || 'À compléter';
                        return;
                    }

                    if (valueToSave === '0 minute') {
                        inputElement.value = 'À compléter';
                        inputElement.dataset.lastSavedValue = 'À compléter';
                    } else {
                        inputElement.value = valueToSave;
                        inputElement.dataset.lastSavedValue = valueToSave;
                    }
                } catch (error) {
                    inputElement.value = inputElement.dataset.lastSavedValue || 'À compléter';
                    console.error('Erreur de sauvegarde du temps passé', error);
                }
            }

            window.deleteCalendarItem = async function(id, eventId) {
                // Aide IA: suppression pilotée serveur avec contrôle d'autorisation
                const card = document.getElementById(id);
                if (!card) return;

                const removedMinutes = parseInt(card.dataset.estimatedMinutes || '0', 10);
                const inWorkloadWindow = card.dataset.workloadWindow === '1';

                try {
                    const response = await fetch('/api/calendar-events/delete', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            event_id: eventId,
                        }),
                    });

                    if (!response.ok) {
                        return;
                    }
                } catch (error) {
                    console.error('Erreur de suppression calendrier', error);
                    return;
                }

                const dayContent = card.closest('.day-content-container');
                if (!dayContent) {
                    card.remove();
                    if (inWorkloadWindow) {
                        const removedSafe = Number.isNaN(removedMinutes) ? 0 : removedMinutes;
                        window.updateWorkloadBar(-removedSafe);
                    }
                    return;
                }

                card.remove();

                if (inWorkloadWindow) {
                    const removedSafe = Number.isNaN(removedMinutes) ? 0 : removedMinutes;
                    window.updateWorkloadBar(-removedSafe);
                }

                const remainingCards = Array.from(dayContent.querySelectorAll('.calendar-task-card'));
                if (remainingCards.length <= 0) {
                    dayContent.classList.add('empty', 'tertiary');
                    dayContent.innerHTML = 'Aucun devoir ou examen ce jour-ci';
                    return;
                }

                const totalElement = dayContent.querySelector('.total-time-container');
                if (totalElement) {
                    const totalMinutes = remainingCards.reduce((sum, currentCard) => {
                        const minutesValue = parseInt(currentCard.dataset.estimatedMinutes || '0', 10);
                        return sum + (Number.isNaN(minutesValue) ? 0 : minutesValue);
                    }, 0);

                    const hoursValue = Math.floor(totalMinutes / 60);
                    const minutesValue = totalMinutes % 60;
                    let formattedDuration = '0 min';

                    if (hoursValue > 0 && minutesValue > 0) {
                        formattedDuration = `${hoursValue} h ${minutesValue} min`;
                    } else if (hoursValue > 0) {
                        formattedDuration = `${hoursValue} h`;
                    } else {
                        formattedDuration = `${minutesValue} min`;
                    }

                    totalElement.textContent = `Temps de travail : ${formattedDuration}`;
                }
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
    ui.run_javascript(f'document.body.dataset.calendarUserIdentifier = {user_identifier!r};')
    ui.run_javascript(f'document.body.dataset.workloadTargetMinutes = {workload_target_minutes};')
    ui.run_javascript(f'document.body.dataset.workloadTotalMinutes = {workload_total_minutes};')
    
    with ui.column().classes('page-container'):
        ui.html('<div class="titre-container">Calendrier</div>', sanitize=False)

        ui.html('<div class="charge-travail-label">Charge de travail pour les 7 prochains jours</div>', sanitize=False)
        ui.html(
            f'''<div id="workload-container" class="charge-travail-container {workload_state_class}">
                    <div id="workload-fill" class="charge-travail-fill" style="width: {workload_percentage:.2f}%;"></div>
                    <div id="workload-text" class="charge-travail-text">{workload_label}</div>
                </div>''',
            sanitize=False,
        )
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
                        day_total_minutes = sum(
                            _duration_to_minutes(event.get('estimated_time', ''))
                            for event in day_events
                        )
                        with ui.column().classes('day-content-container'):
                            ui.html(
                                f'<div class="total-time-container">Temps de travail : {_format_duration(day_total_minutes)}</div>',
                                sanitize=False,
                            )

                            sorted_day_events = sorted(
                                day_events,
                                key=lambda item: 0 if item.get('type') == 'devoir' else 1,
                            )

                            with ui.column().classes('homework-list-container'):
                                average_cache: dict[tuple[str, str, str, str, str, str, str], str] = {}
                                for index, event in enumerate(sorted_day_events):
                                    item_id = f"task-{current_date.strftime('%Y%m%d')}-{index}"
                                    event_type = event.get('type', 'devoir')
                                    card_class = (
                                        'exam-card-container'
                                        if event_type == 'examen'
                                        else 'homework-card-container'
                                    )
                                    if bool(event.get('is_done')):
                                        card_class += ' is-completed'
                                    event_type_label = 'Examen' if event_type == 'examen' else 'Devoir'
                                    estimated_minutes = _duration_to_minutes(event.get('estimated_time', ''))

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
                                    time_label = 'Temps de révision estimé'
                                    in_workload_window = 1 if start_date <= current_date <= (start_date + timedelta(days=workload_window_days - 1)) else 0
                                    class_info_html = ''
                                    branch_info_html = ''
                                    exam_info_html = ''

                                    if is_teacher:
                                        # Aide IA: affichage prof (classe, branche, moyenne élève, méta examen)
                                        average_key = (
                                            event.get('type', ''),
                                            event.get('subject', ''),
                                            event.get('title', ''),
                                            event.get('description', ''),
                                            event.get('date_obj', current_date).isoformat(),
                                            event.get('estimated_time', ''),
                                            event.get('target_class', ''),
                                        )
                                        if average_key not in average_cache:
                                            average_minutes, _ = average_student_time_spent_for_event(
                                                event_type=average_key[0],
                                                subject=average_key[1],
                                                title=average_key[2],
                                                description=average_key[3],
                                                date_iso=average_key[4],
                                                estimated_time=average_key[5],
                                                target_class=average_key[6],
                                            )
                                            average_cache[average_key] = (
                                                _format_duration(average_minutes)
                                                if average_minutes is not None
                                                else ''
                                            )

                                        target_scope_label = _format_target_scope_label(
                                            event.get('subject', ''),
                                            event.get('target_class', ''),
                                        )
                                        class_info_html = f'<div class="time-info">Classe concernée : {escape(target_scope_label)}</div>'
                                        branch_info_html = f'<div class="time-info">Branche : {subject}</div>'
                                        if event_type == 'examen':
                                            exam_coeff = event.get('exam_coefficient')
                                            exam_duration = escape((event.get('exam_duration', '') or '').strip())
                                            exam_meta_parts: list[str] = []
                                            if exam_coeff is not None:
                                                exam_meta_parts.append(f'Coefficient {exam_coeff:g}')
                                            if exam_duration:
                                                exam_meta_parts.append(f'Durée {exam_duration}')
                                            if exam_meta_parts:
                                                exam_info_html = f'<div class="time-info">{" • ".join(exam_meta_parts)}</div>'
                                        time_spent_row_html = f'<div class="time-info time-spent-row">Temps moyen par élève : {escape(average_cache[average_key])}</div>'
                                        # Only show management actions if teacher teaches this subject
                                        event_subject_lower = event.get('subject', '').lower()
                                        can_delete = event_subject_lower in teacher_subjects
                                        if can_delete:
                                            left_actions_html = (
                                                f'<button type="button" class="task-delete-button" onclick="window.location.href=\'/formulaire/modifier/{event["id"]}\'" aria-label="Modifier"><span class="task-delete-icon material-icons">edit</span></button>'
                                                f'<button type="button" class="task-delete-button" onclick="deleteCalendarItem(\'{item_id}\', {event["id"]})" aria-label="Supprimer"><span class="task-delete-icon material-icons">delete</span></button>'
                                            )
                                        else:
                                            left_actions_html = ''
                                    else:
                                        # Aide IA: protections UI élève pour devoirs partagés (pas de suppression/modification)
                                        is_shared_event = event.get('source_event_id') is not None
                                        if event_type == 'examen':
                                            exam_coeff = event.get('exam_coefficient')
                                            exam_duration = escape((event.get('exam_duration', '') or '').strip())
                                            exam_meta_parts: list[str] = []
                                            if exam_coeff is not None:
                                                exam_meta_parts.append(f'Coefficient {exam_coeff:g}')
                                            if exam_duration:
                                                exam_meta_parts.append(f'Durée {exam_duration}')
                                            if exam_meta_parts:
                                                exam_info_html = f'<div class="time-info">{" • ".join(exam_meta_parts)}</div>'
                                        time_spent_row_html = (
                                            f'<div class="time-info time-spent-row">Temps passé : '
                                            f'<input type="text" class="time-spent-input" value="{time_spent if time_spent != "0 minute" else "À compléter"}" aria-label="Temps passé" onfocus="clearTimeSpentInput(this)" onblur="updateCalendarTimeSpent({event["id"]}, this)"></div>'
                                        )
                                        if is_shared_event:
                                            checkbox_checked_attr = ' checked' if bool(event.get('is_done')) else ''
                                            left_actions_html = (
                                                f'<input type="checkbox" class="task-check"{checkbox_checked_attr} onchange="markCalendarDone(\'{item_id}\', {event["id"]}, this)">' 
                                            )
                                        else:
                                            checkbox_checked_attr = ' checked' if bool(event.get('is_done')) else ''
                                            left_actions_html = (
                                                f'<input type="checkbox" class="task-check"{checkbox_checked_attr} onchange="markCalendarDone(\'{item_id}\', {event["id"]}, this)">' 
                                                f'<button type="button" class="task-delete-button" onclick="window.location.href=\'/formulaire/modifier/{event["id"]}\'" aria-label="Modifier"><span class="task-delete-icon material-icons">edit</span></button>'
                                                f'<button type="button" class="task-delete-button" onclick="deleteCalendarItem(\'{item_id}\', {event["id"]})" aria-label="Supprimer"><span class="task-delete-icon material-icons">delete</span></button>'
                                            )

                                    ui.html(
                                        f'''
                                            <div id="{item_id}" class="{card_class} calendar-task-card" data-estimated-minutes="{estimated_minutes}" data-workload-window="{in_workload_window}">
                                                <div class="task-card-layout">
                                                    <div class="task-actions-left">
                                                        {left_actions_html}
                                                    </div>
                                                    <div class="task-content">
                                                        <div class="task-type-label">{event_type_label}</div>
                                                        <div class="subject">{subject}</div>
                                                        <div class="description">{full_description}</div>
                                                        {class_info_html}
                                                        {branch_info_html}
                                                        {exam_info_html}
                                                        <div class="time-info">{time_label} : {estimated_time}</div>
                                                        {time_spent_row_html}
                                                    </div>
                                                </div>
                                            </div>
                                        ''',
                                        sanitize=False,
                                    )

        ui.button(
            '+ Ajouter un événement',
            on_click=open_form_without_prefill
        ).classes('add-button-container')

        create_navbar()