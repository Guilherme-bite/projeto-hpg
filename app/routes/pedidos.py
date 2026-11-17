from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Pedido, Pagamento
from app.services.pedido_service import recalcular_situacao
from app.services.pagamento_service import salvar_comprovante
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

bp = Blueprint("pedidos", __name__)

@bp.route("/pedidos")
@login_required
def listar():
    pedidos = Pedido.query.order_by(Pedido.criado_em.desc()).all()
    return render_template("pedidos.html", pedidos=pedidos)

@bp.route("/pedidos/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        numero = request.form.get("numero")
        cliente = request.form.get("cliente")
        valor_total = request.form.get("valor_total")

        if not numero or not cliente or not valor_total:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("pedidos.novo"))

        try:
            novo_pedido = Pedido(numero=numero, cliente=cliente, valor_total=valor_total)
            db.session.add(novo_pedido)
            db.session.commit()
            flash("Pedido cadastrado com sucesso!", "info")
            return redirect(url_for("pedidos.listar"))
        except IntegrityError:
            db.session.rollback()
            flash("Erro: Já existe um pedido com esse número.", "erro")
            return redirect(url_for("pedidos.novo"))

    return render_template("novo_pedido.html")

@bp.route("/pedidos/<int:pedido_id>/pagamento", methods=["GET", "POST"])
@login_required
def registrar_pagamento(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)

    if request.method == "POST":
        metodo = request.form.get("metodo")
        valor = request.form.get("valor")
        arquivo = request.files.get("comprovante")

        # Validação amigável antes de ir para o banco
        if metodo == "pix" and (not arquivo or not arquivo.filename):
            flash("Para pagamentos via Pix, é obrigatório anexar o comprovante.", "erro")
            return redirect(url_for("pedidos.registrar_pagamento", pedido_id=pedido.id))

        try:
            nome_arquivo = salvar_comprovante(arquivo)
            novo_pagamento = Pagamento(
                pedido_id=pedido.id,
                usuario_id=current_user.id,
                metodo=metodo,
                valor=valor,
                comprovante_arquivo=nome_arquivo
            )
            db.session.add(novo_pagamento)
            
            db.session.flush()
            recalcular_situacao(pedido)
            
            db.session.commit()
            flash("Pagamento registrado!", "info")
            return redirect(url_for("pedidos.listar"))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "erro")
        except IntegrityError:
            db.session.rollback()
            flash("Erro de integridade. Verifique os dados do pagamento.", "erro")

    return render_template("registrar_pagamento.html", pedido=pedido)

@bp.route("/conferencia")
@login_required
def conferencia():
    hoje = datetime.now(timezone.utc).date()
    pedidos = Pedido.query.all()
    total_pix = sum(p.valor for p in Pagamento.query.filter(Pagamento.metodo == "pix").all())
    total_dinheiro = sum(p.valor for p in Pagamento.query.filter(Pagamento.metodo == "dinheiro").all())
    
    return render_template("conferencia.html", pedidos=pedidos, total_pix=total_pix, total_dinheiro=total_dinheiro)