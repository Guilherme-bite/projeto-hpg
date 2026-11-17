from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy import CheckConstraint

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

    # Sem o cascade delete-orphan para que o banco bloqueie a exclusão se houver pagamentos
    pagamentos = db.relationship("Pagamento", back_populates="pedido")

    def __repr__(self):
        return f"<Pedido {self.numero}>"