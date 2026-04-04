from datetime import date
import re
from pathlib import Path
from nicegui import ui, app
from components.navbar import create_navbar
from pages.formulaire import create_date_picker, parse_date_input
from database.database import get_db
from database.models import Eleve, Utilisateur, Enseignant
from database.calendar_repository import list_calendar_events_in_range, list_calendar_events_for_user
from utils.school import all_school_classes, sort_school_classes
from utils.teacher_assignments import list_subjects_from_assignments, parse_teacher_assignments


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
    for hour_raw in re.findall(r'(\d+(?:\.\d+)?)\s*(?:heure|heures|h)\b', normalized):
        total_minutes += int(round(float(hour_raw) * 60))
    for minute_raw in re.findall(r'(\d+)\s*(?:minute|minutes|min)\b', normalized):
        total_minutes += int(minute_raw)
    return total_minutes


def create():
    teacher_email = _get_user_identifier()
    class_catalog = all_school_classes()
    class_lookup = {class_name.lower(): class_name for class_name in class_catalog}

    def normalize_class_name(class_name: str) -> str:
        raw_value = (class_name or '').strip()
        if not raw_value:
            return ''
        return class_lookup.get(raw_value.lower(), raw_value)

    db = get_db()
    try:
        teacher_user = db.query(Utilisateur).filter(Utilisateur.email == teacher_email).first()
        teacher_classes: set[str] = set()
        teacher_branches: list[str] = []
        if teacher_user is not None:
            teacher_row = db.query(Enseignant).filter(Enseignant.utilisateur_id == teacher_user.id).first()
            if teacher_row:
                teacher_assignments_by_class = parse_teacher_assignments(teacher_row.branches, teacher_row.classes)
                teacher_classes = {
                    normalize_class_name(item)
                    for item in (teacher_row.classes or '').split(',')
                    if normalize_class_name(item)
                }
                teacher_classes.update({
                    normalize_class_name(class_name)
                    for class_name in teacher_assignments_by_class.keys()
                    if normalize_class_name(class_name)
                })
                teacher_branches = list_subjects_from_assignments(teacher_assignments_by_class)
        teacher_branches = sorted(set(teacher_branches))

        teacher_row = (
            db.query(Eleve, Utilisateur)
            .join(Utilisateur, Utilisateur.id == Eleve.utilisateur_id)
            .all()
        )
    finally:
        db.close()

    class_to_students: dict[str, list[dict]] = {}
    for student, user in teacher_row:
        normalized_student_class = normalize_class_name(student.classe or '')
        if teacher_classes and normalized_student_class not in teacher_classes:
            continue
        student_item = {
            'email': user.email,
            'nom': user.nom,
            'prenom': user.prenom,
            'profile': student,
        }
        class_to_students.setdefault(normalized_student_class, []).append(student_item)

    class_options = sort_school_classes(sorted(set(class_to_students.keys()) | teacher_classes))
    default_class = class_options[0] if class_options else ''
    default_start = date.today()
    default_end = date.today()
    selected_branches: set[str] = set(teacher_branches)

    css_path = Path(__file__).resolve().parents[1] / 'static' / 'css' / 'custom.css'
    css_version = int(css_path.stat().st_mtime) if css_path.exists() else 0
    ui.add_head_html(f'<link rel="stylesheet" href="/static/css/custom.css?v={css_version}">')

    with ui.column().classes('stats-page-container'):
        ui.html('<div class="titre-container">Statistiques</div>', sanitize=False)

        with ui.column().classes('stats-filter-card'):
            class_filter = ui.select(
                class_options,
                label='Classe',
                value=default_class,
            ).props('outlined dense').classes('w-full')

            ui.label('Branches enseignées à afficher').classes('field-caption')
            branches_box = ui.column().classes('w-full q-mb-sm').style('max-height: 180px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px;')
            sync_lock = {'active': False}

            with branches_box:
                all_branches_checkbox = ui.checkbox('Toutes les branches', value=True)
                branch_checkboxes = []
                for branch_name in teacher_branches:
                    checkbox = ui.checkbox(branch_name, value=True)
                    branch_checkboxes.append((branch_name, checkbox))

            def _set_all_branches(checked: bool) -> None:
                sync_lock['active'] = True
                for branch_name, checkbox in branch_checkboxes:
                    checkbox.value = checked
                    if checked:
                        selected_branches.add(branch_name)
                    else:
                        selected_branches.discard(branch_name)
                sync_lock['active'] = False

            def _on_toggle_all(event) -> None:
                if sync_lock['active']:
                    return
                _set_all_branches(bool(event.value))
                _render()

            def _on_toggle_branch(event, branch_name: str) -> None:
                if sync_lock['active']:
                    return
                if event.value:
                    selected_branches.add(branch_name)
                else:
                    selected_branches.discard(branch_name)

                sync_lock['active'] = True
                all_branches_checkbox.value = (len(selected_branches) == len(teacher_branches))
                sync_lock['active'] = False
                _render()

            all_branches_checkbox.on_value_change(_on_toggle_all)
            for branch_name, checkbox in branch_checkboxes:
                checkbox.on_value_change(lambda event, b=branch_name: _on_toggle_branch(event, b))

            with ui.row().classes('w-full no-wrap gap-2'):
                start_mode = ui.select(['Début', 'Choisir une date'], label='Début', value='Début').props('outlined dense').classes('flex-1')
                start_date_input = create_date_picker('Date de début', default_start)
                start_date_input.classes('flex-1')

            with ui.row().classes('w-full no-wrap gap-2'):
                end_mode = ui.select(['Aujourd\'hui', 'Choisir une date'], label='Fin', value='Aujourd\'hui').props('outlined dense').classes('flex-1')
                end_date_input = create_date_picker('Date de fin', default_end)
                end_date_input.classes('flex-1')

        summary_block = ui.html('', sanitize=False).classes('stats-summary')
        chart_wrapper = ui.column().classes('stats-charts-container w-full')

        def _resolve_start_date() -> date:
            selected_class = class_filter.value or ''
            students = class_to_students.get(selected_class, [])
            first_dates: list[date] = []
            for student in students:
                events = list_calendar_events_for_user(student['email'])
                for event in events:
                    if not (event.title or '').strip() or (event.title or '').startswith('[DEMO-'):
                        continue
                    try:
                        first_dates.append(date.fromisoformat(event.date_iso))
                    except ValueError:
                        continue

            class_first_date = min(first_dates) if first_dates else default_start
            if start_mode.value == 'Choisir une date':
                picked = parse_date_input(start_date_input.value or '')
                return picked or class_first_date
            return class_first_date

        def _resolve_end_date() -> date:
            selected_class = class_filter.value or ''
            students = class_to_students.get(selected_class, [])
            last_dates: list[date] = []
            for student in students:
                events = list_calendar_events_for_user(student['email'])
                for event in events:
                    if not (event.title or '').strip() or (event.title or '').startswith('[DEMO-'):
                        continue
                    try:
                        last_dates.append(date.fromisoformat(event.date_iso))
                    except ValueError:
                        continue

            class_last_date = max(last_dates) if last_dates else default_end
            if end_mode.value == 'Choisir une date':
                picked = parse_date_input(end_date_input.value or '')
                return picked or class_last_date
            return class_last_date

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

        def _render() -> None:
            selected_class = class_filter.value or ''
            students = class_to_students.get(selected_class, [])
            start_date = _resolve_start_date()
            end_date = _resolve_end_date()
            if end_date < start_date:
                return

            names: list[str] = []
            real_hours: list[float] = []
            planned_hours: list[float] = []

            for student in students:
                events = list_calendar_events_in_range(
                    user_identifier=student['email'],
                    start_date=start_date,
                    end_date=end_date,
                    subject=None,
                )
                events = [
                    event for event in events
                    if (event.title or '').strip() and not (event.title or '').startswith('[DEMO-')
                ]
                if selected_branches:
                    events = [event for event in events if event.subject in selected_branches]
                else:
                    events = []
                real_minutes = sum(_duration_to_minutes(event.time_spent) for event in events)
                planned_minutes = sum(_duration_to_minutes(event.estimated_time) for event in events)

                names.append(f"{student['prenom']} {student['nom']}")
                real_hours.append(round(real_minutes / 60, 2))
                planned_hours.append(round(planned_minutes / 60, 2))

            total_real = round(sum(real_hours), 2)
            total_planned = round(sum(planned_hours), 2)
            summary_block.content = (
                f'<div>Classe {selected_class} • Du {start_date.strftime("%d.%m.%Y")} au {end_date.strftime("%d.%m.%Y")}</div>'
                f'<div>Réel: {total_real} h • Prévu: {total_planned} h</div>'
            )

            chart_wrapper.clear()
            with chart_wrapper:
                with ui.column().classes('stats-chart-card'):
                    if not names:
                        ui.label('Aucun élève ou aucune donnée pour cette sélection').classes('stats-empty-state')
                    else:
                        ui.echart({
                            'legend': {
                                'data': ['Temps réel', 'Temps prévu'],
                                'bottom': 0,
                            },
                            'xAxis': {
                                'type': 'category',
                                'data': names,
                                'axisLabel': {'interval': 0, 'rotate': 20},
                            },
                            'yAxis': {
                                'type': 'value',
                                'name': 'Heures',
                            },
                            'tooltip': {'trigger': 'axis'},
                            'series': [
                                {'name': 'Temps réel', 'type': 'bar', 'data': real_hours, 'itemStyle': {'color': '#f2c037'}},
                                {'name': 'Temps prévu', 'type': 'bar', 'data': planned_hours, 'itemStyle': {'color': '#4E7ED2'}},
                            ],
                        }).classes('w-full stats-month-chart')

        def _update_visibility() -> None:
            start_date_input.set_visibility(start_mode.value == 'Choisir une date')
            end_date_input.set_visibility(end_mode.value == 'Choisir une date')
            if not _enforce_valid_date_range():
                return
            _render()

        def _on_start_date_change() -> None:
            if not _enforce_valid_date_range('start'):
                return
            _render()

        def _on_end_date_change() -> None:
            if not _enforce_valid_date_range('end'):
                return
            _render()

        class_filter.on_value_change(lambda _: _render())
        start_mode.on_value_change(lambda _: _update_visibility())
        end_mode.on_value_change(lambda _: _update_visibility())
        start_date_input.on_value_change(lambda _: _on_start_date_change())
        end_date_input.on_value_change(lambda _: _on_end_date_change())

        _update_visibility()
        create_navbar()
