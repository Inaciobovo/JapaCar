# JAPACAR — Gestão de Oficina

Sistema web para gestão de oficina mecânica (clientes, veículos, checklists de entrada,
atendimentos, orçamentos e pagamentos). Aplicação **Laravel** com banco **MySQL** (produção)
ou **SQLite** (desenvolvimento).

## Requisitos

- PHP 8.2+ (testado com 8.5) com extensões `pdo`, `mbstring`, `openssl`, `tokenizer`, `xml`, `ctype`, `json`, `bcmath`, `fileinfo`
- Composer 2

## Instalação (desenvolvimento)

```sh
composer install
cp .env.example .env
php artisan key:generate
touch database/database.sqlite
php artisan migrate --seed
php artisan serve
```

Acesse `http://127.0.0.1:8000`. Usuário admin criado pelo seed:

- **login:** `admin`
- **senha:** `japacar123` (defina `ADMIN_PASSWORD` no `.env` antes do seed para alterar)

> Troque a senha do admin em produção.

## Testes e estilo

```sh
php artisan test
vendor/bin/pint
```

## Configuração

Principais variáveis em `.env`:

| Variável | Descrição |
| --- | --- |
| `APP_ENV` / `APP_DEBUG` | `production` / `false` em produção |
| `APP_URL` | URL pública da aplicação |
| `APP_TIMEZONE` | `America/Sao_Paulo` |
| `DB_CONNECTION` | `sqlite` (dev) ou `mysql` (produção) |
| `ADMIN_LOGIN` / `ADMIN_PASSWORD` | credenciais do admin criado no seed |

### Produção (MySQL)

```env
APP_ENV=production
APP_DEBUG=false
APP_URL=https://seudominio.com

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=japacar
DB_USERNAME=usuario
DB_PASSWORD=senha
```

Após configurar:

```sh
php artisan key:generate
php artisan migrate --force --seed
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

O document root do servidor deve apontar para a pasta `public/`.

## Funcionalidades

- **Login** com usuários (perfis `ADMIN` e `MECANICO`) e proteção contra força bruta (rate limit).
- **Clientes:** cadastro, edição, busca e inativação.
- **Veículos:** cadastro, edição, busca e ficha com histórico.
- **Checklists de entrada:** km, nível de combustível, condições e **fotos** (armazenadas de
  forma privada, servidas apenas para usuários autenticados).
- **Atendimentos:** abertura a partir do veículo/checklist e finalização.
- **Orçamentos:** mão de obra + itens (peças), totais automáticos e registro de pagamento
  (status pendente/parcial/pago).

## Estrutura

- `app/Http/Controllers` — controladores da aplicação
- `app/Models` — modelos Eloquent
- `config/japacar.php` — domínios (perfis, status, formas de pagamento, combustível)
- `database/migrations` — esquema do banco
- `resources/views` — Blade (Bootstrap em `public/vendor/bootstrap`)
- `routes/web.php` — rotas
