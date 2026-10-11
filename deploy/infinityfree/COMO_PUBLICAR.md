# Publicar o JAPACAR no InfinityFree (grátis)

Guia passo a passo. O InfinityFree **não tem SSH nem Composer**, então o projeto vai
pronto (com dependências) e o banco é criado importando um arquivo `.sql` pelo phpMyAdmin.

## Arquivos necessários (já gerados)

| Arquivo | Para que serve |
| --- | --- |
| `deploy/infinityfree/japacar-htdocs.zip` | O sistema completo, pronto para subir em `htdocs` |
| `deploy/infinityfree/japacar.sql` | Estrutura do banco + usuário admin (importar no phpMyAdmin) |

Para regenerar o zip após alterações no código:

```sh
bash deploy/infinityfree/build-htdocs-zip.sh
```

---

## Passo 1 — Criar o site

1. Crie a conta em <https://infinityfree.com>.
2. No painel, crie uma conta de hospedagem (**New Account**) escolhendo um subdomínio,
   por exemplo `japacar.infinityfreeapp.com`.

## Passo 2 — Criar o banco MySQL

1. No painel, abra **MySQL Databases** → **Create Database**.
2. Anote os dados gerados:

   | Campo | Exemplo |
   | --- | --- |
   | Host | `sql302.infinityfree.com` |
   | Database | `if0_12345678_japacar` |
   | Username | `if0_12345678` |
   | Password | (a que você definiu) |

## Passo 3 — Gerar a APP_KEY

No seu computador, dentro da pasta do projeto:

```sh
php artisan key:generate --show
```

Copie o valor retornado (começa com `base64:`).

## Passo 4 — Enviar os arquivos

1. Descompacte `deploy/infinityfree/japacar-htdocs.zip` no seu computador.
2. Abra o arquivo `.env` (na raiz do que foi descompactado) e preencha:

   ```env
   APP_KEY=base64:COLE_AQUI_O_VALOR_DO_PASSO_3
   APP_URL=https://SEU-SUBDOMINIO.infinityfreeapp.com

   DB_HOST=sqlXXX.infinityfree.com
   DB_DATABASE=if0_XXXXXXX_japacar
   DB_USERNAME=if0_XXXXXXX
   DB_PASSWORD=sua_senha
   ```

3. Envie **todo o conteúdo** da pasta descompactada para a pasta **`htdocs`** da sua conta,
   usando um cliente FTP (ex.: [FileZilla](https://filezilla-project.org/)) — o InfinityFree
   disponibiliza os dados de FTP no painel.

   A estrutura dentro de `htdocs` deve ficar assim:

   ```
   htdocs/
   ├── .htaccess        ← simula o document root (NÃO apague)
   ├── .env             ← credenciais (NÃO apague)
   ├── app/
   ├── bootstrap/
   ├── config/
   ├── public/
   ├── storage/
   ├── vendor/
   └── ...
   ```

## Passo 5 — Importar o banco de dados

1. No painel do InfinityFree, abra **phpMyAdmin** do banco criado.
2. Selecione o banco → aba **Importar** → **Escolher arquivo** → selecione
   `deploy/infinityfree/japacar.sql` → **Executar**.
3. Confirme que as tabelas apareceram (users, clientes, veiculos, etc.).

## Passo 6 — Permissões

As pastas `storage/` e `bootstrap/cache/` precisam ser graváveis. No InfinityFree, o PHP
roda como o próprio dono dos arquivos, então normalmente já funciona. Se der erro de
permissão, ajuste via FTP para `755` (ou `775`).

## Passo 7 — Acessar

Abra `https://SEU-SUBDOMINIO.infinityfreeapp.com` e entre com:

- **login:** `admin`
- **senha:** `japacar123`

Em seguida, troque a senha em **Senha** (no menu superior).

---

## Problemas comuns

- **Erro 500 / página branca:** edite `.env`, mude `APP_DEBUG=true` temporariamente e abra
  o site para ver o erro. Os logs ficam em `storage/logs/laravel.log`.
- **Login não persiste / "Page Expired":** confirme `APP_URL` com o endereço correto e que
  `SESSION_DRIVER=file`.
- **CSS/imagens não carregam:** verifique se o `.htaccess` da raiz está presente e se
  `mod_rewrite` está ativo (é o padrão no InfinityFree).
- **Uploads:** as fotos dos checklists ficam em `storage/app/private/uploads` e **não** são
  acessíveis diretamente pela web (servidas só para usuários logados).

## Atualizações futuras

Sem SSH, cada atualização é feita reenviando os arquivos alterados via FTP. Para mudanças
no banco, gere um novo SQL localmente com `php artisan migrate` e importe/compare pelo
phpMyAdmin.
