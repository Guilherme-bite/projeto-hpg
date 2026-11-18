from app import create_app
from app.extensions import db
from app.services.auth_service import criar_usuario
from app.models import Usuario

app = create_app()

with app.app_context():
    # Cria as tabelas
    db.create_all()
    print("Tabelas criadas em:", app.config["SQLALCHEMY_DATABASE_URI"])

    # Cria o usuário padrão se não existir
    if not Usuario.query.filter_by(login="guilherme").first():
        try:
            criar_usuario("guilherme", "ConferePix2026")
            print("Usuário 'guilherme' criado com sucesso.")
        except Exception as e:
            print("Erro ao criar usuário:", e)
    else:
        print("Usuário 'guilherme' já existe.")