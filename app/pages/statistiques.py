#aide de l'IA
from datetime import date
from pathlib import Path
import re
from nicegui import ui, app
from components.navbar import create_navbar
from pages.formulaire import create_date_picker, parse_date_input
from database.calendar_repository import (
    list_calendar_events_for_user,
    list_calendar_events_in_range,
)
from database.database import get_db
from database.models import Utilisateur, Eleve, Enseignant, CalendarEvent, RoleEnum
from utils.teacher_assignments import parse_teacher_assignments, subject_from_choice_token


MONTH_NAMES_FR = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
]


def _get_user_identifier() -> str:
    return (
        app.storage.user.get('email')
        or str(app.storage.user.get('user_id') or '')
        or 'anonymous'
    )


def _duration_to_minutes(raw_value: str) -> int:
    if not raw_value:
        return 0

    normalized = raw_value.strip().lower().replace(',', '.')
    compact_match = re.search(r'(\d+)\s*h\s*(\d{1,2})', normalized)
    if compact_match:
        return (int(compact_match.group(1)) * 60) + int(compact_match.group(2))

    total_minutes = 0
    hour_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:heure|heures|h)\b', normalized)
    for hour_raw in hour_matches:
        total_minutes += int(round(float(hour_raw) * 60))

    minute_matches = re.findall(r'(\d+)\s*(?:minute|minutes|min)\b', normalized)
    for minute_raw in minute_matches:
        total_minutes += int(minute_raw)

    return total_minutes


def _month_key_to_label(month_key: str) -> str:
    year_value, month_value = month_key.split('-')
    month_index = int(month_value) - 1
    return f"{MONTH_NAMES_FR[month_index].capitalize()} {year_value}"


