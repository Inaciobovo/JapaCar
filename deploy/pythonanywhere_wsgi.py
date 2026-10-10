"""Configuracao WSGI do JAPACAR para o PythonAnywhere (conta gratuita).

Como usar (resumo; o passo a passo completo esta no README):

1. Clone o repositorio em /home/USUARIO/JapaCar.
2. No Web Tab, crie um "Manual configuration" com Python 3.12 e aponte o
   Virtualenv para o ambiente criado no Bash console.
3. Abra o arquivo WSGI do seu web app (link no topo do Web Tab, algo como
   /var/www/USUARIO_pythonanywhere_com_wsgi.py), apague o conteudo de exemplo e
   cole o conteudo DESTE arquivo, trocando USUARIO pelo seu login.

O segredo (SECRET_KEY) fica num arquivo .env privado em /home/USUARIO/JapaCar/.env,
que nao vai para o repositorio. Sem ele o app recusa subir, de proposito.
"""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Troque pelo seu login do PythonAnywhere.
USUARIO = "SEU_USUARIO"
# ---------------------------------------------------------------------------

PROJETO = f"/home/{USUARIO}/JapaCar"

# Diretorios persistentes (o disco do PythonAnywhere e persistente, ao
# contrario de plataformas serverless). O SQLite e as fotos moram aqui.
(Path(PROJETO) / "data").mkdir(parents=True, exist_ok=True)
(Path(PROJETO) / "uploads").mkdir(parents=True, exist_ok=True)

# Carrega o .env privado (linhas CHAVE=valor) ANTES dos defaults, para que ele
# possa sobrescrever qualquer coisa. Sem dependencia extra (nada de python-dotenv).
_env = Path(PROJETO) / ".env"
if _env.exists():
    for linha in _env.read_text().splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip())

# Producao e obrigatorio: liga ProxyFix (HTTPS atras do proxy do PA), exige
# SECRET_KEY, TRUSTED_HOSTS e cookie Secure.
os.environ["FLASK_ENV"] = "prod"

# Host publico aceito no header Host. Ajuste se usar outro nome.
os.environ.setdefault("TRUSTED_HOSTS", f"{USUARIO}.pythonanywhere.com")

# Banco e fotos no disco persistente do projeto.
os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJETO}/data/japacar.db")
os.environ.setdefault("UPLOAD_DIR", f"{PROJETO}/uploads")

if not os.environ.get("SECRET_KEY"):
    raise RuntimeError(
        "SECRET_KEY ausente. Crie o arquivo "
        f"{PROJETO}/.env com a linha SECRET_KEY=<chave>. "
        'Gere com: python -c "import secrets; print(secrets.token_urlsafe(64))"'
    )

if PROJETO not in sys.path:
    sys.path.insert(0, PROJETO)

from app import create_app  # noqa: E402  (precisa vir depois de configurar o ambiente)

# O PythonAnywhere procura a variavel `application`.
application = create_app("prod")
