#!/usr/bin/env bash
# Gera o par de chaves do backup do JAPACAR.
#
# Rode na SUA máquina, não no servidor. A chave privada nunca vai para a VPS:
# é ela que decifra o backup, e um backup guardado junto com a própria chave
# não é criptografado, é só mais um arquivo no mesmo disco.
#
# Uso:
#   ./gerar-chave-backup.sh
#
# stdout recebe SOMENTE a chave pública (começa com "age1"), para poder ser
# usada direto:
#     ./gerar-chave-backup.sh > publica.txt
# Tudo o mais (inclusive a chave privada) sai em stderr, para não copiar a
# chave errada ao colar no terminal do servidor.
set -euo pipefail

if ! command -v age-keygen >/dev/null 2>&1; then
    cat >&2 <<'EOF'
ERRO: 'age' nao encontrado.

  Debian/Ubuntu: sudo apt install age
  Fedora/RHEL:   sudo dnf install age
  macOS:         brew install age
  Windows:       winget install FiloSottile.age
EOF
    exit 1
fi

OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT

age-keygen -o "$OUT/chave.txt" 2>/dev/null

echo "Guarde a chave privada em local seguro AGORA. Ela nao sera exibida de novo." >&2
echo "Se perder, os backups existentes ficam definitivamente ilegiveis." >&2
echo >&2

cat >&2 <<'EOF'
================================================================
CHAVE PRIVADA — copie para um lugar seguro e remova do computador
(o arquivo gerado contem esta chave e a publica)
================================================================
EOF
cat "$OUT/chave.txt" >&2

echo >&2
echo "================================================================" >&2
echo >&2

PUBLIC_KEY=$(grep -o 'age1[a-z0-9]*' "$OUT/chave.txt" | head -1)
[[ -n "$PUBLIC_KEY" ]] || { echo "ERRO: nao consegui extrair a chave publica." >&2; exit 1; }

cat >&2 <<EOF
No servidor, grave a chave publica (a que saiu no stdout deste script):
  echo '$PUBLIC_KEY' | sudo tee /opt/japacar/scripts/.backup-recipient
  sudo chmod 600 /opt/japacar/scripts/.backup-recipient
EOF

# stdout: somente a chave publica
echo "$PUBLIC_KEY"
