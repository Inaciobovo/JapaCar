#!/usr/bin/env bash
# Setup automatico do JAPACAR no PythonAnywhere (conta gratuita).
#
# Uso (no Bash console do PythonAnywhere):
#   bash ~/JapaCar/deploy/pythonanywhere_setup.sh
#
# Faz tudo o que da para automatizar pelo console: virtualenv, dependencias,
# SECRET_KEY, diretorios persistentes, WSGI ja com o seu login e o usuario
# admin. O unico passo manual e colar a configuracao no Web Tab (o script
# imprime exatamente o que colar).
set -euo pipefail

USUARIO="${USER:-$(whoami)}"
PROJETO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$HOME/.virtualenvs/japacar"
DOMINIO="${USUARIO}.pythonanywhere.com"
ENV_FILE="$PROJETO/.env"

echo "==> Usuario : $USUARIO"
echo "==> Projeto : $PROJETO"

# 1. Interpretador (prefere 3.12, aceita 3.13/3).
PY=""
for cand in /usr/bin/python3.12 /usr/bin/python3.13 /usr/bin/python3; do
  if [ -x "$cand" ]; then PY="$cand"; break; fi
done
if [ -z "$PY" ]; then
  echo "ERRO: nenhum python3 encontrado no sistema." >&2
  exit 1
fi
echo "==> Python  : $PY ($("$PY" --version 2>&1))"

# 2. Virtualenv
if [ -d "$VENV" ]; then
  echo "==> Virtualenv ja existe, reaproveitando: $VENV"
else
  echo "==> Criando virtualenv em $VENV"
  "$PY" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# 3. Dependencias
echo "==> Instalando dependencias (requirements.txt)..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "$PROJETO/requirements.txt"
echo "==> Dependencias instaladas."

# 4. SECRET_KEY em .env privado (nao versionado)
if [ -f "$ENV_FILE" ] && grep -q '^SECRET_KEY=' "$ENV_FILE"; then
  echo "==> .env ja possui SECRET_KEY, mantendo o existente."
else
  SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
  ( umask 077; printf 'SECRET_KEY=%s\n' "$SECRET" > "$ENV_FILE" )
  echo "==> SECRET_KEY gravado em $ENV_FILE"
fi
chmod 600 "$ENV_FILE" 2>/dev/null || true

# 5. Diretorios persistentes (SQLite + fotos)
mkdir -p "$PROJETO/data" "$PROJETO/uploads"

# 6. WSGI ja com o login preenchido, pronto para colar no Web Tab
WSGI_DEST="$PROJETO/deploy/wsgi_config_pa.py"
sed "s/USUARIO = \"SEU_USUARIO\"/USUARIO = \"$USUARIO\"/" \
  "$PROJETO/deploy/pythonanywhere_wsgi.py" > "$WSGI_DEST"
echo "==> WSGI pronto para colar: $WSGI_DEST"

# 7. Ambiente de producao para os comandos de CLI abaixo
set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a
export FLASK_ENV=prod
export TRUSTED_HOSTS="$DOMINIO"
export DATABASE_URL="sqlite:///$PROJETO/data/japacar.db"
export UPLOAD_DIR="$PROJETO/uploads"

# 8. Usuario admin (so cria se ainda nao existir)
if python -m flask --app app:create_app usuario-listar 2>/dev/null | grep -q '^admin '; then
  echo "==> Usuario 'admin' ja existe, nao recriado."
else
  ADMIN_SENHA="$(python -c 'import secrets; print(secrets.token_urlsafe(18))')"
  python -m flask --app app:create_app usuario-criar \
    --login admin --nome Administrador --perfil ADMIN --senha "$ADMIN_SENHA"
  echo
  echo "############################################################"
  echo "#  LOGIN : admin"
  echo "#  SENHA : $ADMIN_SENHA"
  echo "#  (troque depois com: flask usuario-senha admin)"
  echo "############################################################"
fi

cat <<EOF

==> Pronto. Faltam so os cliques no Web Tab (Add a new web app -> Manual
    configuration -> Python 3.12):

    1) Virtualenv: $VENV

    2) Static files (URL -> Directory):
         /static/  ->  $PROJETO/app/static/
         /css/     ->  $PROJETO/app/static/css/
         /js/      ->  $PROJETO/app/static/js/
         /img/     ->  $PROJETO/app/static/img/
       (NAO mapeie /uploads/)

    3) WSGI configuration file: abra o link, apague o exemplo e cole o
       conteudo de: $WSGI_DEST

    4) Clique em Reload e acesse: https://$DOMINIO
EOF
