from datetime import date, timedelta
import re
from database.database import get_db
from database.models import CalendarEvent, RoleEnum, Utilisateur, Enseignant
from utils.teacher_assignments import parse_teacher_assignments, subject_from_choice_token


def _student_has_subject_for_sync(
    subject: str,
    *,
    langue1: str,
    langue2: str,
    langue3: str,
    os_value: str,
    oc_value: str,
    basic_english: bool,
) -> bool:
    normalized_subject = (subject or '').strip()
    if not normalized_subject:
        return False

    if normalized_subject == 'Basic English':
        return bool(basic_english)

    selected_values = {
        (langue1 or '').strip(),
        (langue2 or '').strip(),
        (langue3 or '').strip(),
        (os_value or '').strip(),
        (oc_value or '').strip(),
    }
    selected_values = {value for value in selected_values if value}

    if normalized_subject.startswith('OS '):
        return (os_value or '').strip() == normalized_subject.removeprefix('OS ').strip()
    if normalized_subject.startswith('OC '):
        return (oc_value or '').strip() == normalized_subject.removeprefix('OC ').strip()

    if normalized_subject in selected_values:
        return True

    common_subjects = {
        'Mathématiques', 'Français', 'Histoire', 'Géographie',
        'Physique', 'Chimie', 'Biologie', 'Arts visuels', 'Éducation physique', 'Musique',
    }
    return normalized_subject in common_subjects


def sync_student_calendar_for_class_change(
    *,
    user_identifier: str,
    new_class: str,
    langue1: str,
    langue2: str,
    langue3: str,
    os_value: str,
    oc_value: str,
    basic_english: bool,
) -> tuple[int, int]:
    """Synchronise les événements élève quand sa classe change.

    Returns:
        (hidden_count, created_count)
    """
    # Aide IA: synchronisation automatique des événements liés lors d'un changement de classe
    normalized_class = (new_class or '').strip()
    if not user_identifier or not normalized_class:
        return (0, 0)

    db = get_db()
    try:
        hidden_count = 0
        created_count = 0

        # Hide linked events from other classes to prevent stale homework visibility.
        stale_events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.user_identifier == user_identifier,
                CalendarEvent.is_hidden.is_(False),
                CalendarEvent.source_event_id.isnot(None),
                (CalendarEvent.target_class.is_(None) | (CalendarEvent.target_class != normalized_class)),
            )
            .all()
        )
        for stale_event in stale_events:
            stale_event.is_hidden = True
            hidden_count += 1

        existing_source_ids = {
            source_id
            for (source_id,) in (
                db.query(CalendarEvent.source_event_id)
                .filter(
                    CalendarEvent.user_identifier == user_identifier,
                    CalendarEvent.is_hidden.is_(False),
                    CalendarEvent.source_event_id.isnot(None),
                    CalendarEvent.target_class == normalized_class,
                )
                .all()
            )
            if source_id is not None
        }

        teacher_events = (
            db.query(CalendarEvent)
            .join(Utilisateur, Utilisateur.email == CalendarEvent.user_identifier)
            .filter(
                Utilisateur.role == RoleEnum.ENSEIGNANT,
                CalendarEvent.is_hidden.is_(False),
                CalendarEvent.source_event_id.is_(None),
                (CalendarEvent.target_class == normalized_class) | CalendarEvent.target_class.is_(None),
            )
            .all()
        )

        teacher_assignments_cache: dict[int, dict[str, list[str]]] = {}

        def _teacher_teaches_subject_for_class(teacher_user_id: int | None, subject: str) -> bool:
            if teacher_user_id is None:
                return False
            if teacher_user_id not in teacher_assignments_cache:
                teacher_profile = (
                    db.query(Enseignant)
                    .filter(Enseignant.utilisateur_id == teacher_user_id)
                    .first()
                )
                assignments = parse_teacher_assignments(
                    teacher_profile.branches if teacher_profile else None,
                    teacher_profile.classes if teacher_profile else None,
                )
                teacher_assignments_cache[teacher_user_id] = assignments

            assignments = teacher_assignments_cache.get(teacher_user_id, {})
            class_tokens = assignments.get(normalized_class, [])
            class_subjects = {subject_from_choice_token(token) for token in class_tokens}
            return (subject or '').strip() in class_subjects

        for teacher_event in teacher_events:
            if teacher_event.id in existing_source_ids:
                continue

            event_target_class = (teacher_event.target_class or '').strip()
            if event_target_class and event_target_class != normalized_class:
                continue
            if not event_target_class:
                teacher_user = (
                    db.query(Utilisateur)
                    .filter(Utilisateur.email == teacher_event.user_identifier)
                    .first()
                )
                if not _teacher_teaches_subject_for_class(
                    teacher_user.id if teacher_user else None,
                    teacher_event.subject,
                ):
                    continue

            db.add(CalendarEvent(
                user_identifier=user_identifier,
                event_type=teacher_event.event_type,
                subject=teacher_event.subject,
                title=teacher_event.title,
                description=teacher_event.description,
                date_iso=teacher_event.date_iso,
                estimated_time=teacher_event.estimated_time,
                exam_coefficient=teacher_event.exam_coefficient,
                exam_duration=teacher_event.exam_duration,
                time_spent='0 minute',
                target_class=normalized_class,
                is_hidden=False,
                source_event_id=teacher_event.id,
            ))
            created_count += 1

        db.commit()
        return (hidden_count, created_count)
    finally:
        db.close()


