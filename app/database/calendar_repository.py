from datetime import date, timedelta
import re
from database.database import get_db
from database.models import CalendarEvent


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
    time_spent: str = '0 minute',
) -> int:
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
            time_spent=time_spent,
            is_hidden=False,
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
