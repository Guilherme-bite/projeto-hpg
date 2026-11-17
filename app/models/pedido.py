from app.extensions import db
from app.models.usuario import agora

PENDENTE = "pendente"
PARCIAL = "parcial"
PAGO = "pago"
A_CONFERIR = "a conferir"
SITUACOES = (PENDENTE, PARCIAL, PAGO, A_CONFERIR)


class Pedido(db.Model):
    __tablename__ = "pedido"
    __table_args__ = (
        db.CheckConstraint("valor_total > 0", name="ck_pedido_valor_positivo"),
        db.CheckConstraint(
            "situacao IN ('pendente', 'parcial', 'pago', 'a conferir')",
            name="ck_pedido_situacao_valida",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.String(30), nullable=False, unique=True)
    cliente = db.Column(db.String(120), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    situacao = db.Column(db.String(20), nullable=False, default=PENDENTE)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora)

    pagamentos = db.relationship(
        "Pagamento", back_populates="pedido", order_by="Pagamento.id"
    )

    def __repr__(self):
        return f"<Pedido {self.numero_pedido}>"