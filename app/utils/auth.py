import bcrypt
from database.models import Utilisateur, RoleEnum
from database.database import get_db

def hash_password(password: str) -> str:
    """Hash un mot de passe"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un mot de passe"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(email: str, password: str) -> Utilisateur | None:
    """Authentifie un utilisateur"""
    db = get_db()
    try:
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        if user and verify_password(password, user.mot_de_passe):
            return user
        return None
    finally:
        db.close()

def create_user(email: str, password: str, nom: str, prenom: str, role: str | RoleEnum) -> Utilisateur:
    """Crée un nouvel utilisateur"""
    db = get_db()
    try:
        hashed_pwd = hash_password(password)
        normalized_role = role
        if isinstance(role, str):
            normalized_role = RoleEnum(role.lower())

        user = Utilisateur(
            email=email,
            mot_de_passe=hashed_pwd,
            nom=nom,
            prenom=prenom,
            role=normalized_role
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()