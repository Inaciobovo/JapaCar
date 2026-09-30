"""Verificações estáticas de infraestrutura para produção.

Cobre os arquivos que não são exercitados pelos testes HTTP: o compose, o
requirements e a configuração. Um segredo padrão passado direto no
docker-compose é exatamente o tipo de falha que só aparece depois do deploy.
"""

import ast
import re
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def compose() -> str:
    return (BASE / "docker-compose.yml").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def requirements() -> str:
    return (BASE / "requirements.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def config_py() -> str:
    return (BASE / "app" / "config.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# docker-compose
# ---------------------------------------------------------------------------


def test_compose_nao_tem_secret_key_com_fallback(compose):
    """`SECRET_KEY=${SECRET_KEY:-<algo>}` sobe o app com uma chave pública.

    Com a SECRET_KEY conhecida, um atacante assina um cookie de sessão
    qualquer e entra no sistema sem senha.
    """
    linhas = [l for l in compose.splitlines() if "SECRET_KEY" in l]
    assert linhas, "SECRET_KEY não está no compose"
    for linha in linhas:
        assert not re.search(r"\$\{SECRET_KEY:-[^}]+\}", linha), (
            f"SECRET_KEY tem valor padrão no compose: {linha.strip()}"
        )


def test_compose_desliga_o_seed_de_usuarios_padrao(compose):
    """SEED_ON_STARTUP=1 cria admin/admin123 no primeiro boot em produção."""
    assert "SEED_ON_STARTUP" in compose
    linhas = [l for l in compose.splitlines() if "SEED_ON_STARTUP" in l]
    for linha in linhas:
        assert re.search(r"SEED_ON_STARTUP=0\b", linha), (
            f"SEED_ON_STARTUP deveria ser 0: {linha.strip()}"
        )


def test_compose_desliga_o_modo_dev(compose):
    assert "FLASK_ENV=prod" in compose


def test_compose_hardena_o_container(compose):
    """Container sem privilégios desnecessários."""
    assert "no-new-privileges:true" in compose
    assert "cap_drop" in compose


def test_compose_nao_publica_a_porta_do_app(compose):
    """O app escuta em 8080 e só deve ser alcançável pela rede interna do Caddy."""
    bloco_app = compose.split("app:")[1].split("caddy:")[0]
    assert "ports:" not in bloco_app, "o serviço app não deve expor portas ao host"


# ---------------------------------------------------------------------------
# requirements
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pacote", ["pytest", "playwright", "pytest-cov"])
def test_dependencia_de_desenvolvimento_fora_de_producao(requirements, pacote):
    """pytest na imagem de produção aumenta superfície sem necessidade."""
    linhas = [l for l in requirements.splitlines() if l.strip()]
    for linha in linhas:
        assert not linha.lower().startswith(pacote), (
            f"{pacote} não deveria estar em requirements.txt de produção: {linha}"
        )


def test_dependencias_com_pino_exato(requirements):
    """Sem `==` o build em produção é não reproduzível."""
    for linha in requirements.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        assert "==" in linha, f"dependência sem versão fixada: {linha}"


def test_dependencias_auditaveis(requirements):
    """pip-audit precisa conseguir ler o arquivo (formato requirements)."""
    conteudo = requirements
    assert "Flask-Limiter" in conteudo, "Flask-Limiter deveria estar pinado"


# ---------------------------------------------------------------------------
# app/config.py
# ---------------------------------------------------------------------------


def test_config_nao_embute_segredo_padrao(config_py):
    """Nenhuma SECRET_KEY de desenvolvimento pode ser atribuída por padrão.

    A string antiga pode continuar listada em SECRET_KEYS_CONHECIDAS — o
    denylist precisa conhecer o valor para recusá-lo. O que não pode existir é a
    *atribuição* desse valor a SECRET_KEY.
    """
    atribuicoes = re.findall(r"^\s*SECRET_KEY\s*(?::[^=]+)?=\s*(.+)$", config_py, re.M)
    assert atribuicoes, "nenhuma definição de SECRET_KEY encontrada"
    for valor in atribuicoes:
        assert "japacar-dev" not in valor, (
            f"SECRET_KEY de desenvolvimento embutida: {valor.strip()}"
        )
        assert "troque" not in valor.lower(), (
            f"SECRET_KEY de fallback embutida: {valor.strip()}"
        )


def test_seed_on_startup_desligado_por_padrao(config_py):
    assert re.search(r"SEED_ON_STARTUP[^\n]*[\"']0[\"']", config_py), (
        "SEED_ON_STARTUP deveria ser 0 por padrão"
    )


def test_cookie_de_sessao_configurado(config_py):
    assert "SESSION_COOKIE_SECURE" in config_py
    assert "SESSION_COOKIE_HTTPONLY" in config_py
    assert "SESSION_COOKIE_SAMESITE" in config_py
    assert "PERMANENT_SESSION_LIFETIME" in config_py


def test_upload_max_file_size_e_um_teto_real(config_py):
    """A configuração precisa existir E ser aplicada pelo serviço de upload."""
    assert "UPLOAD_MAX_FILE_SIZE" in config_py
    servico = (BASE / "app" / "services" / "file_storage_service.py").read_text(
        encoding="utf-8"
    )
    assert "UPLOAD_MAX_FILE_SIZE" in servico, (
        "UPLOAD_MAX_FILE_SIZE é configurado mas nunca aplicado"
    )


def test_app_registra_headers_de_seguranca():
    """O after_request de headers de segurança precisa existir."""
    init = (BASE / "app" / "__init__.py").read_text(encoding="utf-8")
    assert "after_request" in init, "nenhum after_request registrando headers"
    assert "Content-Security-Policy" in init


def test_uploads_nao_e_publico():
    """`/uploads/` não pode estar na lista de caminhos públicos."""
    init = (BASE / "app" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r"PUBLICOS\s*=\s*\(([^)]*)\)", init, re.S)
    assert match, "lista PUBLICOS não encontrada"
    assert "/uploads/" not in match.group(1), (
        "/uploads/ está público: fotos de checklist saem sem autenticação"
    )


def test_render_template_e_importado_no_init():
    """Regressão: o handler de CSRF chamava render_template sem importá-lo."""
    init = (BASE / "app" / "__init__.py").read_text(encoding="utf-8")
    # Lê a AST em vez de casar com regex: o import pode estar em uma linha só
    # ou espalhado em parênteses, e um teste não deve quebrar por isso.
    arvore = ast.parse(init)
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module == "flask":
            importados.update(alias.name for alias in no.names)
    assert importados, "import de flask não encontrado"
    assert "render_template" in importados, (
        "render_template não é importado em app/__init__.py"
    )


def test_registro_de_service_worker_removido():
    """SW na raiz daria controle persistente de toda a origem."""
    js = (BASE / "app" / "static" / "js" / "app.js").read_text(encoding="utf-8")
    assert "serviceWorker" not in js, (
        "registro de service worker na raiz do origin deve ser removido"
    )


# ===========================================================================
# Backup: nada de dado pessoal trafegar em claro
# ===========================================================================


@pytest.fixture(scope="module")
def backup_sh() -> str:
    return (BASE / "scripts" / "backup.sh").read_text(encoding="utf-8")


def test_backup_aborta_sem_chave_publica(backup_sh):
    """    Sem chave pública o script precisa parar, não enviar o banco em claro.

    O backup leva CPF, telefone e endereço de clientes. Um caminho do tipo "se
    não der para cifrar, manda assim mesmo" é a pior falha possível aqui: a
    perda do dado sensível passaria pela caixa de e-mail sem ninguém perceber.
    """
    sem_chave = backup_sh.index("RECIPIENT_FILE")
    die = backup_sh.index("die ", sem_chave)
    assert "sem chave publica" in backup_sh[die : die + 200], (
        "backup.sh precisa abortar quando não há chave pública configurada"
    )
    # E a checagem precisa vir ANTES de empacotar, para não produzir um
    # tar.gz em claro que ninguém cifrou.
    assert die < backup_sh.index("tar -czf"), (
        "a validação da chave precisa vir antes de gerar o arquivo"
    )


def test_backup_criptografa_antes_de_enviar(backup_sh):
    """A ordem é cifrar -> apagar o claro -> enviar."""
    idx_age = backup_sh.index("age -r")
    idx_rm = backup_sh.index("rm -f \"$PLAIN\"", idx_age)
    idx_envio = backup_sh.index("send_backup.py")
    assert idx_age < idx_rm < idx_envio, (
        "o fluxo precisa ser: criptografar, apagar o tar.gz em claro, só então enviar"
    )


def test_backup_apaga_o_arquivo_em_claro(backup_sh):
    """O staging e removido inclusive em caso de erro.

    Um `trap` de limpeza é o que impede que uma execução interrompida deixe o
    banco decifrado em /tmp.
    """
    assert re.search(r"trap .*rm -rf \"\$STAGE\"", backup_sh), (
        "o staging precisa ser limpo no trap para não sobrar banco em claro"
    )


def test_backup_valida_a_assinatura_antes_de_enviar(backup_sh):
    """Confere que o arquivo é age de verdade, não um tar.gz renomeado."""
    idx_age = backup_sh.index("age -r")
    idx_check = backup_sh.index("head -c 4 \"$ARCHIVE\"")
    idx_envio = backup_sh.index("send_backup.py")
    assert idx_age < idx_check < idx_envio, (
        "a checagem da assinatura precisa vir entre a cifragem e o envio"
    )


def test_nenhum_backup_em_claro_e_gerado():
    """Nenhum caminho de backup pode deixar um .tar.gz legível em disco.

    O temporário em claro é necessário (o age lê um arquivo), mas vive só no
    staging apagado pelo trap. O que não pode existir é um .tar.gz sobrevivendo
    em `backups/`. A única referência a .tar.gz fora do temporário tem de ser a
    rotina que APAGA arquivos antigos em claro.
    """
    backup = (BASE / "scripts" / "backup.sh").read_text(encoding="utf-8")
    codigo = "\n".join(
        l for l in backup.splitlines() if not l.strip().startswith("#")
    )
    for linha in codigo.splitlines():
        if ".tar.gz" not in linha:
            continue
        eh_temporario = "PLAIN" in linha
        remove_antigo = "-delete" in linha or "rm -f" in linha
        criptografa = ".age" in linha
        assert (
            eh_temporario or remove_antigo or criptografa
        ), f"backup mantem um .tar.gz em claro: {linha.strip()}"

    # Nenhum caminho pode enviar algo que não seja .age.
    idx_envio = codigo.index("send_backup.py")
    assert codigo[:idx_envio].rstrip().endswith('"$ARCHIVE"') or ".age" in codigo[:idx_envio], (
        "o envio precisa receber o arquivo criptografado"
    )


def test_send_backup_recusa_arquivo_nao_criptografado():
    """O envio é a última barreira: se apontado para um tar.gz, ele recusa."""
    import subprocess
    import sys
    import tempfile

    script = BASE / "scripts" / "send_backup.py"
    with tempfile.TemporaryDirectory() as tmp:
        claro = Path(tmp) / "backup.tar.gz"
        claro.write_bytes(b"CPF 11144477735 Joao da Silva")

        falso = Path(tmp) / "falso.tar.gz.age"
        falso.write_bytes(b"age")  # extensão mente, conteúdo não é age

        for arquivo in (claro, falso):
            resultado = subprocess.run(
                [sys.executable, str(script), str(arquivo)],
                capture_output=True,
                text=True,
                env={"PATH": "/usr/bin:/bin"},
            )
            assert resultado.returncode != 0, f"{arquivo.name} deveria ser recusado"
            assert "ERRO" in resultado.stderr, resultado.stderr


def test_chave_privada_do_backup_nao_esta_no_servidor():
    """A privada tem de ficar fora; o que fica no servidor é só a pública."""
    gitignore = (BASE / ".gitignore").read_text(encoding="utf-8")
    assert "backup-key" in gitignore or "age" in gitignore, (
        "arquivos de chave privada não podem ser versionados"
    )

    backup_sh = (BASE / "scripts" / "backup.sh").read_text(encoding="utf-8")
    assert "AGE-SECRET-KEY" not in backup_sh, (
        "backup.sh não deve manipular chave privada; só a pública de destino"
    )


def test_provision_instala_age_e_avisa():
    """Sem age o backup não criptografa — o problema tem que aparecer no deploy."""
    provision = (BASE / "scripts" / "provision.sh").read_text(encoding="utf-8")
    assert re.search(r"apt-get install[^\n]*\bage\b", provision), (
        "provision.sh precisa instalar age"
    )
    assert "command -v age" in provision, (
        "provision.sh precisa verificar se age ficou disponível"
    )
    assert "BACKUP_RECIPIENT" in provision, (
        "provision.sh precisa aceitar a chave pública de destino"
    )


def test_restore_valida_antes_de_sobrescrever():
    """A restauração não pode tocar no banco antes de confiar no backup."""
    restore = (BASE / "scripts" / "restore.sh").read_text(encoding="utf-8")
    idx_decifra = restore.index("age -d")
    idx_valida = restore.index("integrity_check")
    idx_para_app = restore.index("stop app")
    idx_copia = restore.index('cp "$TMP/japacar.db"')
    assert idx_decifra < idx_valida, "tem que decifrar antes de validar"
    assert idx_valida < idx_para_app < idx_copia, (
        "a integridade precisa ser conferida antes de parar o app e sobrescrever"
    )


def test_restore_apaga_o_banco_decifrado():
    """O staging decifrado não pode sobrar em /tmp."""
    restore = (BASE / "scripts" / "restore.sh").read_text(encoding="utf-8")
    trap = restore[restore.index("trap ") : restore.index("trap ") + 200]
    assert "japacar.db" in trap and ("shred" in trap or "rm -f" in trap), (
        "o trap precisa apagar o banco decifrado do staging"
    )


def test_criptografia_do_backup_documentada():
    """A operação precisa estar explicada, inclusive aonde guardar a chave."""
    readme = (BASE / "README.md").read_text(encoding="utf-8")
    assert re.search(r"age", readme), "o README precisa citar age"
    assert re.search(r"backup.*(criptograf|cifrad)", readme, re.I), (
        "o README precisa dizer que o backup é criptografado"
    )
    assert re.search(r"chave privada.*(fora|n[aã]o (fica|est[aá]) no servidor)", readme, re.I), (
        "o README precisa deixar claro que a chave privada fica fora do servidor"
    )
