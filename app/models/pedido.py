from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy import CheckConstraint
from decimal import Decimal

PENDENTE = "pendente"
PARCIAL = "parcial"
PAGO = "pago"
A_CONFERIR = "a conferir"

def agora():
    return datetime.now(timezone.utc)

class Pedido(db.Model):
    __tablename__ = "pedido"
    __table_args__ = (
        CheckConstraint("valor_total > 0", name="check_valor_total_positivo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False, unique=True)
    cliente = db.Column(db.String(100), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    situacao = db.Column(db.String(20), nullable=False, default=PENDENTE)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora)

    pagamentos = db.relationship("Pagamento", back_populates="pedido")

    @property
    def valor_restante(self):
        """Calcula quanto falta pagar sem precisar abrir o pedido."""
        total_pago = sum((Decimal(str(p.valor)) for p in self.pagamentos), Decimal("0.00"))
        falta = Decimal(str(self.valor_total)) - total_pago
        return max(falta, Decimal("0.00"))

    def __repr__(self):
        return f"<Pedido {self.numero}>"