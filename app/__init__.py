#aide de l'IA
import sys
from pathlib import Path


_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from config.settings import APP_NAME, DEBUG, SECRET_KEY
from main import ui


class _AppRunner:
    def run(self, debug: bool = True) -> None:
        ui.run(
            title=APP_NAME,
            favicon='🎓',
            dark=False,
            reload=DEBUG and debug,
            show=True,
            port=8080,
            storage_secret=SECRET_KEY,
        )


def create_app() -> _AppRunner:
    return _AppRunner()
