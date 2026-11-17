from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.models import TentativaLogin, Usuario
from app.services.auth_service import (
    BLOQUEADO,
    INVALIDO,
    OK,
    autenticar,
    criar_usuario,
)

SENHA = "senha-segura-123"
T0 = datetime(2026, 11, 17, 10, 0, 0)


@pytest.fixture
def conta(app):
    return criar_usuario("equipe", SENHA)


def entrar(cliente, login="equipe", senha=SENHA):
    return cliente.post("/login", data={"login": login, "senha": senha})


def falhar(vezes, login="equipe", inicio=T0):
    for i in range(vezes):
        autenticar(login, "senha-errada", agora=inicio + timedelta(seconds=i))


# ---- senha e cadastro -------------------------------------------------------

def test_banco_guarda_apenas_o_hash_da_senha(conta):
    assert conta.senha_hash.startswith("scrypt:")
    assert SENHA not in conta.senha_hash


def test_senha_curta_e_recusada(app):
    with pytest.raises(ValueError):
        criar_usuario("equipe", "curta123")


def test_login_repetido_e_recusado(conta):
    with pytest.raises(ValueError):
        criar_usuario("EQUIPE", SENHA)


def test_login_com_caracteres_invalidos_e_recusado(app):
    with pytest.raises(ValueError):
        criar_usuario("equipe <script>", SENHA)


# ---- login pelo navegador ---------------------------------------------------

def test_login_valido_abre_o_sistema(app, conta):
    cliente = app.test_client()

    resposta = entrar(cliente)

    assert resposta.status_code == 302
    assert cliente.get("/").status_code == 200


def test_mensagem_de_erro_e_igual_para_login_inexistente_e_senha_errada(app, conta):
    cliente = app.test_client()

    senha_errada = entrar(cliente, "equipe", "senha-errada-1")
    inexistente = entrar(cliente, "ninguem", "senha-errada-1")

    for resposta in (senha_errada, inexistente):
        assert resposta.status_code == 200
        assert "Login ou senha inválidos." in resposta.get_data(as_text=True)


@pytest.mark.parametrize("caminho", ["/", "/qualquer-coisa"])
def test_rotas_sem_login_levam_ao_login(app, caminho):
    resposta = app.test_client().get(caminho)

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_logout_sem_login_leva_ao_login(app):
    resposta = app.test_client().post("/logout")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_saude_continua_publica(app):
    assert app.test_client().get("/saude").status_code == 200


def test_logout_so_aceita_post(app, conta):
    cliente = app.test_client()
    entrar(cliente)

    assert cliente.get("/logout").status_code == 405


def test_logout_encerra_a_sessao(app, conta):
    cliente = app.test_client()
    entrar(cliente)

    cliente.post("/logout")

    assert cliente.get("/").status_code == 302


def test_cookie_antigo_nao_da_acesso_depois_do_logout(app, conta):
    cliente = app.test_client()
    entrar(cliente)
    cookie_antigo = cliente.get_cookie("session").value
    cliente.post("/logout")

    outro = app.test_client()
    outro.set_cookie("session", cookie_antigo)
    resposta = outro.get("/")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_usuario_desativado_perde_o_acesso_na_hora(app, conta):
    cliente = app.test_client()
    entrar(cliente)

    conta.ativo = False
    db.session.commit()

    assert cliente.get("/").status_code == 302


def test_usuario_inativo_nao_consegue_entrar(app, conta):
    conta.ativo = False
    db.session.commit()
    cliente = app.test_client()

    resposta = entrar(cliente)

    assert "Login ou senha inválidos." in resposta.get_data(as_text=True)
    assert cliente.get("/").status_code == 302


# ---- bloqueio por tentativas ------------------------------------------------

def test_seis_tentativas_seguidas_bloqueiam_ate_a_senha_certa(app, conta):
    cliente = app.test_client()
    for _ in range(5):
        entrar(cliente, senha="senha-errada-1")

    resposta = entrar(cliente)  # agora com a senha correta

    assert "Muitas tentativas" in resposta.get_data(as_text=True)
    assert cliente.get("/").status_code == 302


def test_apos_cinco_falhas_a_senha_certa_tambem_e_bloqueada(conta):
    falhar(5)

    usuario, resultado = autenticar("equipe", SENHA, agora=T0 + timedelta(minutes=5))

    assert usuario is None
    assert resultado == BLOQUEADO


def test_quatro_falhas_ainda_nao_bloqueiam(conta):
    falhar(4)

    usuario, resultado = autenticar("equipe", SENHA, agora=T0 + timedelta(minutes=1))

    assert resultado == OK
    assert usuario.login == "equipe"


def test_bloqueio_acaba_depois_de_15_minutos(conta):
    falhar(5)

    depois = T0 + timedelta(seconds=4) + timedelta(minutes=15, seconds=1)
    usuario, resultado = autenticar("equipe", SENHA, agora=depois)

    assert resultado == OK


def test_login_correto_zera_o_contador(conta):
    falhar(4)
    autenticar("equipe", SENHA, agora=T0 + timedelta(minutes=1))
    assert TentativaLogin.query.count() == 0

    falhar(4, inicio=T0 + timedelta(minutes=2))
    _, resultado = autenticar("equipe", SENHA, agora=T0 + timedelta(minutes=3))

    assert resultado == OK


def test_login_inexistente_tambem_e_bloqueado(conta):
    falhar(5, login="fantasma")

    _, resultado = autenticar("fantasma", "qualquer-coisa", agora=T0 + timedelta(minutes=1))

    assert resultado == BLOQUEADO


def test_falha_de_um_login_nao_bloqueia_outro(conta):
    criar_usuario("gerente", SENHA)
    falhar(5, login="equipe")

    _, resultado = autenticar("gerente", SENHA, agora=T0 + timedelta(minutes=1))

    assert resultado == OK


# ---- sessao e cookie --------------------------------------------------------

def test_cookie_de_sessao_tem_httponly_e_samesite(app, conta):
    resposta = entrar(app.test_client())

    cabecalho = resposta.headers.get("Set-Cookie", "")

    assert "HttpOnly" in cabecalho
    assert "SameSite=Lax" in cabecalho


def test_sessao_dura_8_horas(app):
    assert app.config["PERMANENT_SESSION_LIFETIME"] == timedelta(hours=8)


def test_formulario_sem_token_csrf_e_recusado(app, conta):
    app.config["WTF_CSRF_ENABLED"] = True

    resposta = app.test_client().post("/login", data={"login": "equipe", "senha": SENHA})

    assert resposta.status_code == 400