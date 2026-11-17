from app import create_app
from config import TestConfig


def test_saude_responde_ok():
    app = create_app(TestConfig)
    client = app.test_client()

    resposta = client.get("/saude")

    assert resposta.status_code == 200
    assert resposta.get_json() == {"status": "ok"}