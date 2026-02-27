import re


def all_school_classes() -> list[str]:
    classes: list[str] = []
    for level in range(1, 5):
        for group in range(1, 13):
            classes.append(f'{level}GY{group}')
    return sort_school_classes(classes)


def sort_school_classes(class_names: list[str]) -> list[str]:
    def _class_sort_key(class_name: str) -> tuple[int, str, int, str]:
        match = re.match(r'^(\d+)([A-Za-z]+)(\d+)$', class_name)
        if not match:
            return (999, class_name, 999, class_name)
        level = int(match.group(1))
        stream = match.group(2)
        number = int(match.group(3))
        return (level, stream, number, class_name)

    return sorted(class_names, key=_class_sort_key)


def standard_subjects() -> list[str]:
    return [
        'Mathématiques',
        'Français',
        'Allemand',
        'Anglais',
        'Histoire',
        'Géographie',
        'Physique',
        'Chimie',
        'Biologie',
        'Arts visuels',
        'Éducation physique',
        'Musique',
    ]


def os_subjects() -> list[str]:
    return [
        'OS Arts visuels',
        'OS Anglais',
        'OS Biologie et chimie',
        'OS Économie et droit',
        'OS Espagnol',
        'OS Grec',
        'OS Italien',
        'OS Latin (débutants)',
        'OS Latin (avancés)',
        'OS Musique',
        'OS Physique et application des mathématiques',
    ]


def oc_subjects() -> list[str]:
    return [
        'OC Applications des mathématiques',
        'OC Arts visuels',
        'OC Biologie',
        'OC Chimie',
        'OC Économie et droit',
        'OC Géographie',
        'OC Histoire',
        'OC Informatique',
        'OC Musique',
        'OC Philosophie',
        'OC Physique',
        'OC Psychologie et pédagogie',
        'OC Sciences politiques',
        'OC Sciences religieuses',
        'OC Sport',
    ]


def all_teaching_subjects() -> list[str]:
    return standard_subjects() + os_subjects() + oc_subjects() + ['Basic English']


def student_language_1_options() -> list[str]:
    return ['Français']


def student_language_options() -> list[str]:
    return ['Allemand', 'Anglais', 'Espagnol', 'Grec', 'Italien', 'Latin (débutants)', 'Latin (avancés)']


def student_os_options() -> list[str]:
    return [
        'Arts visuels', 'Anglais', 'Biologie et chimie', 'Économie et droit', 'Espagnol', 'Grec', 'Italien',
        'Latin (débutants)', 'Latin (avancés)', 'Musique', 'Physique et application des mathématiques',
    ]


def student_oc_options() -> list[str]:
    return [
        'Applications des mathématiques', 'Arts visuels', 'Biologie', 'Chimie', 'Économie et droit', 'Géographie',
        'Histoire', 'Informatique', 'Musique', 'Philosophie', 'Physique', 'Psychologie et pédagogie',
        'Sciences politiques', 'Sciences religieuses', 'Sport',
    ]
