import os
from pathlib import Path
from dotenv import load_dotenv

_SETTINGS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _SETTINGS_FILE.parents[2]
_APP_ROOT = _SETTINGS_FILE.parents[1]

load_dotenv(_PROJECT_ROOT / '.env')
load_dotenv(_APP_ROOT / '.env')

# Configuration base de données
_DEFAULT_SQLITE_PATH = (_PROJECT_ROOT / 'app.db').resolve()
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{_DEFAULT_SQLITE_PATH.as_posix()}")

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
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '').replace(' ', '').strip()
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '').strip()
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True') == 'True'