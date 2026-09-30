#!/usr/bin/env bash
# Provisiona a VPS para rodar o JAPACAR em Docker + Caddy (HTTPS Let's Encrypt).
# Uso (como root):
#   APP_DOMAIN=japacar.duckdns.org ./provision.sh
#
# Com backup por e-mail (opcional; as três variáveis abaixo podem ser omitidas
# para adiar o backup — nesse caso o app sobe sem cron de backup):
#   APP_DOMAIN=japacar.duckdns.org \
#   GMAIL_APP_PASSWORD=xxxx BACKUP_FROM=x@gmail.com BACKUP_TO=x@gmail.com \
#   BACKUP_RECIPIENT='age1...' \
#   sudo ./provision.sh
set -euo pipefail

: "${APP_DOMAIN:?APP_DOMAIN obrigatorio (ex: japacar.duckdns.org)}"

# Credenciais de e-mail do backup são opcionais (adiadas por ~1 mês).
# Quando não informadas, o backup não é configurado, mas o provisionamento
# do app continua. Isso evita que o script aborte no primeiro deploy sem a
# senha de app do Gmail.
BACKUP_OPCIONAL=1
: "${GMAIL_APP_PASSWORD:=}"
: "${BACKUP_FROM:=}"
: "${BACKUP_TO:=}"

BASE=/opt/japacar
export DEBIAN_FRONTEND=noninteractive

log() { echo "[provision] $(date -Is) $*"; }

mkdir -p "$BASE"

# O compose aborta com ${SECRET_KEY:?...} quando esta variavel falta. Gerar a
# chave aqui e persistir num arquivo com permissao 600 evita que o primeiro
# `docker compose up` falhe e evita que a chave fique no historico do shell.
if [[ -z "${SECRET_KEY:-}" && ! -s "$BASE/.env" ]]; then
    log "Gerando SECRET_KEY"
    umask 077
    printf 'SECRET_KEY=%s\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" > "$BASE/.env"
    chmod 600 "$BASE/.env"
    umask 022
    log "Chave salva em $BASE/.env (permissao 600). Guarde uma copia fora do servidor."
elif [[ -n "${SECRET_KEY:-}" ]]; then
    umask 077
    printf 'SECRET_KEY=%s\n' "$SECRET_KEY" > "$BASE/.env"
    chmod 600 "$BASE/.env"
    umask 022
else
    log "Reaproveitando a SECRET_KEY existente em $BASE/.env"
fi

log "Timezone America/Sao_Paulo"
timedatectl set-timezone America/Sao_Paulo 2>/dev/null || true

log "Pacotes base"
apt-get update -qq
apt-get install -y -qq ca-certificates curl sqlite3 cron gnupg lsb-release age >/dev/null

if ! command -v age >/dev/null 2>&1; then
    # O backup depende de 'age' para criptografar. Sem ele o script de backup
    # aborta (fail-closed) em vez de enviar o banco em claro, mas avisar aqui
    # evita descobrir o problema 14 dias depois, na primeira execucao do cron.
    echo "[provision] ERRO: 'age' nao instalado. O backup NAO sera criptografado."
    echo "[provision] Instale manualmente: apt install age"
    exit 1
fi
log "age disponivel: $(age --version)"

if ! command -v docker >/dev/null 2>&1; then
    log "Instalando Docker (get.docker.com)"
    curl -fsSL https://get.docker.com | sh
fi
if ! docker compose version >/dev/null 2>&1; then
    log "Instalando plugin docker compose"
    apt-get install -y -qq docker-compose-plugin >/dev/null
fi

if ! id -u appuser >/dev/null 2>&1; then
    useradd --system --uid 1001 --create-home appuser
fi

log "Diretorios persistentes"
install -d -o 1001 -g 1001 "$BASE/data"
install -d -o root -g root "$BASE/backups" "$BASE/scripts"
chown -R 1001:1001 "$BASE/data"

log "Gerando Caddyfile para $APP_DOMAIN"
sed "s/__DOMAIN__/$APP_DOMAIN/g" "$BASE/Caddyfile.template" > "$BASE/Caddyfile"
chmod 644 "$BASE/Caddyfile"

