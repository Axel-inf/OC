import json
import re
from typing import Iterable

from utils.school import oc_subjects, os_subjects, standard_subjects


_TRACK_STANDARD = 'standard'
_TRACK_BILINGUE = 'bilingue'


def _extract_class_level(class_name: str) -> int | None:
    match = re.match(r'^(\d+)', (class_name or '').strip())
    if not match:
        return None
    return int(match.group(1))


def _is_pam_class(class_name: str) -> bool:
    return 'pam' in (class_name or '').lower()


def bilingual_subjects_for_class(class_name: str) -> set[str]:
    level = _extract_class_level(class_name)
    if level is None:
        return set()

    if level == 1:
        return {'Économie et droit'}

    if level == 2:
        subjects = {'Histoire', 'Biologie'}
        if not _is_pam_class(class_name):
            subjects.update({'Mathématiques', 'Physique'})
        return subjects

    if level in {3, 4}:
        subjects = {'Histoire'}
        if not _is_pam_class(class_name):
            subjects.update({'Mathématiques', 'Physique'})
        return subjects

    return set()


def _standard_subjects_for_teacher() -> list[str]:
    return sorted({subject for subject in standard_subjects() if subject})


def _base_subjects_for_teacher() -> set[str]:
    excluded_subjects = {'Chimie', 'Biologie', 'Géographie'}
    return {subject for subject in _standard_subjects_for_teacher() if subject not in excluded_subjects}


def _available_subjects_for_class(class_name: str) -> list[str]:
    level = _extract_class_level(class_name)
    base = _base_subjects_for_teacher() | {'Basic English'}

    if level == 1:
        subjects = base | {'Chimie', 'Biologie', 'Géographie', 'Économie et droit', 'Sciences religieuses'}
    elif level == 2:
        subjects = base | {'Chimie', 'Biologie', 'Géographie'} | set(os_subjects())
    elif level in {3, 4}:
        subjects = base | {'Philosophie'} | set(os_subjects()) | set(oc_subjects())
    else:
        subjects = base | {'Chimie', 'Biologie', 'Géographie'} | set(os_subjects()) | set(oc_subjects())

    return sorted(subjects)


def build_subject_option_labels_for_class(class_name: str) -> list[str]:
    labels: list[str] = []
    for subject in _available_subjects_for_class(class_name):
        labels.append(subject)

    for subject in sorted(bilingual_subjects_for_class(class_name)):
        labels.append(f'{subject} bilingue')

    return labels


def build_subject_options_for_class(class_name: str) -> dict[str, str]:
    options: dict[str, str] = {}

    for subject in _available_subjects_for_class(class_name):
        token = make_choice_token(subject, _TRACK_STANDARD)
        options[token] = subject

    for subject in sorted(bilingual_subjects_for_class(class_name)):
        token = make_choice_token(subject, _TRACK_BILINGUE)
        options[token] = f'{subject} <strong>bilingue</strong>'

    return options


def make_choice_token(subject: str, track: str) -> str:
    normalized_track = _TRACK_BILINGUE if track == _TRACK_BILINGUE else _TRACK_STANDARD
    return f'{subject.strip()}||{normalized_track}'


def parse_label_to_choice_token(label: str) -> str | None:
    raw_label = re.sub(r'<[^>]+>', '', (label or '')).strip()
    if not raw_label:
        return None

    if '||' in raw_label:
        subject, track = split_choice_token(raw_label)
        return make_choice_token(subject, track)

    if raw_label.endswith(' bilingue'):
        return make_choice_token(raw_label[:-9], _TRACK_BILINGUE)
    if raw_label.endswith(' standard'):
        return make_choice_token(raw_label[:-9], _TRACK_STANDARD)

    return make_choice_token(raw_label, _TRACK_STANDARD)


def token_to_label(token: str) -> str:
    subject, track = split_choice_token(token)
    if track == _TRACK_BILINGUE:
        return f'{subject} bilingue'
    return subject


def token_to_html_label(token: str) -> str:
    subject, track = split_choice_token(token)
    if track == _TRACK_BILINGUE:
        return f'{subject} <strong>bilingue</strong>'
    return subject


def split_choice_token(token: str) -> tuple[str, str]:
    raw_token = (token or '').strip()
    if '||' in raw_token:
        subject, raw_track = raw_token.split('||', 1)
        track = _TRACK_BILINGUE if raw_track == _TRACK_BILINGUE else _TRACK_STANDARD
        return subject.strip(), track

    lowered = raw_token.lower()
    if lowered.endswith(' bilingue'):
        return raw_token[:-9].strip(), _TRACK_BILINGUE
    if lowered.endswith(' standard'):
        return raw_token[:-9].strip(), _TRACK_STANDARD
    return raw_token.strip(), _TRACK_STANDARD


def is_bilingual_choice_token(token: str) -> bool:
    return split_choice_token(token)[1] == _TRACK_BILINGUE


def subject_from_choice_token(token: str) -> str:
    return split_choice_token(token)[0]


def serialize_teacher_assignments(assignments_by_class: dict[str, Iterable[str]]) -> str:
    cleaned: dict[str, list[str]] = {}
    for class_name, tokens in assignments_by_class.items():
        key = (class_name or '').strip()
        if not key:
            continue
        unique_tokens = sorted({(token or '').strip() for token in tokens if (token or '').strip()})
        if unique_tokens:
            cleaned[key] = unique_tokens

    payload = {
        'version': 2,
        'by_class': cleaned,
    }
    return json.dumps(payload, ensure_ascii=False)


def parse_teacher_assignments(raw_branches: str | None, raw_classes: str | None) -> dict[str, list[str]]:
    classes = [item.strip() for item in (raw_classes or '').split(',') if item.strip()]

    if raw_branches:
        try:
            decoded = json.loads(raw_branches)
            by_class = decoded.get('by_class', {}) if isinstance(decoded, dict) else {}
            parsed: dict[str, list[str]] = {}
            if isinstance(by_class, dict):
                for class_name, values in by_class.items():
                    if not isinstance(values, list):
                        continue
                    tokens = []
                    for value in values:
                        token = parse_label_to_choice_token(str(value))
                        if token:
                            tokens.append(token)
                    if tokens:
                        parsed[str(class_name).strip()] = sorted(set(tokens))
            if parsed:
                return parsed
        except json.JSONDecodeError:
            pass

    legacy_branches = [item.strip() for item in (raw_branches or '').split(',') if item.strip()]
    tokens = [make_choice_token(branch, _TRACK_STANDARD) for branch in legacy_branches]
    parsed_legacy: dict[str, list[str]] = {}
    for class_name in classes:
        parsed_legacy[class_name] = sorted(set(tokens))
    return parsed_legacy


def list_subjects_from_assignments(assignments_by_class: dict[str, list[str]]) -> list[str]:
    subjects = {subject_from_choice_token(token) for values in assignments_by_class.values() for token in values}
    return sorted(subjects)


def list_subjects_for_class(assignments_by_class: dict[str, list[str]], class_name: str) -> list[str]:
    values = assignments_by_class.get((class_name or '').strip(), [])
    return sorted({subject_from_choice_token(token) for token in values})
