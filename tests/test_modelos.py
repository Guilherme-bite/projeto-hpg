from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Pagamento, Pedido


def novo_pagamento(pedido, usuario, **campos):
    dados = dict(
        pedido_id=pedido.id,
        usuario_id=usuario.id,
        metodo="pix",
        valor=100,
        comprovante_arquivo="a1b2c3.pdf",
    )
    dados.update(campos)
    return Pagamento(**dados)


def test_pedido_nasce_pendente(pedido):
    assert pedido.situacao == "pendente"
    assert pedido.valor_total == Decimal("450.00")
    assert pedido.pagamentos == []


def test_numero_de_pedido_nao_pode_repetir(pedido):
    db.session.add(Pedido(numero_pedido="1042", cliente="Outro", valor_total=10))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


@pytest.mark.parametrize("valor", [0, -5])
def test_valor_total_deve_ser_maior_que_zero(app, valor):
    db.session.add(Pedido(numero_pedido="9", cliente="X", valor_total=valor))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_pedido_pode_ter_tres_pix(pedido, usuario):
    for i in range(3):
        db.session.add(novo_pagamento(pedido, usuario, comprovante_arquivo=f"{i}.pdf"))
    db.session.commit()

    assert len(pedido.pagamentos) == 3
    assert pedido.pagamentos[0].usuario.login == "equipe"


def test_pix_exige_comprovante(pedido, usuario):
    db.session.add(novo_pagamento(pedido, usuario, comprovante_arquivo=None))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_dinheiro_nao_exige_comprovante(pedido, usuario):
    db.session.add(
        novo_pagamento(pedido, usuario, metodo="dinheiro", comprovante_arquivo=None)
    )
    db.session.commit()
    assert Pagamento.query.count() == 1


@pytest.mark.parametrize(
    "campos", [{"valor": 0}, {"valor": -1}, {"metodo": "cartao"}]
)
def test_pagamento_invalido_e_recusado(pedido, usuario, campos):
    db.session.add(novo_pagamento(pedido, usuario, **campos))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_pagamento_exige_pedido_existente(usuario):
    db.session.add(
        Pagamento(
            pedido_id=999, usuario_id=usuario.id, metodo="pix", valor=10,
            comprovante_arquivo="x.pdf",
        )
    )
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_pedido_com_pagamentos_nao_pode_ser_excluido(pedido, usuario):
    db.session.add(novo_pagamento(pedido, usuario))
    db.session.commit()

    db.session.delete(pedido)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()