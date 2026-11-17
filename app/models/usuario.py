import secrets
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

TAMANHO_MINIMO_SENHA = 10


def agora():
    return datetime.now(timezone.utc)


def gerar_token():
    return secrets.token_hex(16)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    token_sessao = db.Column(db.String(64), nullable=False, default=gerar_token)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora)

    pagamentos = db.relationship("Pagamento", back_populates="usuario")

    @property
    def is_active(self):
        return bool(self.ativo)

    def get_id(self):
        # O token vai junto no cookie: ao trocar o token (logout), cookies antigos morrem.
        return f"{self.id}:{self.token_sessao}"

    def definir_senha(self, senha):
        if not senha or len(senha) < TAMANHO_MINIMO_SENHA:
            raise ValueError(
                f"A senha deve ter no minimo {TAMANHO_MINIMO_SENHA} caracteres."
            )
        self.senha_hash = generate_password_hash(senha, method="scrypt")

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def rotacionar_token(self):
        self.token_sessao = gerar_token()

    def __repr__(self):
        return f"<Usuario {self.login}>"