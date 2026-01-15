import re

def validate_email(email: str) -> bool:
    """Valide un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> tuple[bool, str]:
    """Valide un mot de passe (min 8 caractères)"""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    return True, ""

def validate_required_fields(**fields) -> tuple[bool, str]:
    """Vérifie que tous les champs requis sont remplis"""
    for field_name, field_value in fields.items():
        if not field_value or str(field_value).strip() == "":
            return False, f"Le champ {field_name} est requis"
    return True, ""