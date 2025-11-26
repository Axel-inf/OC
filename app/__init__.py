from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schoolplanner.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "a"

    # Initialise SQLAlchemy avec l'app Flask
    db.init_app(app)

    # Importer les modèles, nécessaire pour créer les tables
    from . import models

    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()

    # Charger les routes
    from .routes import register_routes
    register_routes(app)

    return app

