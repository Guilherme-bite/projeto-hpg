import os

from flask import Flask

from config import Config


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Defina SECRET_KEY no arquivo .env")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.get("/saude")
    def saude():
        return {"status": "ok"}

    return app