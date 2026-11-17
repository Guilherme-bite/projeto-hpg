import pytest

from app import create_app
from app.extensions import db
from app.models import Pedido, Usuario
from config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def usuario(app):
    u = Usuario(login="equipe", senha_hash="hash-de-teste")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def pedido(app):
    p = Pedido(numero="1042", cliente="Cliente Teste", valor_total=450)
    db.session.add(p)
    db.session.commit()
    return p
