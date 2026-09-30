#!/usr/bin/env python3
"""Envia o backup CRIPTOGRAFADO como anexo para o Gmail usando senha de app.

Le credenciais do ambiente: BACKUP_FROM, BACKUP_TO, GMAIL_APP_PASSWORD.

Este script se recusa a enviar um arquivo que nao seja age. A ultima barreira
contra vazar o banco em claro: `backup.sh` ja criptografa antes de chamar
aqui, mas se alguem apontar este script para o tar.gz, o dado pessoal dos
clientes sairia legivel.
"""
import os
import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# Assinatura de um arquivo age (comeca com "age-encryption.org").
ASSINATURA_AGE = b"age-encryption.org"


def exige_criptografado(caminho: str) -> None:
    """Recusa qualquer coisa que nao seja um arquivo age de verdade.

    Um arquivo chamado `.age` com conteudo arbitrario passaria na checagem
    apenas de extensao. Por isso o cabecalho precisa bater exatamente: e o que
    separa um backup cifrado de um tar.gz renomeado.
    """
    if not caminho.endswith(".age"):
        sys.stderr.write(
            f"ERRO: {caminho} nao termina em .age. Recusando enviar backup "
            "sem criptografia: o arquivo contem CPF, telefone e endereco dos "
            "clientes.\n"
        )
        sys.exit(1)
    with open(caminho, "rb") as arquivo:
        inicio = arquivo.read(len(ASSINATURA_AGE))
    if inicio != ASSINATURA_AGE:
        sys.stderr.write(
            f"ERRO: {caminho} nao tem cabecalho age valido. Recusando enviar.\n"
        )
        sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("uso: send_backup.py <arquivo.tar.gz.age>\n")
        sys.exit(2)

    attachment_path = sys.argv[1]
    exige_criptografado(attachment_path)

    faltando = [
        v for v in ("BACKUP_FROM", "BACKUP_TO", "GMAIL_APP_PASSWORD")
        if not os.environ.get(v)
    ]
    if faltando:
        sys.stderr.write(
            "ERRO: variaveis de ambiente ausentes: " + ", ".join(faltando) + "\n"
            "O backup continua cifrado em disco; configure e rode de novo.\n"
        )
        sys.exit(1)

    sender = os.environ["BACKUP_FROM"]
    recipient = os.environ["BACKUP_TO"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    with open(attachment_path, "rb") as f:
        attachment = f.read()

    nome = os.path.basename(attachment_path)

    msg = MIMEMultipart()
    msg["From"] = f"Backup JAPACAR <{sender}>"
    msg["To"] = recipient
    msg["Subject"] = f"Backup JAPACAR (criptografado) - {nome}"
    msg["Date"] = formatdate(localtime=True)

    msg.attach(MIMEText(
        "Backup automatico do sistema JAPACAR, criptografado com age.\n\n"
        f"Arquivo em anexo: {nome}\n\n"
        "O conteudo (banco de dados e fotos dos clientes) esta cifrado. Nao ha\n"
        "como ler este arquivo sem a chave privada age.\n\n"
        "Se voce esta lendo esta mensagem e nao tem a chave privada, o arquivo\n"
        "e inutil -- e era esse o objetivo.\n\n"
        "Para restaurar, no servidor:\n"
        "  BACKUP_KEY=~/minha-chave-privada.txt \\\n"
        f"    sudo -E ./scripts/restore.sh ./{nome}\n"
        "Sem BACKUP_KEY o script pergunta a chave no terminal.\n\n"
        "A chave privada NAO fica no servidor de proposito. Guarde a sua em\n"
        "local seguro e fora dali; sem ela este backup nao pode ser lido.\n",
        "plain", "utf-8"))

    part = MIMEApplication(attachment, _subtype="age", Name=nome)
    part["Content-Disposition"] = f'attachment; filename="{nome}"'
    msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(sender, app_password)
        server.send_message(msg)

    print(f"enviado backup para {recipient}")


if __name__ == "__main__":
    main()