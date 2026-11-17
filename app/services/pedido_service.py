"""Regras de negocio dos pedidos (RF03).

Esta camada nao conhece telas nem rotas: so recebe dados, aplica a regra e
devolve o resultado. Por isso pode ser testada de forma isolada.
"""
from decimal import Decimal

from app.models.pedido import A_CONFERIR, PAGO, PARCIAL, PENDENTE

CENTAVOS = Decimal("0.01")


def _dinheiro(valor):
    """Converte para Decimal com 2 casas. Passa por str para nao herdar erro de float."""
    return Decimal(str(valor)).quantize(CENTAVOS)


def calcular_situacao(valor_total, valores_pagos):
    """Define a situacao do pedido a partir do total e dos pagamentos.

    - pendente:   nao ha pagamentos
    - parcial:    soma maior que zero e menor que o total
    - pago:       soma igual ao total
    - a conferir: soma maior que o total
    """
    total = _dinheiro(valor_total)
    pagos = [_dinheiro(v) for v in valores_pagos]

    if not pagos:
        return PENDENTE

    soma = sum(pagos, Decimal("0.00"))
    if soma < total:
        return PARCIAL
    if soma == total:
        return PAGO
    return A_CONFERIR


def total_pago(pedido):
    return sum((_dinheiro(p.valor) for p in pedido.pagamentos), Decimal("0.00"))


def valor_restante(pedido):
    """Quanto falta pagar. Nunca negativo: se pagou a mais, falta zero."""
    falta = _dinheiro(pedido.valor_total) - total_pago(pedido)
    return max(falta, Decimal("0.00"))


def recalcular_situacao(pedido):
    """Atualiza pedido.situacao com base nos pagamentos atuais.

    Nao faz commit: quem chama decide quando gravar, junto com o pagamento.
    """
    pedido.situacao = calcular_situacao(
        pedido.valor_total, [p.valor for p in pedido.pagamentos]
    )
    return pedido.situacao