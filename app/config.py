import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'anime.db'}"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
