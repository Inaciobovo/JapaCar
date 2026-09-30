#!/usr/bin/env bash
# Backup do JAPACAR: a cada 14 dias gera tar.gz (banco consistente + fotos),
# CRIPTOGRAFA e envia por e-mail.
# Agendado via cron diario; o intervalo de 14 dias e controlado por .last_backup.
#
# O arquivo em claro nunca e enviado. Se nao houver chave publica configurada,
# o script aborta: enviar o banco com CPF e endereco de clientes em claro
# seria pior que nao ter backup.
set -euo pipefail

BASE=/opt/japacar
DATA_DIR="$BASE/data"
STAGE_DIR="$BASE/backups"
SCRIPTS_DIR="$BASE/scripts"
INTERVAL_DAYS=14
LOCK_FILE="$STAGE_DIR/.backup.lock"
LAST_FILE="$STAGE_DIR/.last_backup"
RECIPIENT_FILE="$SCRIPTS_DIR/.backup-recipient"
STAMP=$(date +%Y%m%d_%H%M%S)

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[backup] ja existe outra execucao em andamento; saindo"
    exit 0
fi

log() { echo "[backup] $(date -Is) $*"; }
die() { log "ERRO: $*"; exit 1; }

test -f "$SCRIPTS_DIR/.backup-credentials" && source "$SCRIPTS_DIR/.backup-credentials"

# --- Chave publica de destino ------------------------------------------------
# Sem isto o backup sairia em claro. Verificamos ANTES de coletar os dados,
# para nao produzir um tar.gz em claro que ninguem cifrou.
if [[ ! -s "$RECIPIENT_FILE" ]]; then
    die "sem chave publica de backup em $RECIPIENT_FILE.
Gere o par na sua maquina com scripts/gerar-chave-backup.sh e grave a chave
publica (age1...) no servidor. NADA foi enviado por e-mail."
fi
RECIPIENT=$(grep -o 'age1[a-z0-9]*' "$RECIPIENT_FILE" | head -1)
[[ -n "$RECIPIENT" ]] || die "chave publica invalida em $RECIPIENT_FILE (esperado age1...)"
# `age` falha com um erro confuso se receber mais de um argumento, e a saida
# de gerar-chave-backup.sh tem varias linhas. Passa a chave via stdin para
# nao haver como o arquivo influenciar os argumentos.
AGE_RECIPIENT="$RECIPIENT"

command -v age >/dev/null 2>&1 \
    || die "'age' nao instalado no servidor. Rode: apt install age"

# --- Intervalo ----------------------------------------------------------------
now=$(date +%s)
last=0
if [[ -f "$LAST_FILE" ]]; then
    last=$(cat "$LAST_FILE")
fi
elapsed=$(( (now - last) / 86400 ))
if (( elapsed < INTERVAL_DAYS )); then
    log "faltam $((INTERVAL_DAYS - elapsed)) dia(s) para o proximo backup"
    exit 0
fi

mkdir -p "$STAGE_DIR"
STAGE=$(mktemp -d)
# Limpa o staging inclusive em caso de erro: um tar.gz em claro esquecido em /tmp
# seria uma copia dos dados sem criptografia.
trap 'rm -rf "$STAGE"' EXIT
PLAIN="$STAGE/japacar_backup_$STAMP.tar.gz"
ARCHIVE="$STAGE_DIR/japacar_backup_$STAMP.tar.gz.age"

log "coletando banco (copia consistente, app continua no ar)"
[[ -f "$DATA_DIR/japacar.db" ]] || die "$DATA_DIR/japacar.db nao existe"
sqlite3 "$DATA_DIR/japacar.db" ".backup '$STAGE/japacar.db'"

log "empacotando banco + fotos"
tar -czf "$PLAIN" -C "$STAGE" japacar.db -C "$DATA_DIR" uploads

log "criptografando (age, chave publica: ${RECIPIENT:0:12}...)"
# age falha e nao produz saida se a chave estiver corrompida ou o destino
# invalido. O tar.gz em claro e removido logo depois, no mesmo passo.
age -r "$AGE_RECIPIENT" -o "$ARCHIVE" "$PLAIN" \
    || die "falha ao criptografar; o backup NAO foi enviado"
rm -f "$PLAIN"

# Garante que o que vai para o disco e mesmo um arquivo age: sem isto, um erro
# de script poderia deixar o tar.gz em claro com nome de .age e ser enviado.
head -c 4 "$ARCHIVE" | grep -q 'age' \
    || die "o arquivo gerado nao e um age valido; envio abortado"

log "enviando por e-mail ($ARCHIVE)"
python3 "$SCRIPTS_DIR/send_backup.py" "$ARCHIVE" \
    || die "falha no envio; o backup cifrado ficou em $ARCHIVE"

log "rotacao: mantendo apenas os 4 backups mais recentes"
ls -1t "$STAGE_DIR"/japacar_backup_*.tar.gz.age 2>/dev/null | tail -n +5 | xargs -r rm -f
# Remove tambem qualquer tar.gz em claro de execucoes antigas (antes da
# criptografia). Sem isto o risco antigo continuaria em disco para sempre.
find "$STAGE_DIR" -maxdepth 1 -name 'japacar_backup_*.tar.gz' -mtime +1 -delete 2>/dev/null || true

echo "$now" > "$LAST_FILE"
log "backup concluido e criptografado: $(basename "$ARCHIVE")"
