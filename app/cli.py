import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Usuario
from app.security import PERFIS_VALIDOS

# Senhas de demonstração ficam apenas no dev. O seed de produção é sempre
# manual (`flask usuario-criar`), e mesmo assim exige senha forte.
SENHAS_PADRAO = {
    "admin": "admin123",
    "mecanico": "mecanico123",
}


def seed_users():
    """Cria os usuários de demonstração, apenas se o app for de desenvolvimento.

    Em produção este caminho não roda: `SEED_ON_STARTUP` é 0 por padrão e a
    validação de configuração rejeita subir o app em `prod` com ele ligado.
    """
    from flask import current_app

    if current_app.config.get("ENV") == "production" or not current_app.debug:
        return []

    criados = []
    for login, perfil in (("admin", "ADMIN"), ("mecanico", "MECANICO")):
        if db.session.execute(
            db.select(Usuario).where(Usuario.login == login)
        ).scalar_one_or_none() is None:
            db.session.add(
                Usuario(
                    nome="Administrador" if perfil == "ADMIN" else "Mecânico",
                    login=login,
                    senha=gerar_hash(SENHAS_PADRAO[login]),
                    perfil=perfil,
                    ativo=True,
                )
            )
            criados.append(login)
    db.session.commit()
    return criados


def gerar_hash(senha):
    import bcrypt

    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def senha_forte(senha):
    """Regra mínima de senha.

    `admin123` satisfazeria qualquer regra baseada só em tamanho, e é exatamente
    a senha que estava documentada no README.
    """
    if len(senha) < 10:
        return False, "A senha precisa de ao menos 10 caracteres."
    if senha.lower() in SENHAS_PADRAO.values():
        return False, "Esta senha já foi usada como senha padrão do sistema."
    if senha.isdigit() or senha.isalpha():
        return False, "A senha precisa misturar letras e números."
    return True, None


def register_cli(app):
    @app.cli.command("seed")
    def seed_command():
        """Cria os usuários padrão de DEMONSTRAÇÃO (apenas em dev)."""
        criados = seed_users()
        if not criados:
            click.echo(
                "Nada a fazer. Em produção use: flask usuario-criar "
                "--login admin --perfil ADMIN"
            )
            return
        for login in criados:
            click.echo(f">>> Usuário {login} criado (senha de demonstração).")

    @app.cli.command("usuario-criar")
    @click.option("--login", help="Login de acesso")
    @click.option("--nome", help="Nome completo")
    @click.option(
        "--perfil",
        type=click.Choice(sorted(PERFIS_VALIDOS)),
        default="ADMIN",
        show_default=True,
    )
    @click.option(
        "--senha",
        help=(
            "Senha inicial. Evita o prompt quando o provision.sh roda "
            "desligado. A senha vai para o histórico do shell; prefira o prompt."
        ),
    )
    @with_appcontext
    def usuario_criar(login, nome, perfil, senha):
        """Cria um usuário com senha forte (usado no primeiro acesso em produção)."""
        login = (login or "").strip().lower()
        if not login:
            login = click.prompt("Login", type=str).strip().lower()
        nome = (nome or "").strip() or login
        if db.session.execute(
            db.select(Usuario).where(Usuario.login == login)
        ).scalar_one_or_none() is not None:
            click.echo(f"ERRO: já existe um usuário com o login '{login}'.")
            raise SystemExit(1)

        if senha:
            ok, motivo = senha_forte(senha)
            if not ok:
                click.echo(f"ERRO: {motivo}")
                raise SystemExit(1)
        else:
            senha = click.prompt("Senha", hide_input=True, confirmation_prompt=True)
            ok, motivo = senha_forte(senha)
            if not ok:
                click.echo(f"ERRO: {motivo}")
                raise SystemExit(1)

        db.session.add(
            Usuario(nome=nome, login=login, senha=gerar_hash(senha), perfil=perfil, ativo=True)
        )
        db.session.commit()
        click.echo(f">>> Usuário '{login}' criado com perfil {perfil}.")

    @app.cli.command("usuario-senha")
    @click.argument("login")
    @click.option("--senha", help="Nova senha. Evita o prompt; fica no histórico do shell.")
    @with_appcontext
    def usuario_senha(login, senha):
        """Redefine a senha de um usuário."""
        usuario = db.session.execute(
            db.select(Usuario).where(Usuario.login == login.strip().lower())
        ).scalar_one_or_none()
        if usuario is None:
            click.echo(f"ERRO: usuário '{login}' não encontrado.")
            raise SystemExit(1)

        if not senha:
            senha = click.prompt("Nova senha", hide_input=True, confirmation_prompt=True)
        ok, motivo = senha_forte(senha)
        if not ok:
            click.echo(f"ERRO: {motivo}")
            raise SystemExit(1)

        usuario.senha = gerar_hash(senha)
        db.session.commit()
        click.echo(f">>> Senha de '{usuario.login}' atualizada.")

    @app.cli.command("usuario-listar")
    @with_appcontext
    def usuario_listar():
        """Lista os usuários cadastrados."""
        for u in db.session.execute(db.select(Usuario).order_by(Usuario.login)).scalars():
            estado = "ativo" if u.ativo else "inativo"
            click.echo(f"{u.login:<20} {u.perfil:<10} {estado:<8} {u.nome}")
