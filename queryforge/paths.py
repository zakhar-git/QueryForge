from pathlib import Path
import os


PACKAGE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGE_DIR.parent
DATA_DIR = PACKAGE_DIR / "data"
ENTITY_DIR = DATA_DIR / "entities"
USER_DIR = Path(os.environ.get("QUERYFORGE_HOME", Path.home() / ".queryforge"))
OUTPUT_DIR = Path(os.environ.get("QUERYFORGE_OUTPUT", Path.cwd() / "output"))
SETTINGS_FILE = USER_DIR / "settings.json"
HISTORY_FILE = USER_DIR / "history.json"
