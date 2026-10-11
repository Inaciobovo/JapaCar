#!/usr/bin/env bash
#
# Monta o pacote pronto para upload no InfinityFree.
#
# Gera: deploy/infinityfree/japacar-htdocs.zip
# Descompacte este zip DENTRO da pasta "htdocs" da sua conta.
#
# O pacote já contém:
#   - dependências de produção (vendor, sem dev)
#   - .htaccess na raiz (simula o document root = public/)
#   - .env.production.example (copie para .env e preencha)
#
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DESTINO_DIR="$RAIZ/deploy/infinityfree"
BUILD="$(mktemp -d /tmp/japacar-build.XXXXXX)"
ZIP="$DESTINO_DIR/japacar-htdocs.zip"

echo ">> Limpando $BUILD"
rm -rf "$BUILD"/*

echo ">> Copiando código-fonte (sem .git, vendor, node_modules, .env...)"
rsync -a \
  --exclude='.git/' \
  --exclude='node_modules/' \
  --exclude='vendor/' \
  --exclude='deploy/' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='database/database.sqlite' \
  --exclude='storage/app/private/uploads/' \
  --exclude='storage/logs/*' \
  --exclude='storage/framework/cache/data/*' \
  --exclude='storage/framework/sessions/*' \
  --exclude='storage/framework/views/*' \
  --exclude='tests/' \
  --exclude='phpunit.xml' \
  --exclude='.editorconfig' \
  --exclude='.npmrc' \
  --exclude='package.json' \
  --exclude='package-lock.json' \
  --exclude='vite.config.js' \
  --exclude='*.zip' \
  "$RAIZ/" "$BUILD/"

echo ">> Instalando dependências de produção"
composer install \
  --no-dev \
  --optimize-autoloader \
  --no-interaction \
  --no-progress \
  --working-dir="$BUILD"

echo ">> Ajustando .htaccess e arquivos de ambiente"
cp "$DESTINO_DIR/htdocs.htaccess" "$BUILD/.htaccess"
cp "$DESTINO_DIR/.env.production.example" "$BUILD/.env.production.example"
cp "$DESTINO_DIR/.env.production.example" "$BUILD/.env"

echo ">> Empacotando $ZIP"
rm -f "$ZIP"
( cd "$BUILD" && zip -rq "$ZIP" . )

rm -rf "$BUILD"

echo ">> Pronto: $ZIP ($(du -h "$ZIP" | cut -f1))"
