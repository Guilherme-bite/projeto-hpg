"""Cadastra um usuario da equipe. Nao existe cadastro publico no sistema (RNF01).

Uso: python criar_usuario.py
"""
import getpass
import sys

from app import create_app
from app.services.auth_service import criar_usuario


def main():
    app = create_app()
    login = input("Login: ")
    senha = getpass.getpass("Senha (minimo 10 caracteres): ")
    confirmacao = getpass.getpass("Repita a senha: ")

    if senha != confirmacao:
        print("As senhas nao conferem.")
        sys.exit(1)

    with app.app_context():
        try:
            usuario = criar_usuario(login, senha)
        except ValueError as erro:
            print("Nao foi possivel criar o usuario:", erro)
            sys.exit(1)
        print("Usuario criado:", usuario.login)


if __name__ == "__main__":
    main()