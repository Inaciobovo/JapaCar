#!/usr/bin/env bash
# Restaura um backup CRIPTOGRAFADO do JAPACAR (japacar_backup_*.tar.gz.age).
# Uso (como root): ./restore.sh /caminho/para/backup.tar.gz.age
#
# A chave privada NAO esta no servidor — e essa e a razao do backup valer algo.
# Apos baixar o .age do e-mail, aponte a chave que voce guardou:
#
#   BACKUP_KEY=/caminho/para/chave.txt ./restore.sh backup.tar.gz.age
#
# Se BACKUP_KEY nao vier, o script procura a chave em arquivos uteis e, em
# ultimo caso, pede que voce cole o conteudo da chave no terminal (sem eco).
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "uso: $0 <arquivo.tar.gz.age>"; exit 2
fi
ARCHIVE="$1"
[[ -f "$ARCHIVE" ]] || { echo "arquivo nao encontrado: $ARCHIVE"; exit 1; }

BASE=/opt/japacar
DATA_DIR="$BASE/data"
TMP=$(mktemp -d)
# O staging e apagado ao sair, mesmo em caso de erro: o banco decifrado nao
# pode sobrar em /tmp.
trap 'shred -u "$TMP"/japacar.db 2>/dev/null || rm -f "$TMP"/japacar.db; rm -rf "$TMP"' EXIT

command -v age >/dev/null 2>&1 || { echo "ERRO: 'age' nao instalado. apt install age"; exit 1; }

# Confere que o arquivo e mesmo age antes de pedir a chave: da para validar o
# cabecalho sem decifrar nada.
head -c 4 "$ARCHIVE" | grep -q 'age' \
    || { echo "ERRO: $ARCHIVE nao parece um arquivo age (criptografado)."; exit 1; }

# --- Chave privada ------------------------------------------------------------
chave_encontrada=0
chave_arquivo="${BACKUP_KEY:-}"

if [[ -z "$chave_arquivo" ]]; then
    for candidato in \
        "$HOME/.config/japacar/backup-key.txt" \
        "$HOME/.japacar-backup-key.txt"
    do
        if [[ -s "$candidato" ]]; then
            chave_arquivo="$candidato"
            break
        fi
    done
fi

if [[ -n "$chave_arquivo" ]]; then
    [[ -f "$chave_arquivo" ]] || { echo "ERRO: chave nao encontrada: $chave_arquivo"; exit 1; }
    chave_encontrada=1
else
    echo "Cole o conteudo da chave privada age (AGE-SECRET-KEY-...)."
    echo "Nada e digitado na tela e a chave nao vai para o historico."
    read -rs chave_colada
    chave_arquivo="$TMP/age.key"
    # O arquivo temporario herda o mktemp -d: ja e 700, e o trap apaga tudo.
    printf '%s' "$chave_colada" > "$chave_arquivo"
    unset chave_colada
    chave_encontrada=1
fi

[[ "$chave_encontrada" -eq 1 ]] || { echo "ERRO: nenhuma chave informada."; exit 1; }

echo "[restore] decifrando (pode demorar: o arquivo traz o banco e as fotos)"
if ! age -d -i "$chave_arquivo" -o "$TMP/backup.tar.gz" "$ARCHIVE" 2>"$TMP/age.err"; then
    echo "ERRO: nao foi possivel decifrar. A chave nao corresponde a este backup?"
    sed 's/^/  /' "$TMP/age.err" >&2
    exit 1
fi

echo "[restore] extraindo"
tar -xzf "$TMP/backup.tar.gz" -C "$TMP"
[[ -f "$TMP/japacar.db" ]] || { echo "ERRO: o backup nao contem japacar.db"; exit 1; }

# Um backup e so util se abrir. Verificar antes de sobrescrever o banco em
# producao evita descobrir a corrupcao depois de perder os dados atuais.
echo "[restore] validando o banco do backup"
if ! sqlite3 "$TMP/japacar.db" "PRAGMA integrity_check;" | grep -q '^ok$'; then
    echo "ERRO: o banco do backup esta corrompido. Nada foi alterado."; exit 1
fi

echo "[restore] parando app"
docker compose -f "$BASE/docker-compose.yml" stop app

echo "[restore] restaurando dados"
mkdir -p "$DATA_DIR"
cp "$TMP/japacar.db" "$DATA_DIR/japacar.db"
if [[ -d "$TMP/uploads" ]]; then
    rm -rf "$DATA_DIR/uploads"
    cp -r "$TMP/uploads" "$DATA_DIR/uploads"
fi
# O app roda como uid 1001. Falhar ao ajustar o dono deixaria a restauracao
# pela metade — o banco no lugar, as fotos de fora — e o `set -e` abortaria
# aqui. Por isso avisa em vez de parar: o operador ve o aviso e ajusta o dono.
if ! chown -R 1001:1001 "$DATA_DIR/japacar.db" "$DATA_DIR/uploads" 2>/dev/null; then
    echo "[restore] AVISO: nao foi possivel ajustar o dono para 1001:1001."
    echo "[restore] Rode: chown -R 1001:1001 $DATA_DIR"
fi

echo "[restore] subindo app"
docker compose -f "$BASE/docker-compose.yml" start app

echo "[restore] concluido. Acesse o site e confira os dados."
