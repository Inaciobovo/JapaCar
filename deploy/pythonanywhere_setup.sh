#!/usr/bin/env bash
# Setup automatico do JAPACAR no PythonAnywhere (conta gratuita).
#
# Uso (no Bash console do PythonAnywhere):
#   bash ~/JapaCar/deploy/pythonanywhere_setup.sh
#
# Faz TUDO pelo console: virtualenv, dependencias, SECRET_KEY, diretorios
# persistentes, usuario admin e, se o token da API estiver disponivel (a
# variavel $API_TOKEN ja existe no console do PythonAnywhere), configura o
# web app inteiro via API: cria o web app, aponta o virtualenv, registra os
# arquivos estaticos, instala o WSGI e recarrega. Sem token, ele apenas
# imprime o que colar no Web Tab.
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

# 6. WSGI ja com o login preenchido
WSGI_DEST="$PROJETO/deploy/wsgi_config_pa.py"
sed "s/USUARIO = \"SEU_USUARIO\"/USUARIO = \"$USUARIO\"/" \
  "$PROJETO/deploy/pythonanywhere_wsgi.py" > "$WSGI_DEST"

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

# ---------------------------------------------------------------------------
# 9. Configuracao do web app via API (dispensa cliques no Web Tab).
# ---------------------------------------------------------------------------
api() {
  # api METHOD PATH [curl args...] -> imprime corpo e, na ultima linha, o HTTP
  local method="$1" path="$2"; shift 2
  curl -sS -w '\n%{http_code}' -X "$method" \
    -H "Authorization: Token $API_TOKEN" "$API_BASE$path" "$@" || true
}

detectar_api() {
  local base code
  for base in "https://www.pythonanywhere.com" "https://eu.pythonanywhere.com"; do
    code=$(curl -sS -o /dev/null -w '%{http_code}' \
      -H "Authorization: Token $API_TOKEN" \
      "$base/api/v0/user/$USUARIO/cpu/" 2>/dev/null || true)
    if [ "$code" = "200" ]; then API_BASE="$base"; return 0; fi
  done
  return 1
}

configurar_webapp() {
  local py_tag resp code body pair url dir
  py_tag="python$(python -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"

  echo "==> Configurando o web app via API ($API_BASE)..."

  # (a) cria o web app (manual config) se ainda nao existir
  resp="$(api POST "/api/v0/user/$USUARIO/webapps/" \
    --data-urlencode "domain_name=$DOMINIO" \
    --data-urlencode "python_version=$py_tag")"
  code="$(printf '%s\n' "$resp" | tail -n1)"; body="$(printf '%s\n' "$resp" | sed '$d')"
  case "$code" in
    200|201) echo "    [ok] web app criado ($py_tag)." ;;
    400)     echo "    [ok] web app ja existia." ;;
    *)       echo "    [!] criar web app -> HTTP $code"; printf '%s\n' "$body" ;;
  esac

  # (b) virtualenv, diretorio de codigo e HTTPS obrigatorio
  resp="$(api PATCH "/api/v0/user/$USUARIO/webapps/$DOMINIO/" \
    --data-urlencode "virtualenv_path=$VENV" \
    --data-urlencode "source_directory=$PROJETO" \
    --data-urlencode "force_https=true")"
  code="$(printf '%s\n' "$resp" | tail -n1)"
  echo "    [ok] virtualenv/source/https -> HTTP $code"

  # (c) mapeamentos de arquivos estaticos
  for pair in "/static/=$PROJETO/app/static/" "/css/=$PROJETO/app/static/css/" \
              "/js/=$PROJETO/app/static/js/" "/img/=$PROJETO/app/static/img/"; do
    url="${pair%%=*}"; dir="${pair#*=}"
    resp="$(api POST "/api/v0/user/$USUARIO/webapps/$DOMINIO/static_files/" \
      --data-urlencode "url=$url" --data-urlencode "path=$dir")"
    code="$(printf '%s\n' "$resp" | tail -n1)"
    echo "    [static] $url -> HTTP $code"
  done

  # (d) instala o arquivo WSGI (o PythonAnywhere le este arquivo)
  resp="$(api POST "/api/v0/user/$USUARIO/files/path/var/www/${USUARIO}_pythonanywhere_com_wsgi.py" \
    -F "content=@$WSGI_DEST;type=text/x-python")"
  code="$(printf '%s\n' "$resp" | tail -n1)"
  echo "    [wsgi] upload -> HTTP $code"

  # (e) recarrega o site
  resp="$(api POST "/api/v0/user/$USUARIO/webapps/$DOMINIO/reload/")"
  code="$(printf '%s\n' "$resp" | tail -n1)"
  echo "    [reload] -> HTTP $code"
}

if [ -n "${API_TOKEN:-}" ] && command -v curl >/dev/null 2>&1; then
  if detectar_api; then
    configurar_webapp
    echo
    echo "==> Pronto! Acesse: https://$DOMINIO  (login: admin)"
  else
    echo "==> Nao consegui falar com a API (token/server?). Configure pelo Web Tab:"
    manual=1
  fi
else
  echo "==> \$API_TOKEN indisponivel. Configure pelo Web Tab:"
  manual=1
fi

if [ "${manual:-0}" = "1" ]; then
  cat <<EOF

    Web Tab -> Add a new web app -> Manual configuration:

    1) Virtualenv: $VENV
    2) Static files (URL -> Directory):
         /static/  ->  $PROJETO/app/static/
         /css/     ->  $PROJETO/app/static/css/
         /js/      ->  $PROJETO/app/static/js/
         /img/     ->  $PROJETO/app/static/img/
       (NAO mapeie /uploads/)
    3) WSGI file: cole o conteudo de $WSGI_DEST
    4) Reload e acesse https://$DOMINIO
EOF
fi
