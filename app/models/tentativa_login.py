from datetime import datetime, timezone

from app.extensions import db


def agora_utc():
    """UTC sem fuso (naive), o mesmo formato que o banco devolve ao ler."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TentativaLogin(db.Model):
    """Registra tentativas de login que falharam, inclusive de logins que nao existem."""

    __tablename__ = "tentativa_login"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, index=True)
    momento = db.Column(db.DateTime, nullable=False, default=agora_utc, index=True)