import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "pdf"}

def arquivo_permitido(nome_arquivo):
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS

def salvar_comprovante(arquivo):
    """Salva o arquivo com nome aleatório e seguro na pasta instance/uploads."""
    if not arquivo or not arquivo.filename:
        return None
    
    if not arquivo_permitido(arquivo.filename):
        raise ValueError("Formato de arquivo não permitido. Use imagem ou PDF.")

    # Gera um nome único para evitar colisões e problemas de segurança
    ext = arquivo.filename.rsplit(".", 1)[1].lower()
    nome_seguro = f"{uuid.uuid4().hex}.{ext}"
    
    caminho_completo = os.path.join(current_app.config["UPLOAD_FOLDER"], nome_seguro)
    arquivo.save(caminho_completo)
    return nome_seguro