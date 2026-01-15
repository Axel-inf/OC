# Script d'initialisation de la BD
from .database import db

def init_database():
    """Initialise et crée les tables de la base de données"""
    db.create_all()
    print("Base de données initialisée")