def seed_default_calendar_events_for_user(user_identifier: str) -> None:
    if not user_identifier:
        return

    db = get_db()
    try:
        existing = db.query(CalendarEvent).filter(CalendarEvent.user_identifier == user_identifier).count()
        if existing > 0:
            return

        current_year = date.today().year
        default_rows = [
            CalendarEvent(
                user_identifier=user_identifier,
                event_type='devoir',
                subject='Mathématiques',
                title='',
                description='Exercice 1.20',
                date_iso=date(current_year, 1, 13).isoformat(),
                estimated_time='30 minutes',
                time_spent='1 heure',
                is_hidden=False,
            ),
            CalendarEvent(
                user_identifier=user_identifier,
                event_type='devoir',
                subject='Français',
                title='',
                description='Lecture de Théodat',
                date_iso=date(current_year, 1, 13).isoformat(),
                estimated_time='7 heures',
                time_spent='10 heures',
                is_hidden=False,
            ),
            CalendarEvent(
                user_identifier=user_identifier,
                event_type='examen',
                subject='Physique',
                title='',
                description='Magnétisme',
                date_iso=date(current_year, 1, 13).isoformat(),
                estimated_time='2 heures',
                time_spent='8 heures',
                is_hidden=False,
            ),
            CalendarEvent(
                user_identifier=user_identifier,
                event_type='devoir',
                subject='Chimie',
                title='',
                description='Exercice chapitre 5',
                date_iso=date(current_year, 1, 15).isoformat(),
                estimated_time='1 heure',
                time_spent='1h30',
                is_hidden=False,
            ),
            CalendarEvent(
                user_identifier=user_identifier,
                event_type='examen',
                subject='Anglais',
                title='',
                description='Grammaire et vocabulaire',
                date_iso=date(current_year, 1, 15).isoformat(),
                estimated_time='1 heure',
                time_spent='30 minutes',
                is_hidden=False,
            ),
        ]

        db.add_all(default_rows)
        db.commit()
    finally:
        db.close()


def list_calendar_events_for_user(user_identifier: str, include_hidden: bool = False) -> list[CalendarEvent]:
    if not user_identifier:
        return []

    db = get_db()
    try:
        query = db.query(CalendarEvent).filter(CalendarEvent.user_identifier == user_identifier)
        if not include_hidden:
            query = query.filter(CalendarEvent.is_hidden.is_(False))

        return query.order_by(CalendarEvent.date_iso.asc(), CalendarEvent.id.asc()).all()
    finally:
        db.close()


def create_calendar_event(
    *,
    user_identifier: str,
    event_type: str,
    subject: str,
    title: str,
    description: str,
    date_iso: str,
    estimated_time: str,
    exam_coefficient: float | None = None,
    exam_duration: str | None = None,
    time_spent: str = '0 minute',
    source_event_id: int | None = None,
    target_class: str | None = None,
) -> int:
    # Aide IA: extension des événements calendrier avec classe cible + métadonnées d'examen
    db = get_db()
    try:
        new_event = CalendarEvent(
            user_identifier=user_identifier,
            event_type=event_type,
            subject=subject,
            title=title,
            description=description,
            date_iso=date_iso,
            estimated_time=estimated_time,
            exam_coefficient=exam_coefficient,
            exam_duration=(exam_duration or '').strip() or None,
            time_spent=time_spent,
            target_class=(target_class or '').strip() or None,
            is_hidden=False,
            source_event_id=source_event_id,
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return int(new_event.id)
    finally:
        db.close()


def delete_calendar_event(event_id: int, user_identifier: str) -> bool:
    db = get_db()
    try:
        event = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.id == event_id,
                CalendarEvent.user_identifier == user_identifier,
            )
            .first()
        )
        if event is None:
            return False

        event.is_hidden = True
        
        linked_events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.source_event_id == event_id,
                CalendarEvent.is_hidden.is_(False),
            )
            .all()
        )
        for linked_event in linked_events:
            linked_event.is_hidden = True
        
        db.commit()
        return True
    finally:
        db.close()


