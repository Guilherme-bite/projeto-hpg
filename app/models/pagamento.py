from app.extensions import db
from app.models.usuario import agora

PIX = "pix"
DINHEIRO = "dinheiro"
METODOS = (PIX, DINHEIRO)


class Pagamento(db.Model):
    __tablename__ = "pagamento"
    __table_args__ = (
        db.CheckConstraint("valor > 0", name="ck_pagamento_valor_positivo"),
        db.CheckConstraint(
            "metodo IN ('pix', 'dinheiro')", name="ck_pagamento_metodo_valido"
        ),
        db.CheckConstraint(
            "metodo <> 'pix' OR comprovante_arquivo IS NOT NULL",
            name="ck_pagamento_pix_exige_comprovante",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("pedido.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    metodo = db.Column(db.String(10), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    registrado_em = db.Column(db.DateTime, nullable=False, default=agora, index=True)
    comprovante_arquivo = db.Column(db.String(255), nullable=True)

    pedido = db.relationship("Pedido", back_populates="pagamentos")
    usuario = db.relationship("Usuario", back_populates="pagamentos")

    def __repr__(self):
        return f"<Pagamento {self.metodo} {self.valor}>"