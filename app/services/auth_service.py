"""Regras de autenticacao (RNF01): criar usuario, validar login e bloquear tentativas."""
import re
from datetime import timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.tentativa_login import TentativaLogin, agora_utc
from app.models.usuario import Usuario

LIMITE_TENTATIVAS = 5
JANELA = timedelta(minutes=15)
BLOQUEIO = timedelta(minutes=15)

OK = "ok"
INVALIDO = "invalido"
BLOQUEADO = "bloqueado"

_PADRAO_LOGIN = re.compile(r"^[a-z0-9._-]{3,50}$")
_hash_falso = None


def normalizar_login(login):
    return (login or "").strip().lower()[:50]


def criar_usuario(login, senha):
    login = (login or "").strip().lower()
    if not _PADRAO_LOGIN.match(login):
        raise ValueError(
            "O login deve ter de 3 a 50 caracteres: letras, numeros, ponto, "
            "underline ou hifen."
        )
    if Usuario.query.filter_by(login=login).first():
        raise ValueError("Esse login ja existe.")

    usuario = Usuario(login=login)
    usuario.definir_senha(senha)  # valida o tamanho minimo e gera o hash
    db.session.add(usuario)
    db.session.commit()
    return usuario


def _esta_bloqueado(login, agora):
    falhas = (
        TentativaLogin.query.filter(
            TentativaLogin.login == login, TentativaLogin.momento > agora - JANELA
        )
        .order_by(TentativaLogin.momento)
        .all()
    )
    if len(falhas) < LIMITE_TENTATIVAS:
        return False
    return agora < falhas[-1].momento + BLOQUEIO


def _registrar_falha(login, agora):
    db.session.add(TentativaLogin(login=login, momento=agora))
    # Limpeza: tentativas com mais de um dia nao servem mais.
    TentativaLogin.query.filter(TentativaLogin.momento < agora - timedelta(days=1)).delete()
    db.session.commit()


def _conferir_senha(usuario, senha):
    """Confere a senha. Se o usuario nao existe, gasta o mesmo tempo com um hash falso,
    para o tempo de resposta nao revelar se o login existe."""
    global _hash_falso
    if usuario is None:
        if _hash_falso is None:
            _hash_falso = generate_password_hash("senha-falsa-de-comparacao", method="scrypt")
        check_password_hash(_hash_falso, senha)
        return False
    return usuario.verificar_senha(senha)


def autenticar(login, senha, agora=None):
    """Devolve (usuario, resultado). Resultado: OK, INVALIDO ou BLOQUEADO."""
    agora = agora or agora_utc()
    login = normalizar_login(login)
    senha = senha or ""

    if _esta_bloqueado(login, agora):
        return None, BLOQUEADO

    usuario = Usuario.query.filter_by(login=login).first()
    senha_confere = _conferir_senha(usuario, senha)

    if usuario is None or not usuario.ativo or not senha_confere:
        _registrar_falha(login, agora)
        return None, INVALIDO

    TentativaLogin.query.filter_by(login=login).delete()
    db.session.commit()
    return usuario, OK