def update_calendar_event_time_spent(event_id: int, user_identifier: str, time_spent: str) -> bool:
    db = get_db()
    try:
        event = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.id == event_id,
                CalendarEvent.user_identifier == user_identifier,
            )
            .first()
        )
        if event is None:
            return False

        event.time_spent = time_spent
        db.commit()
        return True
    finally:
        db.close()


def get_calendar_event_for_user(event_id: int, user_identifier: str) -> CalendarEvent | None:
    db = get_db()
    try:
        return (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.id == event_id,
                CalendarEvent.user_identifier == user_identifier,
                CalendarEvent.is_hidden.is_(False),
            )
            .first()
        )
    finally:
        db.close()


def update_calendar_event(
    *,
    event_id: int,
    user_identifier: str,
    event_type: str,
    subject: str,
    title: str,
    description: str,
    date_iso: str,
    estimated_time: str,
    exam_coefficient: float | None = None,
    exam_duration: str | None = None,
    target_class: str | None = None,
    propagate_to_linked: bool = True,
) -> bool:
    # Aide IA: propagation des modifications vers événements liés (élèves)
    db = get_db()
    try:
        event = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.id == event_id,
                CalendarEvent.user_identifier == user_identifier,
                CalendarEvent.is_hidden.is_(False),
            )
            .first()
        )
        if event is None:
            return False

        event.event_type = event_type
        event.subject = subject
        event.title = title
        event.description = description
        event.date_iso = date_iso
        event.estimated_time = estimated_time
        event.exam_coefficient = exam_coefficient
        event.exam_duration = (exam_duration or '').strip() or None
        event.target_class = (target_class or '').strip() or None
        db.commit()

        if propagate_to_linked:
            linked_events = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.source_event_id == event_id,
                    CalendarEvent.is_hidden.is_(False),
                )
                .all()
            )
            for linked_event in linked_events:
                linked_event.event_type = event_type
                linked_event.subject = subject
                linked_event.title = title
                linked_event.description = description
                linked_event.date_iso = date_iso
                linked_event.estimated_time = estimated_time
                linked_event.exam_coefficient = exam_coefficient
                linked_event.exam_duration = (exam_duration or '').strip() or None
                linked_event.target_class = (target_class or '').strip() or None
            db.commit()

        return True
    finally:
        db.close()


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


def _is_unfinished_event(time_spent: str) -> bool:
    normalized = (time_spent or '').strip()
    if not normalized:
        return True

    lowered = normalized.lower()
    if lowered in {'à compléter', 'a completer', '0 minute', '0 minutes', '0 min', '0h', '0 h'}:
        return True

    return _duration_to_minutes(normalized) <= 0


def move_unfinished_events_to_next_day(reference_date: date) -> int:
    today_iso = reference_date.isoformat()
    next_day_iso = (reference_date + timedelta(days=1)).isoformat()

    db = get_db()
    try:
        day_events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.date_iso == today_iso,
                CalendarEvent.is_hidden.is_(False),
            )
            .all()
        )
        moved_count = 0

        for event in day_events:
            if not _is_unfinished_event(event.time_spent):
                continue

            event.date_iso = next_day_iso
            moved_count += 1

        if moved_count > 0:
            db.commit()

        return moved_count
    finally:
        db.close()


def list_calendar_events_in_range(
    user_identifier: str,
    start_date: date,
    end_date: date,
    subject: str | None = None,
) -> list[CalendarEvent]:
    db = get_db()
    try:
        query = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.user_identifier == user_identifier,
                CalendarEvent.is_hidden.is_(False),
                CalendarEvent.date_iso >= start_date.isoformat(),
                CalendarEvent.date_iso <= end_date.isoformat(),
            )
        )

        if subject and subject != 'Toutes':
            query = query.filter(CalendarEvent.subject == subject)

        return query.order_by(CalendarEvent.date_iso.asc(), CalendarEvent.id.asc()).all()
    finally:
        db.close()


