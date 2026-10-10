# JAPACAR — Sistema de Gestão para Oficina Mecânica

Sistema web completo para gestão de uma oficina mecânica: cadastro de clientes e veículos,
checklist de entrada, painel de serviços (atendimentos), orçamentos com emissão de PDF,
recebimentos (inclusive **parcelamento**), despesas, relatório de orçamentos e dashboard financeiro.

> **Nota de migração:** o JAPACAR foi originalmente desenvolvido em Java/Spring Boot e foi
> reescrito em **Python/Flask**. Todo o código-fonte Java, o `pom.xml` e os wrappers do Maven
> (`mvnw`, `mvnw.cmd`, `.mvn/`) foram removidos do repositório. A aplicação atual é 100% Python.

---

## Índice

1. [Visão geral](#visão-geral)
2. [Stack e arquitetura](#stack-e-arquitetura)
3. [Estrutura de pastas](#estrutura-de-pastas)
4. [Modelo de dados](#modelo-de-dados)
5. [Fluxos de negócio](#fluxos-de-negócio)
6. [Rotas (endpoints)](#rotas-endpoints)
7. [Configuração e variáveis de ambiente](#configuração-e-variáveis-de-ambiente)
8. [Executando localmente](#executando-localmente)
9. [Testes](#testes)
10. [Segurança](#segurança)
11. [Criptografia do backup](#criptografia-do-backup)
12. [Implantação em produção (Docker + Caddy)](#implantação-em-produção-docker--caddy)
13. [Implantação gratuita no PythonAnywhere](#implantação-gratuita-no-pythonanywhere)
14. [Backup e restauração](#backup-e-restauração)
14. [Usuários](#usuários)
15. [Changelog recente](#changelog-recente)
16. [Licença](#licença)

---

## Visão geral

O JAPACAR organiza o trabalho da oficina em um fluxo simples:

```
Cliente → Veículo → Checklist de entrada → Atendimento (serviço) → Orçamento → Recebimento/parcelas → Relatórios
```

Módulos disponíveis:

| Módulo | Descrição |
| --- | --- |
| **Dashboard** | Indicadores do mês (receitas, despesas, saldo), serviços em andamento, despesas por categoria e gráfico de barras dos últimos 6 meses. |
| **Clientes** | Cadastro com CPF, telefone, e-mail e endereço; busca por nome ou CPF; CPF único. |
| **Veículos** | Cadastro vinculado ao cliente; busca por placa ou modelo; placa única. |
| **Checklists** | Checklist de entrada do veículo com quilometragem, combustível, condições de lataria, observações e fotos. Ao salvar, gera automaticamente um atendimento. |
| **Serviços (atendimentos)** | Painel com status *Em andamento / Concluído / Cancelado*; finalização registra data de saída e encerra orçamentos. |
| **Orçamentos** | Items de serviço, mão de obra, total calculado automaticamente, PDF impresso e **parcelamento** do valor em N vezes. |
| **Despesas** | Registro de despesas por categoria com filtros de data e categoria. |
| **Relatórios** | Relatório de orçamentos com filtros de intervalo e status + resumo de totais (peças, mão de obra, pago). |
| **Autenticação** | Login/logout com senha criptografada (bcrypt) e proteção CSRF em todos os formulários. |

---

## Stack e arquitetura

- **Python 3.12+** (testado também com 3.14)
- **Flask 3.1** + **Flask-Login** (autenticação) + **Flask-WTF** (CSRF) + **Flask-SQLAlchemy** (ORM)
- **SQLite** como banco (arquivo `japacar.db`; em produção em `/app/data/japacar.db`)
- **ReportLab** para geração do PDF do orçamento
- **Gunicorn** como servidor WSGI
- **Docker / Docker Compose** para implantação; **Caddy** como proxy reverso com HTTPS automático (Let's Encrypt)
- **pytest** para testes automatizados
- **Bootstrap 5** (vendored) para interface; CSS e JS próprios em `app/static/`

### Arquitetura em camadas

```
app/
  routes/    → Blueprints (HTTP + controle de formulário)
  services/  → Regras de negócio e persistência
  models.py  → Modelos SQLAlchemy + enums/descrições
  pdf/       → Geração de PDF (ReportLab)
  templates/ → Jinja2 (HTML)
  static/    → CSS, JS e vendor Bootstrap
  utils.py   → Helpers (moeda, data, dispositivo, página ativa)
  auth.py    → Login/logout
  context.py → Variáveis globais e enums para as templates
  config.py  → Configurações dev/prod
  cli.py     → Comando `flask seed`
```

As rotas são finas (tratam requisição e flash) e delegam a lógica aos **services** (padrão Service
Layer), o que mantém as regras de negócio testáveis e fora das views.

---

## Estrutura de pastas

```
JAPACAR/
├── app/
│   ├── routes/
│   │   ├── __init__.py        # helpers de sessão (guardar/recuperar formulário)
│   │   ├── dashboard.py
│   │   ├── clientes.py
│   │   ├── veiculos.py
│   │   ├── checklists.py
│   │   ├── atendimentos.py
│   │   ├── orcamentos.py
│   │   ├── despesas.py
│   │   └── relatorios.py
│   ├── services/
│   │   ├── cliente_service.py
│   │   ├── veiculo_service.py
│   │   ├── checklist_service.py
│   │   ├── atendimento_service.py
│   │   ├── orcamento_service.py
│   │   ├── despesa_service.py
│   │   ├── dashboard_service.py
│   │   └── file_storage_service.py
│   ├── pdf/
│   │   └── orcamento_pdf.py   # PDF do orçamento (com plano de parcelas)
│   ├── templates/
│   │   ├── fragments/         # nav, head, header, alerts, scripts
│   │   ├── clientes/, veiculos/, checklists/, atendimentos/,
│   │   ├── orcamentos/, despesas/, relatorios/
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   └── erro_csrf.html
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/app.js
│   │   └── vendor/bootstrap/
│   ├── __init__.py            # create_app (app factory) e registro de rotas/erros
│   ├── auth.py
│   ├── cli.py                 # seed de usuários
│   ├── config.py
│   ├── context.py
│   ├── extensions.py          # db, login_manager, csrf
│   ├── models.py
│   └── utils.py
├── scripts/
│   ├── provision.sh           # provisiona a VPS (Docker, Caddy, cron de backup)
│   ├── gerar-chave-backup.sh  # gera o par de chaves age (roda no SEU computador)
│   ├── backup.sh              # backup cifrado (envia por e-mail a cada 14 dias)
│   ├── restore.sh             # decifra e restaura um backup
│   └── send_backup.py         # envia o .tar.gz.age por e-mail (SMTP Gmail)
├── deploy/
│   └── pythonanywhere_wsgi.py # WSGI do PythonAnywhere (deploy gratuito)
├── tests/
│   ├── conftest.py            # fixtures do pytest
│   ├── seed_base.py           # dataset mínimo para testes
│   ├── test_app.py            # suíte de testes
│   └── e2e_browser.py         # roteiro de smoke test em navegador
├── backups/                   # backups gerados localmente (gitignored)
├── uploads/                   # fotos dos checklists (gitignored)
├── Dockerfile
├── docker-compose.yml
├── Caddyfile.template
├── gunicorn.conf.py
├── requirements.txt
├── run.py
└── README.md
```

---

## Modelo de dados

O banco SQLite usa colunas de data/hora em **epoch-milliseconds (inteiro)** para compatibilidade
com dados legados. Os tipos `EpochMsDateTime` e `EpochMsDate` em `app/models.py` cuidam da conversão.

### Tabelas

| Tabela | Descrição | Campos principais |
| --- | --- | --- |
| `usuario` | Usuários do sistema | nome, login (único), senha (bcrypt), perfil, ativo |
| `cliente` | Clientes da oficina | nome, cpf (único), telefone, email, endereco, ativo |
| `veiculo` | Veículos dos clientes | placa (única), modelo, marca, ano, cor, cliente_id |
| `checklist_entrada` | Checklist de entrada | veiculo_id, data_entrada, quilometragem, nivel_combustivel, condicoes_lataria, observacoes, responsavel |
| `foto_checklist` | Fotos do checklist | checklist_id, caminho_arquivo, descricao |
| `atendimento` | Serviços em andamento | veiculo_id, checklist_entrada_id, data_entrada, data_saida, status, mecanico_responsavel, conferente, observacoes |
| `orcamento` | Orçamentos por atendimento | atendimento_id, data_criacao, valor_mao_de_obra, valor_pecas, valor_total, status, status_pagamento, forma_pagamento, data_pagamento, valor_pago, observacoes |
| `item_servico` | Itens do orçamento | orcamento_id, descricao, peca_id, quantidade, valor_unitario |
| `parcela` | **Parcelas do orçamento** | orcamento_id, numero, total_parcelas, valor, vencimento, status_pagamento, forma_pagamento, valor_pago, data_pagamento, observacoes |
| `peca` | Peças (tabela legada, sem tela) | codigo, nome, descricao, preco_compra, preco_venda, estoque |
| `despesa` | Despesas da oficina | descricao, valor, data, categoria, observacoes |

### Enums (dicionários de descrição em `app/models.py`)

- **Status de atendimento:** `EM_ANDAMENTO`, `CONCLUIDO`, `CANCELADO`
- **Status de orçamento:** `PENDENTE`, `APROVADO`, `REJEITADO`, `CONCLUIDO`, `INATIVO`
- **Status de pagamento:** `PENDENTE`, `PAGO`
- **Forma de pagamento:** `DINHEIRO`, `PIX`, `CARTAO_DEBITO`, `CARTAO_CREDITO`, `TRANSFERENCIA`, `BOLETO`, `OUTROS`
- **Nível de combustível:** `CHEIO`, `TRES_QUARTOS`, `METADE`, `UM_QUARTO`, `RESERVA`, `VAZIO`
- **Categoria de despesa:** `ALUGUEL`, `FUNCIONARIOS`, `MATERIAIS`, `PRODUTOS`, `SERVICOS`, `ENERGIA`, `AGUA`, `TELEFONE`, `IMPOSTOS`, `OUTROS`
- **Perfil de usuário:** `ADMIN`, `MECANICO`, `ATENDENTE`

> **Importante:** como o banco usa `db.create_all()` no startup, tabelas novas (ex.: `parcela`)
> são criadas automaticamente sem migração manual.

---

## Fluxos de negócio

1. **Entrada do veículo (Checklist)**
   - Cadastre o cliente → cadastre o veículo → abra um **Checklist de entrada** (`/checklists/nova`)
     com fotos, quilometragem, nível de combustível e condições.
   - Ao salvar, o sistema **cria automaticamente um atendimento** `EM_ANDAMENTO`.

2. **Serviço (Atendimento)**
   - O painel `/atendimentos` lista os serviços. Você pode editar o veículo, mecânico responsável,
     conferente e observações.
   - Em **Finalizar serviço** (`/atendimentos/<id>/finalizar`) você registra os recebimentos dos
     orçamentos e encerra o atendimento.

3. **Orçamento**
   - Criado a partir do atendimento (`/orcamentos/novo?atendimentoId=x`): itens + mão de obra,
     total calculado automaticamente.
   - Gera **PDF** do orçamento com dados do cliente, veículo, serviço, itens, totais e parcelas.

4. **Recebimento (pagamento)**
   - À vista: marque o orçamento como `Pago`, informe forma/valor/data.
   - **Parcelado:** clique em *Gerar parcelas* (2 a 12x). O sistema divide o valor total em parcelas
     mensais (a última absorve o arredondamento). O pagamento passa a ser registrado **por parcela**;
     o total recebido (`valor_pago`) e o status do orçamento (`PENDENTE`/`PAGO`) são atualizados
     automaticamente conforme as parcelas são quitadas.

5. **Financeiro**
   - Despesas com categoria e filtros; relatório de orçamentos; dashboard resumindo receitas × despesas.

---

## Rotas (endpoints)

| Rota | Método | Descrição |
| --- | --- | --- |
| `/login` | GET/POST | Página e ação de login |
| `/logout` | POST | Encerra a sessão |
| `/` | GET | Dashboard |
| `/clientes` | GET | Lista de clientes |
| `/clientes/novo`, `/clientes/<id>/editar` | GET | Formulários |
| `/clientes/salvar` | POST | Salva cliente |
| `/clientes/<id>/inativar` | POST | Inativa cliente |
| `/veiculos` | GET | Lista de veículos |
| `/veiculos/novo`, `/veiculos/<id>/editar` | GET | Formulários |
| `/veiculos/salvar` | POST | Salva veículo |
| `/veiculos/<id>/remover` | POST | Remove (bloqueado se houver atendimentos) |
| `/checklists` | GET | Lista de checklists |
| `/checklists/nova`, `/checklists/<id>`, `/checklists/<id>/editar` | GET | Lista/detalhe/formulário |
| `/checklists/salvar` | POST | Salva checklist (cria atendimento) |
| `/checklists/foto/<foto_id>/remover` | POST | Remove foto |
| `/atendimentos` | GET | Painel de serviços |
| `/atendimentos/<id>`, `/atendimentos/<id>/editar` | GET | Detalhe/formulário |
| `/atendimentos/<id>/salvar` | POST | Atualiza atendimento |
| `/atendimentos/<id>/finalizar` | GET/POST | Tela e ação de finalização |
| `/atendimentos/<id>/pagamentos` | POST | Registra pagamentos (à vista e parcelas) |
| `/atendimentos/<id>/inativar` | POST | Cancela atendimento |
| `/orcamentos` | GET | Lista de orçamentos |
| `/orcamentos/novo`, `/orcamentos/<id>/editar` | GET | Formulários |
| `/orcamentos/salvar` | POST | Salva orçamento |
| `/orcamentos/<id>/parcelar` | POST | Gera plano de parcelas |
| `/orcamentos/<id>/inativar` | POST | Inativa orçamento |
| `/orcamentos/<id>/pdf` | GET | Baixa PDF do orçamento |
| `/despesas`, `/despesas/nova`, `/despesas/<id>/editar` | GET | Lista/formulários |
| `/despesas/salvar`, `/despesas/<id>/remover` | POST | Salva/remove despesa |
| `/relatorios/orcamentos` | GET | Relatório de orçamentos |
| `/css/<arquivo>`, `/js/<arquivo>`, `/img/<arquivo>` | GET | Estáticos |
| `/uploads/<arquivo>` | GET | Fotos enviadas |

---

## Configuração e variáveis de ambiente

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `FLASK_ENV` | `dev` | `dev` ou `prod` |
| `SECRET_KEY` | aleatória por processo (dev) | Chave de assinatura de sessão e CSRF. **Obrigatória em produção**: sem ela o app não sobe. |
| `APP_DOMAIN` / `TRUSTED_HOSTS` | vazio (dev) | Host(s) público(s) aceitos no header `Host`. **Obrigatório em produção** (vem do `APP_DOMAIN`, ex.: `japacar.duckdns.org`); sem ele o app recusa subir para não aceitar Host forjado. |
| `DATABASE_URL` | `sqlite:///<projeto>/japacar.db` (dev) / `sqlite:////app/data/japacar.db` (prod) | URI do banco |
| `UPLOAD_DIR` | `./uploads` (dev) / `/app/data/uploads` (prod) | Pasta de fotos |
| `TZ` | `America/Sao_Paulo` | Fuso horário |
| `SEED_ON_STARTUP` | `0` | Cria usuários padrão no startup. **Proibido em produção.** |
| `RATELIMIT_LOGIN` | `5 per 10 minutes` | Tentativas de login por IP + usuário |
| `PORT` | `8080` | Porta do `run.py` |
| `BACKUP_RECIPIENT` | — (provision.sh) | Chave pública `age1...` usada para cifrar o backup. **Lida de `.backup-recipient`, não do ambiente em tempo de execução** |

Configurações fixas: `MAX_CONTENT_LENGTH` (50 MB) e `UPLOAD_MAX_FILE_SIZE` (10 MB).

Em desenvolvimento, sem `SECRET_KEY` no ambiente, a chave é gerada aleatoriamente a cada
processo. A consequência é perder a sessão a cada reinício do servidor — preço justo para não
haver um segredo adivinhável guardado no repositório.

---

## Executando localmente

Pré-requisitos: Python 3.12+ e `pip`.

```bash
# 1. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt
# 3. Rodar (cria o banco; usuários são criados por comando, não automaticamente)
python run.py

# ou
flask --app run.py run --debug

# 4. Acessar
# http://localhost:8080
```

Criar usuários explicitamente:

```bash
# o comando recebe senha por prompt, sem eco no terminal e sem histórico
flask --app run.py usuario-criar --login admin --perfil ADMIN

# conferir quem existe e trocar uma senha
flask --app run.py usuario-listar
flask --app run.py usuario-senha --login admin
```

Não existe mais `admin/admin123` criado no boot. Um usuário padrão que já vem pronto é o caminho
mais curto para alguém tomar conta do sistema: em produção o boot é recusado se
`SEED_ON_STARTUP` estiver ligado.

---

## Testes

A suíte usa um banco em disco (cópia de `japacar.db`) e é idempotente (o fixture `seed_dados_base`
só popula dados se não existirem clientes).

```bash
source .venv/bin/activate
pytest -q
```

Cobertura atual: autenticação, páginas autenticadas, CRUD de clientes/veículos/despesas,
edição de orçamento com recálculo de totais, **geração de parcelas e pagamento por parcela**,
finalização de serviço, relatórios, PDF e regras de exclusão (veículo com atendimento).

Há também um roteiro de smoke test em navegador em `tests/e2e_browser.py`.

A suíte de segurança vive em `tests/test_security.py` (HTTP, com a configuração `prod`) e
`tests/test_security_static.py` (compose, requirements, configuração). Ela mede o que roda em
produção: cookie `Secure`, CSP, HSTS, uploads por allowlist com conferência de magic bytes, RBAC,
rate limit de login, CSRF e ausência de segredo padrão no repositório.

---

## Segurança

O que está implementado e por quê:

| Controle | Motivo |
| --- | --- |
| RBAC no servidor (`app/security.py`) | Menu escondido não é controle de acesso; a rota precisa recusar |
| Rate limit de login (Flask-Limiter, IP + usuário) | Trava tentativa de adivinhação sem atrapalhar o operador legítimo. Roda em **um único processo** (`gthread` com threads): com vários workers o contador em memória seria multiplicado e o limite viraria ficção |
| `TRUSTED_HOSTS` (Host header) | Sem lista de hosts confiáveis, um `Host` forjado envenena links/redirecionamentos e cache; produção recusa subir sem `APP_DOMAIN` |
| Valores de pagamento limitados a `(0, total]` | Impede que um valor digitado a mais (ou negativo) infle a receita e o saldo do dashboard |
| Parcelamento limitado a 12x no servidor | O limite não pode depender só do `max` do input HTML |
| CSRF em todo POST | Impede que um site externo acione uma escrita com a sessão do operador |
| Cookie `HttpOnly` + `Secure` + `SameSite=Lax` | Script não lê o cookie; cookie não viaja em HTTP nem em navegação cruzada |
| `session.clear()` antes do login | Anti session-fixing: cookie plantado não sobrevive ao login |
| CSP, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy` | XSS, clickjacking e vazamento de referer |
| HSTS em conexão segura | Trava o downgrade para HTTP |
| Upload: allowlist de extensão **e** magic bytes | Foto renomeada para `.jpg` não vira documento executável |
| `/uploads/` exige sessão e responde como anexo | Fotos de lataria e interior não são públicas |
| Nome de arquivo gerado no servidor (UUID) | Elimina traversal e colisão de nome |
| `SECRET_KEY` obrigatória em produção | Conhecer a chave permite forjar sessão sem senha |
| Senhas só como bcrypt | Vazamento do banco não entrega login pronto |
| Sem usuário padrão no boot | `admin/admin123` é o caminho mais curto para uma tomada de conta |

Verificação antes de publicar:

```bash
pytest -q                                   # funcional + segurança
pip-audit                                  # dependências com CVE conhecida
bandit -r app                              # padrões inseguros no código
```

Os backups são **criptografados com age antes do envio**, com a chave privada fora do servidor
(ver seção "Criptografia do backup").

---

## Criptografia do backup

O backup é cifrado com **[age](https://age-encryption.org)** (Curves25519 + ChaCha20-Poly1305)
antes de sair do servidor. Quem receber o arquivo, inclusive quem comprometer a caixa de e-mail,
vê apenas bytes sem sentido; o conteúdo só abre com a chave privada.

A chave privada **não fica no servidor** — é essa a condição para o backup valer alguma coisa. Um
arquivo guardado junto com a chave que o abre é apenas mais um arquivo no mesmo disco.

O caminho do script é *fail-closed*: sem chave pública configurada, o backup aborta e nada é
enviado. Não existe caminho em que o banco saia em claro por acidente.

#### Configurar (uma vez, no seu computador)

```bash
./scripts/gerar-chave-backup.sh
```

O script imprime a chave **privada** (guarde em local seguro) e a **pública** (`age1...`).
Guarde a privada fora do servidor: pendrive, gerenciador de senhas ou papel em cofre. Sem ela os
backups existentes são definitivamente ilegíveis.

Depois de copiar a chave privada, **remova o arquivo do computador**. Ela foi escrita em um
arquivo temporário que o script apaga, mas enquanto estiver lá em `/tmp`, qualquer processo local
consegue lê-la — e uma chave privada no disco da máquina de desenvolvimento não protege nada
quando a VPS some.

Gravar a pública no servidor:

```bash
echo 'age1...' | sudo tee /opt/japacar/scripts/.backup-recipient
sudo chmod 600 /opt/japacar/scripts/.backup-recipient
```

Ou no provisionamento, de uma vez:

```bash
BACKUP_RECIPIENT='age1...' ./scripts/provision.sh
```

O `provision.sh` instala `age` e falha se não conseguir — assim o problema aparece no deploy, não
14 dias depois na primeira execução do cron.

#### Verificar que está funcionando

```bash
sudo /opt/japacar/scripts/backup.sh
ls -1 /opt/japacar/backups/          # só .tar.gz.age, nenhum .tar.gz
sudo grep -c "age-encryption.org" /opt/japacar/backups/*.age   # 1
```

Um backup em claro é um arquivo `.tar.gz`. Se aparecer algum, o processo não está cifrando.

#### O que a criptografia protege — e o que não protege

| | |
| --- | --- |
| **Protege** | InterCEPtação da mensagem; acesso à caixa de entrada do Gmail; vazamento do diretório de backups; alguém que leia o disco da VPS sem a chave |
| **Não protege** | Quem compromise a VPS pode substituir o app e capturar a senha na próxima digitação. Isso exige proteção do servidor, não do backup |
| **Não protege** | Perda da chave privada: os backups param de ser recuperáveis. É por isso que ela precisa de cópia |

#### Rotina

A rotação mantém os 4 backups mais recentes, a cada 14 dias. Backups em claro de execuções
anteriores (anteriores à criptografia) são removidos automaticamente.

## Implantação em produção (Docker + Caddy)

O projeto entrega a imagem Docker com **Gunicorn** e, no `docker-compose.yml`, um **Caddy** como
proxy reverso que emite HTTPS automático (Let's Encrypt) para o domínio.

### 1. Provisionar a VPS

O repositório precisa estar em `/opt/japacar` **antes** do provisionamento: o script usa esse
diretório como base e roda o `docker compose build` a partir dele.

```bash
cd /opt/japacar/scripts
APP_DOMAIN=japacar.duckdns.org \
sudo ./provision.sh
```

O script instala Docker, cria os diretórios persistentes, gera o `Caddyfile` a partir do template,
sobe os containers, instala o `age` e endurece o SSH. Em seguida, crie o primeiro usuário
(veja a seção [Usuários](#usuários)) — não existe admin/admin123.

Para ativar também o **backup por e-mail**, informe as três variáveis de credenciais na mesma
execução:

```bash
APP_DOMAIN=japacar.duckdns.org \
GMAIL_APP_PASSWORD=xxxx \
BACKUP_FROM=x@gmail.com \
BACKUP_TO=x@gmail.com \
BACKUP_RECIPIENT='age1...' \
sudo ./provision.sh
```

Sem elas, o app sobe normalmente e o script avisa que o backup por e-mail ficou desativado: as
credenciais não são gravadas e o cron não é agendado. Nada de banco sai do servidor nesse estado —
o `backup.sh` aborta antes de coletar dados se a chave `age` faltar. Para ativar depois, basta
definir as variáveis e rodar o `provision.sh` novamente.

`BACKUP_RECIPIENT` é a chave **pública** vinda do `gerar-chave-backup.sh` (ver seção
"Criptografia do backup"). Sem ela o provisionamento avisa e o backup não sai.

### 2. Atualizar uma versão já provisionada

O código vem do GitHub, então a atualização é um `pull` seguido de um rebuild **no servidor**:

```bash
cd /opt/japacar
git pull --ff-only
docker compose build
docker compose up -d --remove-orphans
docker compose ps
```

O `SECRET_KEY` já está em `/opt/japacar/.env` (gerada no primeiro provisionamento, permissão 600)
e **não** deve ser trocada a cada update: mudá-la invalida as sessões de quem estiver logado. Se
perdeu o arquivo, regenere com
`python3 -c "import secrets; print(secrets.token_urlsafe(64))"` e grave em `.env`.

> **Por que o build fica no servidor:** compilar a imagem local consome RAM da máquina de
> desenvolvimento. Com 8 GB e o editor aberto, o build derruba o ambiente de trabalho. Na VPS o
> build roda com folga e as wheels das dependências existem para ARM — nada é compilado do zero.

Estrutura em produção:

```
/opt/japacar/
├── Caddyfile            # gerado pelo provision.sh
├── docker-compose.yml
├── data/                # volume persistente (banco + uploads)
│   ├── japacar.db
│   └── uploads/
├── backups/             # backups gerados (.tar.gz.age, já cifrados)
└── scripts/
    ├── .backup-credentials   # credenciais do e-mail (permissão 600)
    ├── .backup-recipient     # chave PÚBLICA age de destino (permissão 600)
    ├── backup.sh
    ├── restore.sh
    └── send_backup.py
```

Note que o servidor guarda **apenas a chave pública**. A privada fica com você; se ela for
versionada junto com os backups, a criptografia deixa de proteger o que quer que seja.

---

## Implantação gratuita no PythonAnywhere

Alternativa **sem cartão de crédito** para o Docker + Caddy: o PythonAnywhere hospeda o app Flask
com **disco persistente** (SQLite e fotos continuam lá entre reinícios) e HTTPS no subdomínio
`SEU_USUARIO.pythonanywhere.com`. Como o plano gratuito roda **um único worker**, o rate limit de
login em memória funciona corretamente — o mesmo motivo pelo qual o Gunicorn usa 1 processo.

Limites do plano gratuito (importantes):

| Limite | Valor | Consequência |
| --- | --- | --- |
| CPU | **100 CPU-segundos por dia** | É o limite mais apertado. O login usa bcrypt (~0,2 s de CPU cada); evite scripts de teste em rajada. Se estourar, o app responde erro até o dia seguinte. |
| Disco | 512 MB | Suficiente para banco + fotos + código; cuidado com muitos uploads grandes. |
| Web app | 1 app, 1 worker | Sem processos paralelos. |
| Expiração | ~1 mês de inatividade | **Entre no painel e clique em "Run until 3 months from today"** de tempos em tempos, senão o web app é desativado. |
| Domínio | Só `SEU_USUARIO.pythonanywhere.com` | Sem domínio próprio no plano gratuito. |

O repositório inclui `deploy/pythonanywhere_wsgi.py`, que já configura `FLASK_ENV=prod`,
`TRUSTED_HOSTS`, `DATABASE_URL` e `UPLOAD_DIR`, e lê o `SECRET_KEY` de um `.env` privado.

### 1. Conta e código

Crie a conta gratuita e abra um **Bash console**:

```bash
# código no disco persistente
git clone https://github.com/Inaciobovo/JapaCar.git ~/JapaCar
cd ~/JapaCar

# ambiente virtual Python 3.12 (disponível nas contas novas)
mkvirtualenv --python=/usr/bin/python3.12 japacar
pip install -r requirements.txt
```

Gere a chave e crie o `.env` (permissão restrita, conteúdo **não** vai para o git):

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
umask 077
printf 'SECRET_KEY=%s\n' 'COLE_A_CHAVE_GERADA_AQUI' > ~/JapaCar/.env
```

### 2. Web app

No **Web Tab** → *Add a new web app* → **Manual configuration** → **Python 3.12**:

1. **Virtualenv**: `/home/SEU_USUARIO/.virtualenvs/japacar`.
2. **Static files** (desvia os estáticos do Flask, economizando CPU):

   | URL | Directory |
   | --- | --- |
   | `/static/` | `/home/SEU_USUARIO/JapaCar/app/static/` |
   | `/css/` | `/home/SEU_USUARIO/JapaCar/app/static/css/` |
   | `/js/` | `/home/SEU_USUARIO/JapaCar/app/static/js/` |
   | `/img/` | `/home/SEU_USUARIO/JapaCar/app/static/img/` |

3. **WSGI configuration file** (link no topo do Web Tab): apague o exemplo e cole o conteúdo de
   `deploy/pythonanywhere_wsgi.py`, trocando `USUARIO = "SEU_USUARIO"` pelo seu login.
4. Clique em **Reload**.

> Não mapeie `/uploads/`: essas fotos passam pelo Flask para exigir login. Mapear o diretório
> `uploads/` como estático tornaria as fotos de lataria e interior **públicas**.

### 3. Primeiro usuário

No Bash console (com o virtualenv ativo e o `.env` já criado, o WSGI cuida do ambiente do site;
para o comando abaixo exporte as variáveis):

```bash
cd ~/JapaCar && workon japacar
set -a; . ./.env; set +a
export FLASK_ENV=prod
export TRUSTED_HOSTS=SEU_USUARIO.pythonanywhere.com
export DATABASE_URL="sqlite:///$HOME/JapaCar/data/japacar.db"
flask --app app:create_app usuario-criar --login admin --perfil ADMIN
```

Acesse `https://SEU_USUARIO.pythonanywhere.com` e faça login.

### 4. Atualizar a versão

```bash
cd ~/JapaCar && git pull --ff-only && workon japacar && pip install -r requirements.txt
```

Depois clique em **Reload** no Web Tab. O `SECRET_KEY` no `.env` **não** deve mudar: trocá-lo
invalida as sessões ativas.

---

## Backup e restauração

### Backup automático

`scripts/backup.sh` (agendado via cron pelo `provision.sh`, todo dia às 06:14):

- Gera cópia **consistente** do banco com `sqlite3 .backup` (o app continua no ar).
- Empacota banco + fotos.
- **Cifra com age** e só então envia por e-mail (`.tar.gz.age`).
- Rodada só a cada **14 dias** (controlado por `.last_backup`) e mantém os **4 backups mais recentes**.
- O tar.gz em claro é apagado assim que a cifragem termina; se a cifragem falhar, nada é enviado.

> **O cron só é agendado se o `provision.sh` tiver sido executado com as credenciais de e-mail.**
> Se a instalação foi feita sem elas, o backup automático **não está rodando** — confirme com
> `sudo crontab -l`. Para ativar, rode o `provision.sh` de novo com as três variáveis e a chave
> pública (veja [Implantação em produção](#implantação-em-produção-docker--caddy)). Enquanto o
> backup não estiver configurado, não existe cópia dos dados: um `rm` acidental ou uma perda da
> VPS significa perder o banco sem volta.

### Backup manual

```bash
sudo ./scripts/backup.sh
```

### Restauração

```bash
# o arquivo baixado do e-mail é .tar.gz.age
BACKUP_KEY=~/caminho/da-chave-privada.txt \
  sudo -E ./scripts/restore.sh ./japacar_backup_20260115_061400.tar.gz.age
```

Sem `BACKUP_KEY`, o script procura a chave em `~/.config/japacar/backup-key.txt` e, se não achar,
pede que você cole o conteúdo da chave privada no terminal (sem eco na tela e sem histórico).

O `restore.sh` confere a assinatura age, valida a integridade do banco **antes** de sobrescrever
qualquer coisa, e apaga o staging decifrado ao sair. Se a chave estiver errada ou o backup
corrompido, ele para antes de tocar no banco em produção.

---

## Usuários

Nenhum usuário é criado automaticamente. Use `flask usuario-criar --login <login> --perfil <perfil>`;
a senha é digitada em prompt e armazenada só como hash bcrypt.

| Perfil | Acesso |
| --- | --- |
| `ADMIN` | Tudo, inclusive dashboard, despesas e relatórios |
| `MECANICO` | Fluxo operacional: clientes, veículos, checklists, atendimentos, orçamentos e PDF |
| `ATENDENTE` | Previsto no modelo; não é criado pelo seed |

O perfil `MECANICO` **não** acessa dashboard, despesas nem relatórios: são visões consolidadas de
dinheiro da oficina. O bloqueio vale nas rotas, não só no menu, então a URL direta também é
recusada com 403.

### Trocar uma senha

```bash
flask --app run.py usuario-senha --login admin
```

---

## Changelog recente

- **v1.5** — **Deploy gratuito no PythonAnywhere**: artefato `deploy/pythonanywhere_wsgi.py`
  (configura produção, lê `SECRET_KEY` de `.env` privado e usa disco persistente) e passo a passo
  no README. Sem alteração na lógica do app; alternativa sem cartão ao Docker + Caddy.
- **v1.4** — **Hardening de deploy**: `TRUSTED_HOSTS` obrigatório em produção (anti Host
  header injection), Gunicorn em um único processo `gthread` para o rate limit de login valer de
  fato, valores de pagamento limitados a `(0, total]` e parcelamento com teto de 12x no servidor,
  categoria de despesa obrigatória (fim do 500), placa única no banco, SQLite em WAL com
  `busy_timeout`/foreign keys, CSP sem CDN externo e remoção de código de RBAC morto.
- **v1.3** — **Backup criptografado com age**: o pacote é cifrado antes de sair do servidor, com a
  chave privada fora da VPS e apenas a pública no servidor. Envio em texto claro deixou de existir
  (o risco estava documentado desde a v1.2). Hardening: `SECRET_KEY` externa obrigatória em
  produção, seed desativada, cookie `Secure`, rate limit de login corrigido, `MECANICO` sem acesso
  ao financeiro, upload com allowlist e magic bytes, `ProxyFix` restrito à rede do proxy e service
  worker removido.
- **v1.1** — Remoção completa do código Java/Spring Boot; migração consolidada para Flask.
- **v1.2** — **Parcelamento de orçamentos**: modelo `Parcela`, geração de parcelas na finalização do
  serviço, pagamento por parcela, sincronização automática de `valor_pago`/status e plano de parcelas
  no PDF. Gráfico de barras (6 meses) no dashboard. Página amigável para erro CSRF.
- **v1.0** — Porte de Spring Boot → Flask (todos os módulos funcionais).

---

## Licença

Projeto desenvolvido pela **BovoTech** para uso comercial interno da oficina **JAPACAR**.
A distribuição e a utilização estão sujeitas aos termos do contrato de prestação de serviços
(ver `CONTRATO_JAPACAR.md`).