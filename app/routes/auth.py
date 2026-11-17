import secrets

from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length

from app.extensions import db, login_manager
from app.models import Usuario
from app.services.auth_service import BLOQUEADO, OK, autenticar

bp = Blueprint("auth", __name__)

MSG_INVALIDO = "Login ou senha inválidos."
MSG_BLOQUEADO = "Muitas tentativas incorretas. Aguarde 15 minutos e tente de novo."


class LoginForm(FlaskForm):
    login = StringField(
        "Login",
        validators=[
            DataRequired("Informe o login."),
            Length(max=50, message="O login deve ter no máximo 50 caracteres."),
        ],
    )
    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired("Informe a senha."),
            Length(max=128, message="A senha deve ter no máximo 128 caracteres."),
        ],
    )


@login_manager.user_loader
def carregar_usuario(valor_da_sessao):
    """Reconstroi o usuario a partir do cookie. Recusa usuario inativo ou token trocado."""
    try:
        id_texto, token = valor_da_sessao.split(":", 1)
        usuario = db.session.get(Usuario, int(id_texto))
    except (ValueError, AttributeError):
        return None
    if usuario and usuario.ativo and secrets.compare_digest(usuario.token_sessao, token):
        return usuario
    return None


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.inicio"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario, resultado = autenticar(form.login.data, form.senha.data)
        if resultado == OK:
            session.clear()  # evita fixacao de sessao
            session.permanent = True
            login_user(usuario)
            return redirect(url_for("main.inicio"))
        flash(MSG_BLOQUEADO if resultado == BLOQUEADO else MSG_INVALIDO, "erro")

    return render_template("login.html", form=form)


@bp.post("/logout")
def logout():
    current_user.rotacionar_token()  # invalida qualquer copia antiga do cookie
    db.session.commit()
    logout_user()
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))