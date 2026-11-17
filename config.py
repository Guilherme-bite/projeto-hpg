import os
import tempfile
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "conferepix.db"),
    )
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(BASE_DIR, "instance", "uploads")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB, como no RF02

    # Sessao e cookie (RNF01)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE") == "1"  # 1 com HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_REFRESH_EACH_REQUEST = False  # 8 horas contadas a partir do login

    WTF_CSRF_ENABLED = True


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "chave-so-para-testes"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "conferepix_testes")
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False