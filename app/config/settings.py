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

# Configuration calendrier
CALENDAR_AUTO_ROLLOVER_HOUR = int(os.getenv('CALENDAR_AUTO_ROLLOVER_HOUR', '0'))
CALENDAR_AUTO_ROLLOVER_MINUTE = int(os.getenv('CALENDAR_AUTO_ROLLOVER_MINUTE', '0'))

# Configuration email (réinitialisation mot de passe)
SMTP_HOST = os.getenv('SMTP_HOST', '').strip()
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '').strip()
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '').strip()
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '').strip()
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True') == 'True'