def create():
    """Crée la page des statistiques"""
    # Aide IA: vue statistiques enrichie (par professeur + top prof prévu/réel)
    user_identifier = _get_user_identifier()
    available_events = [
        event for event in list_calendar_events_for_user(user_identifier)
        if (event.title or '').strip() and not (event.title or '').startswith('[DEMO-')
    ]
    available_dates: list[date] = []
    for event in available_events:
        if not event.date_iso:
            continue
        try:
            available_dates.append(date.fromisoformat(event.date_iso))
        except ValueError:
            continue
    available_dates.sort()

    default_start = available_dates[0] if available_dates else date.today()
    default_end = available_dates[-1] if available_dates else date.today()
    branch_options = ['Toutes'] + sorted({event.subject for event in available_events})

    student_class = ''
    teacher_directory: list[dict] = []
    db = get_db()
    try:
        current_user = db.query(Utilisateur).filter(Utilisateur.email == user_identifier).first()
        if current_user is not None:
            student_profile = db.query(Eleve).filter(Eleve.utilisateur_id == current_user.id).first()
            if student_profile is not None:
                student_class = (student_profile.classe or '').strip()

        teacher_rows = (
            db.query(Enseignant, Utilisateur)
            .join(Utilisateur, Utilisateur.id == Enseignant.utilisateur_id)
            .all()
        )
        for teacher_profile, teacher_user in teacher_rows:
            assignments_by_class = parse_teacher_assignments(teacher_profile.branches, teacher_profile.classes)
            teacher_classes = set(assignments_by_class.keys())
            teacher_by_class_subjects = {
                class_name: {subject_from_choice_token(token) for token in tokens}
                for class_name, tokens in assignments_by_class.items()
            }
            teacher_directory.append({
                'name': f'{teacher_user.prenom} {teacher_user.nom}',
                'classes': teacher_classes,
                'by_class_subjects': teacher_by_class_subjects,
            })
    finally:
        db.close()

    css_path = Path(__file__).resolve().parents[1] / 'static' / 'css' / 'custom.css'
    css_version = int(css_path.stat().st_mtime) if css_path.exists() else 0
    ui.add_head_html(f'<link rel="stylesheet" href="/static/css/custom.css?v={css_version}">')

    with ui.column().classes('stats-page-container'):
        ui.html('<div class="titre-container">Statistiques</div>', sanitize=False)

        with ui.column().classes('stats-filter-card'):
            stats_view_filter = ui.select(
                ['Par branche', 'Par professeur'],
                label='Vue statistique',
                value='Par branche',
            ).props('outlined dense').classes('w-full')

            branche_filter = ui.select(
                branch_options,
                label='Branche',
                value='Toutes',
            ).props('outlined dense').classes('w-full')

            with ui.row().classes('w-full no-wrap gap-2'):
                start_mode = ui.select(
                    ['Début', 'Choisir une date'],
                    label='Début',
                    value='Début',
                ).props('outlined dense').classes('flex-1')
                start_date_input = create_date_picker('Date de début', default_start)
                start_date_input.classes('flex-1')

            with ui.row().classes('w-full no-wrap gap-2'):
                end_mode = ui.select(
                    ['Aujourd\'hui', 'Choisir une date'],
                    label='Fin',
                    value='Aujourd\'hui',
                ).props('outlined dense').classes('flex-1')
                end_date_input = create_date_picker('Date de fin', default_end)
                end_date_input.classes('flex-1')

        summary_block = ui.html('', sanitize=False).classes('stats-summary')
        charts_container = ui.column().classes('stats-charts-container w-full')

        def _resolve_start_date() -> date:
            if start_mode.value == 'Choisir une date':
                selected = parse_date_input(start_date_input.value or '')
                return selected or default_start
            return default_start

        def _resolve_end_date() -> date:
            if end_mode.value == 'Choisir une date':
                selected = parse_date_input(end_date_input.value or '')
                return selected or default_end
            return default_end

        def _enforce_valid_date_range(changed_source: str | None = None) -> bool:
            start_date = _resolve_start_date()
            end_date = _resolve_end_date()
            if start_date <= end_date:
                return True

            if changed_source == 'start':
                ui.notify('La date de début est postérieure à la date de fin: la date de fin a été ajustée.', type='warning')
                if end_mode.value != 'Choisir une date':
                    end_mode.value = 'Choisir une date'
                    end_date_input.set_visibility(True)
                end_date_input.value = start_date.strftime('%d.%m.%Y')
                return True

            if changed_source == 'end':
                ui.notify('La date de fin est antérieure à la date de début: la date de début a été ajustée.', type='warning')
                if start_mode.value != 'Choisir une date':
                    start_mode.value = 'Choisir une date'
                    start_date_input.set_visibility(True)
                start_date_input.value = end_date.strftime('%d.%m.%Y')
                return True

            ui.notify('La date de début doit être avant ou égale à la date de fin', type='warning')

            if changed_source == 'start' and start_mode.value == 'Choisir une date':
                start_date_input.value = end_date.strftime('%d.%m.%Y')
            elif changed_source == 'end' and end_mode.value == 'Choisir une date':
                end_date_input.value = start_date.strftime('%d.%m.%Y')
            elif start_mode.value == 'Choisir une date':
                start_date_input.value = end_date.strftime('%d.%m.%Y')
            elif end_mode.value == 'Choisir une date':
                end_date_input.value = start_date.strftime('%d.%m.%Y')

            return False

        def _teachers_for_subject(subject: str) -> list[str]:
            matching_names: list[str] = []
            for teacher in teacher_directory:
                if student_class and teacher['classes'] and student_class not in teacher['classes']:
                    continue
                if student_class:
                    class_subjects = teacher['by_class_subjects'].get(student_class, set())
                else:
                    class_subjects = {
                        item
                        for values in teacher['by_class_subjects'].values()
                        for item in values
                    }
                if subject not in class_subjects:
                    continue
                matching_names.append(teacher['name'])
            return sorted(set(matching_names))

        def _render_statistics() -> None:
            start_date = _resolve_start_date()
            end_date = _resolve_end_date()
            if end_date < start_date:
                return

            selected_subject = branche_filter.value or 'Toutes'
            filtered_events = list_calendar_events_in_range(
                user_identifier=user_identifier,
                start_date=start_date,
                end_date=end_date,
                subject=selected_subject,
            )
            filtered_events = [
                event for event in filtered_events
                if (event.title or '').strip() and not (event.title or '').startswith('[DEMO-')
            ]

            total_real_minutes = sum(_duration_to_minutes(event.time_spent) for event in filtered_events)
            total_planned_minutes = sum(_duration_to_minutes(event.estimated_time) for event in filtered_events)
            total_real_hours = round(total_real_minutes / 60, 2)
            total_planned_hours = round(total_planned_minutes / 60, 2)
            summary_parts = [
                f'<div>Du {start_date.strftime("%d.%m.%Y")} au {end_date.strftime("%d.%m.%Y")}</div>',
                f'<div>{len(filtered_events)} événement(s) • Réel: {total_real_hours} h • Prévu: {total_planned_hours} h</div>',
            ]

            charts_container.clear()
            if not filtered_events:
                with charts_container:
                    with ui.column().classes('stats-chart-card'):
                        ui.label('Aucune donnée sur la période sélectionnée').classes('stats-empty-state')
                summary_block.content = ''.join(summary_parts)
                return

            if stats_view_filter.value == 'Par professeur':
                source_event_ids = sorted({
                    int(event.source_event_id)
                    for event in filtered_events
                    if event.source_event_id is not None
                })
                teacher_by_source_event_id: dict[int, str] = {}
                if source_event_ids:
                    db = get_db()
                    try:
                        source_rows = (
                            db.query(CalendarEvent.id, Utilisateur.prenom, Utilisateur.nom)
                            .join(Utilisateur, Utilisateur.email == CalendarEvent.user_identifier)
                            .filter(
                                CalendarEvent.id.in_(source_event_ids),
                                Utilisateur.role == RoleEnum.ENSEIGNANT,
                            )
                            .all()
                        )
                        for source_id, first_name, last_name in source_rows:
                            teacher_by_source_event_id[int(source_id)] = f'{first_name} {last_name}'.strip()
                    finally:
                        db.close()

                by_teacher: dict[str, dict[str, float]] = {}
                for event in filtered_events:
                    source_id = int(event.source_event_id) if event.source_event_id is not None else None
                    linked_teacher_name = teacher_by_source_event_id.get(source_id) if source_id is not None else None
                    if linked_teacher_name:
                        teachers = [linked_teacher_name]
                    else:
                        teachers = _teachers_for_subject(event.subject)
                        if not teachers:
                            teachers = ['Non attribué']

                    real_share = _duration_to_minutes(event.time_spent) / len(teachers)
                    planned_share = _duration_to_minutes(event.estimated_time) / len(teachers)
                    for teacher_name in teachers:
                        if teacher_name not in by_teacher:
                            by_teacher[teacher_name] = {'real': 0.0, 'planned': 0.0}
                        by_teacher[teacher_name]['real'] += real_share
                        by_teacher[teacher_name]['planned'] += planned_share

                sorted_teachers = sorted(
                    by_teacher.keys(),
                    key=lambda teacher_name: by_teacher[teacher_name]['planned'],
                    reverse=True,
                )
                real_hours_data = [round(by_teacher[name]['real'] / 60, 2) for name in sorted_teachers]
                planned_hours_data = [round(by_teacher[name]['planned'] / 60, 2) for name in sorted_teachers]

                if sorted_teachers:
                    top_teacher_name = sorted_teachers[0]
                    top_teacher_planned_hours = round(by_teacher[top_teacher_name]['planned'] / 60, 2)
                    top_teacher_real_hours = round(by_teacher[top_teacher_name]['real'] / 60, 2)
                    summary_parts.append(
                        f'<div>Prof donnant le plus de travail: {top_teacher_name} '
                        f'({top_teacher_planned_hours} h prévues, {top_teacher_real_hours} h réelles reportées par les élèves)</div>'
                    )

                with charts_container:
                    with ui.column().classes('stats-chart-card'):
                        ui.label('Temps de travail par professeur').classes('stats-chart-title')
                        ui.echart({
                            'legend': {
                                'data': ['Temps réel', 'Temps prévu'],
                                'bottom': 0,
                            },
                            'xAxis': {
                                'type': 'category',
                                'data': sorted_teachers,
                                'axisLabel': {'interval': 0, 'rotate': 20},
                            },
                            'yAxis': {
                                'type': 'value',
                                'name': 'Heures',
                            },
                            'tooltip': {'trigger': 'axis'},
                            'series': [
                                {
                                    'name': 'Temps réel',
                                    'type': 'bar',
                                    'data': real_hours_data,
                                    'itemStyle': {'color': '#f2c037'},
                                },
                                {
                                    'name': 'Temps prévu',
                                    'type': 'bar',
                                    'data': planned_hours_data,
                                    'itemStyle': {'color': '#4E7ED2'},
                                },
                            ],
                        }).classes('w-full stats-month-chart')

                summary_block.content = ''.join(summary_parts)
                return

            grouped_by_month: dict[str, dict[str, dict[str, int]]] = {}
            all_subjects = sorted({event.subject for event in filtered_events})

            for event in filtered_events:
                month_key = event.date_iso[:7]
                if month_key not in grouped_by_month:
                    grouped_by_month[month_key] = {}

                month_subjects = grouped_by_month[month_key]
                if event.subject not in month_subjects:
                    month_subjects[event.subject] = {'real': 0, 'planned': 0}

                month_subjects[event.subject]['real'] += _duration_to_minutes(event.time_spent)
                month_subjects[event.subject]['planned'] += _duration_to_minutes(event.estimated_time)

            with charts_container:
                for month_key in sorted(grouped_by_month.keys()):
                    month_data = grouped_by_month[month_key]
                    subject_labels = [subject for subject in all_subjects if subject in month_data]
                    real_hours_data = [round(month_data[subject]['real'] / 60, 2) for subject in subject_labels]
                    planned_hours_data = [round(month_data[subject]['planned'] / 60, 2) for subject in subject_labels]

                    with ui.column().classes('stats-chart-card'):
                        ui.label(_month_key_to_label(month_key)).classes('stats-chart-title')
                        ui.echart({
                            'legend': {
                                'data': ['Temps réel', 'Temps prévu'],
                                'bottom': 0,
                            },
                            'xAxis': {
                                'type': 'category',
                                'data': subject_labels,
                                'axisLabel': {'interval': 0, 'rotate': 20},
                            },
                            'yAxis': {
                                'type': 'value',
                                'name': 'Heures',
                            },
                            'tooltip': {'trigger': 'axis'},
                            'series': [
                                {
                                    'name': 'Temps réel',
                                    'type': 'bar',
                                    'data': real_hours_data,
                                    'itemStyle': {'color': '#f2c037'},
                                },
                                {
                                    'name': 'Temps prévu',
                                    'type': 'bar',
                                    'data': planned_hours_data,
                                    'itemStyle': {'color': '#4E7ED2'},
                                }
                            ],
                        }).classes('w-full stats-month-chart')

            summary_block.content = ''.join(summary_parts)

        def _update_filter_visibility() -> None:
            start_date_input.set_visibility(start_mode.value == 'Choisir une date')
            end_date_input.set_visibility(end_mode.value == 'Choisir une date')
            branche_filter.set_visibility(stats_view_filter.value == 'Par branche')
            if not _enforce_valid_date_range():
                return
            _render_statistics()

        def _on_start_date_change() -> None:
            if not _enforce_valid_date_range('start'):
                return
            _render_statistics()

        def _on_end_date_change() -> None:
            if not _enforce_valid_date_range('end'):
                return
            _render_statistics()

        stats_view_filter.on_value_change(lambda _: _update_filter_visibility())
        branche_filter.on_value_change(lambda _: _render_statistics())
        start_mode.on_value_change(lambda _: _update_filter_visibility())
        end_mode.on_value_change(lambda _: _update_filter_visibility())
        start_date_input.on_value_change(lambda _: _on_start_date_change())
        end_date_input.on_value_change(lambda _: _on_end_date_change())

        _update_filter_visibility()
        create_navbar()