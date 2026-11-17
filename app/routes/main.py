from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.get("/")
def inicio():
    return render_template("inicio.html")