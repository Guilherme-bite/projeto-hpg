from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Pagamento
from app.services.pedido_service import (
    calcular_situacao,
    recalcular_situacao,
    total_pago,
    valor_restante,
)


# ---- regra pura (sem banco) -------------------------------------------------

def test_sem_pagamentos_fica_pendente():
    assert calcular_situacao(300, []) == "pendente"


def test_pagamento_menor_que_o_total_fica_parcial():
    assert calcular_situacao(300, [100]) == "parcial"


def test_pagamento_igual_ao_total_fica_pago():
    assert calcular_situacao(300, [300]) == "pago"


def test_pagamento_maior_que_o_total_fica_a_conferir():
    assert calcular_situacao(300, [350]) == "a conferir"


def test_pedido_pago_com_tres_pix():
    assert calcular_situacao(300, [100, 100, 100]) == "pago"


def test_dois_pix_ainda_deixam_parcial():
    assert calcular_situacao(300, [100, 100]) == "parcial"


def test_tres_pix_que_passam_do_total_ficam_a_conferir():
    assert calcular_situacao(300, [100, 100, 150]) == "a conferir"


def test_centavos_sao_somados_sem_erro_de_float():
    # Com float, 0.10 + 0.20 daria 0.30000000000000004 e nao bateria com 0.30.
    assert calcular_situacao("0.30", ["0.10", "0.20"]) == "pago"


@pytest.mark.parametrize(
    "total, pagos, esperado",
    [
        (450, [200], "parcial"),
        (450, [200, 100], "parcial"),
        (450, [200, 100, 150], "pago"),
        (450, [200, 100, 150, 1], "a conferir"),
    ],
)
def test_sequencia_do_pedido_1042_do_prototipo(total, pagos, esperado):
    assert calcular_situacao(total, pagos) == esperado


# ---- regra aplicada a um pedido do banco ------------------------------------

def registrar(pedido, usuario, valor, metodo="pix"):
    pagamento = Pagamento(
        pedido_id=pedido.id,
        usuario_id=usuario.id,
        metodo=metodo,
        valor=valor,
        comprovante_arquivo="arquivo.pdf" if metodo == "pix" else None,
    )
    db.session.add(pagamento)
    db.session.commit()


def test_recalcular_acompanha_os_pagamentos(pedido, usuario):
    assert recalcular_situacao(pedido) == "pendente"

    registrar(pedido, usuario, 200)
    assert recalcular_situacao(pedido) == "parcial"

    registrar(pedido, usuario, 100)
    assert recalcular_situacao(pedido) == "parcial"

    registrar(pedido, usuario, 150)
    assert recalcular_situacao(pedido) == "pago"

    registrar(pedido, usuario, 50, metodo="dinheiro")
    assert recalcular_situacao(pedido) == "a conferir"


def test_situacao_recalculada_e_gravada_no_banco(pedido, usuario):
    registrar(pedido, usuario, 200)
    recalcular_situacao(pedido)
    db.session.commit()
    db.session.expire_all()

    assert pedido.situacao == "parcial"


def test_total_pago_e_valor_restante_do_prototipo(pedido, usuario):
    # Tela 2 do prototipo: pedido de R$ 450,00 com Pix de R$ 200,00.
    registrar(pedido, usuario, 200)

    assert total_pago(pedido) == Decimal("200.00")
    assert valor_restante(pedido) == Decimal("250.00")


def test_valor_restante_nunca_fica_negativo(pedido, usuario):
    registrar(pedido, usuario, 500)

    assert valor_restante(pedido) == Decimal("0.00")