def average_student_time_spent_for_event(
    *,
    event_type: str,
    subject: str,
    title: str,
    description: str,
    date_iso: str,
    estimated_time: str,
    target_class: str | None = None,
) -> tuple[int | None, int]:
    db = get_db()
    try:
        matching_events = (
            db.query(CalendarEvent)
            .join(Utilisateur, Utilisateur.email == CalendarEvent.user_identifier)
            .filter(
                Utilisateur.role == RoleEnum.ELEVE,
                CalendarEvent.is_hidden.is_(False),
                CalendarEvent.event_type == event_type,
                CalendarEvent.subject == subject,
                CalendarEvent.title == title,
                CalendarEvent.description == description,
                CalendarEvent.date_iso == date_iso,
                CalendarEvent.estimated_time == estimated_time,
            )
        )

        normalized_target_class = (target_class or '').strip()
        if normalized_target_class:
            matching_events = matching_events.filter(CalendarEvent.target_class == normalized_target_class)

        matching_events = matching_events.all()

        completed_minutes: list[int] = []
        for event in matching_events:
            if _is_unfinished_event(event.time_spent):
                continue
            minutes = _duration_to_minutes(event.time_spent)
            if minutes > 0:
                completed_minutes.append(minutes)

        if not completed_minutes:
            return None, 0

        average_minutes = int(round(sum(completed_minutes) / len(completed_minutes)))
        return average_minutes, len(completed_minutes)
    finally:
        db.close()


def seed_statistics_demo_events_for_user(user_identifier: str) -> None:
    if not user_identifier:
        return

    db = get_db()
    try:
        existing_demo = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.user_identifier == user_identifier,
                CalendarEvent.title.like('[DEMO-STATS-V2]%'),
            )
            .count()
        )
        if existing_demo > 0:
            return

        subjects = ['Mathématiques', 'Français', 'Anglais', 'Physique', 'Chimie', 'Histoire']
        base_date = date.today() - timedelta(days=160)
        demo_rows: list[CalendarEvent] = []

        for index in range(20):
            event_date = base_date + timedelta(days=index * 4)
            estimated_minutes = 80 + ((index % 5) * 25)
            delta_minutes = [35, -20, 25, -15, 10][index % 5]
            spent_minutes = max(20, estimated_minutes + delta_minutes)
            subject = subjects[index % len(subjects)]
            demo_rows.append(
                CalendarEvent(
                    user_identifier=user_identifier,
                    event_type='devoir',
                    subject=subject,
                    title=f'[DEMO-STATS-V2] Devoir {index + 1}',
                    description='Donnée fictive pour test statistiques',
                    date_iso=event_date.isoformat(),
                    estimated_time=_format_minutes_for_storage(estimated_minutes),
                    time_spent=_format_minutes_for_storage(spent_minutes),
                    is_hidden=False,
                )
            )

        for index in range(10):
            event_date = base_date + timedelta(days=(index * 7) + 2)
            estimated_minutes = 120 + ((index % 4) * 30)
            delta_minutes = [-30, 45, -20, 35][index % 4]
            spent_minutes = max(30, estimated_minutes + delta_minutes)
            subject = subjects[(index + 2) % len(subjects)]
            demo_rows.append(
                CalendarEvent(
                    user_identifier=user_identifier,
                    event_type='examen',
                    subject=subject,
                    title=f'[DEMO-STATS-V2] Examen {index + 1}',
                    description='Donnée fictive pour test statistiques',
                    date_iso=event_date.isoformat(),
                    estimated_time=_format_minutes_for_storage(estimated_minutes),
                    time_spent=_format_minutes_for_storage(spent_minutes),
                    is_hidden=False,
                )
            )

        db.add_all(demo_rows)
        db.commit()
    finally:
        db.close()


def _format_minutes_for_storage(total_minutes: int) -> str:
    hours_value, minutes_value = divmod(total_minutes, 60)
    if hours_value and minutes_value:
        return f'{hours_value} h {minutes_value} min'
    if hours_value:
        return f'{hours_value} h'
    return f'{minutes_value} min'
