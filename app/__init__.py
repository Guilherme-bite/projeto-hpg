import os

from flask import Flask, request
from flask_login import current_user

from app.extensions import csrf, db, login_manager
from config import Config

ROTAS_PUBLICAS = {"auth.login", "saude", "static"}


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Defina SECRET_KEY no arquivo .env")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para continuar."
    login_manager.login_message_category = "info"

    from app import models  # noqa: F401  (registra as tabelas no SQLAlchemy)
    from app.routes import auth, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    @app.before_request
    def exigir_login():
        """Toda rota exige login, exceto as da lista de publicas (RNF01)."""
        if request.endpoint in ROTAS_PUBLICAS:
            return None
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        return None

    @app.get("/saude")
    def saude():
        return {"status": "ok"}

    return app