# Credenciais de backup (permissao 600). Gravadas apenas se as três variáveis
# foram informadas; caso contrário, o backup fica desativado com um aviso.
if [[ -n "$GMAIL_APP_PASSWORD" && -n "$BACKUP_FROM" && -n "$BACKUP_TO" ]]; then
    log "Credenciais de backup (permissao 600)"
    umask 077
    cat > "$BASE/scripts/.backup-credentials" <<EOF
GMAIL_APP_PASSWORD='$GMAIL_APP_PASSWORD'
BACKUP_FROM='$BACKUP_FROM'
BACKUP_TO='$BACKUP_TO'
EOF
    chmod 600 "$BASE/scripts/.backup-credentials"
    umask 022
else
    BACKUP_OPCIONAL=0
    log "AVISO: GMAIL_APP_PASSWORD / BACKUP_FROM / BACKUP_TO nao informadas."
    log "Backup por e-mail DESATIVADO nesta instalacao."
    log "Para ativar depois, defina as variaveis e rode provision.sh novamente."
fi

# A chave PUBLICA de destino do backup. A privada nao vem para ca: e o que
# faz o backup valer algo, ja que ela nunca fica junto dos dados.
RECIPIENT_FILE="$BASE/scripts/.backup-recipient"
if [[ -n "${BACKUP_RECIPIENT:-}" ]]; then
    umask 077
    printf '%s\n' "$BACKUP_RECIPIENT" > "$RECIPIENT_FILE"
    chmod 600 "$RECIPIENT_FILE"
    umask 022
    log "Chave publica de backup gravada em $RECIPIENT_FILE"
elif [[ "$BACKUP_OPCIONAL" -eq 1 ]]; then
    log "AVISO: BACKUP_RECIPIENT nao informado."
    log "O backup sera ABORTADO ate voce rodar scripts/gerar-chave-backup.sh"
    log "na sua maquina e gravar a chave publica em $RECIPIENT_FILE"
else
    log "Backup por e-mail desativado (sem credenciais); chave publica ignorada."
fi

log "Build da imagem e subida dos containers"
cd "$BASE"
docker compose build
docker compose up -d --remove-orphans
docker compose ps

log "Aguardando o app ficar saudavel"
ok=0
for _ in $(seq 1 30); do
    if docker compose exec -T app curl -fsS http://localhost:8080/login >/dev/null 2>&1; then
        ok=1
        break
    fi
    sleep 4
done
if [[ "$ok" -ne 1 ]]; then
    echo "[provision] AVISO: app nao respondeu ainda. Veja os logs: docker compose logs app"
    exit 1
fi

# Nao existe usuario padrao. Sem este passo o sistema sobe sem ninguem able de
# entrar, e o operador perde tempo procurando o login padrao no lugar errado.
log "Criando o usuario administrador inicial"
ADMIN_LOGIN="${ADMIN_LOGIN:-admin}"
if docker compose exec -T app flask usuario-listar 2>/dev/null | grep -q "^${ADMIN_LOGIN}\b"; then
    log "Usuario $ADMIN_LOGIN ja existe; nada a fazer"
else
    docker compose exec -T app flask usuario-criar \
        --login "$ADMIN_LOGIN" --perfil ADMIN --senha "${ADMIN_PASSWORD:-}"
fi

# O cron so e agendado quando as credenciais existem. Sem elas, nao ha envio
# possivel e agendar o backup.sh seria gerar um aviso por dia no log sem
# perspectiva de resolver — pior do que nenhum agendamento.
if [[ "$BACKUP_OPCIONAL" -eq 1 ]]; then
    log "Cron de backup (verifica diario, envia a cada 14 dias)"
    CRON_LINE="14 6 * * * $BASE/scripts/backup.sh >> /var/log/japacar-backup.log 2>&1"
    ( crontab -l 2>/dev/null | grep -v "$BASE/scripts/backup.sh" || true; echo "$CRON_LINE" ) | crontab -
else
    log "Cron de backup NAO agendado (credenciais de e-mail ausentes)."
fi

log "Endurecendo SSH (sem senha, sem root)"
sed -i -E 's/^#?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i -E 's/^#?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl restart ssh 2>/dev/null || systemctl restart sshd 2>/dev/null || true

log "Pronto! Site: https://$APP_DOMAIN"