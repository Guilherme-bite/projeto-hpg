from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy import CheckConstraint

def agora():
    return datetime.now(timezone.utc)

class Pagamento(db.Model):
    __tablename__ = "pagamento"
    __table_args__ = (
        CheckConstraint("valor > 0", name="check_valor_pagamento_positivo"),
        CheckConstraint(
            "metodo != 'pix' OR comprovante_arquivo IS NOT NULL",
            name="check_pix_exige_comprovante",
        ),
        CheckConstraint(
            "metodo IN ('pix', 'dinheiro')",
            name="check_metodo_valido",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    metodo = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    comprovante_arquivo = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora)

    pedido = db.relationship("Pedido", back_populates="pagamentos")
    usuario = db.relationship("Usuario", back_populates="pagamentos")