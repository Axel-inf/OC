import os
from dotenv import load_dotenv

load_dotenv()

# Configuration base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')

# Configuration application
SECRET_KEY = os.getenv('SECRET_KEY', 'votre-clé-secrète-à-changer')
APP_NAME = "Planification Devoirs - Collège du Sud"
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Configuration authentification
SESSION_TIMEOUT = 3600  # 1 heure en secondes