"""Cria as tabelas do banco. Uso: python init_db.py"""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Tabelas criadas em:", app.config["SQLALCHEMY_DATABASE_URI"])