"""Gravacao de arquivos enviados pelo usuario.

O servico original aceitava qualquer arquivo e mantinha a extensao do nome
enviado. Como as fotos sao servidas de volta na MESMA ORIGEM do sistema
(`/uploads/...`), um `foto.html` ou `foto.svg` virava XSS armazenado: o
navegador executava o script contra a origem do JAPACAR e o atacante controlava
a sessao de um atendente logado.

A defesa aqui tem duas camadas, porque a segunda e a que realmente fecha o
problema:

1. **Allowlist de extensao** — barra .html, .svg, .js, .php, .exe.
2. **Conferencia dos magic bytes** — o conteudo precisa realmente ser uma
   imagem. Sem isso, `encomenda.gz` renomeado para `.jpg` passaria na
   camada 1 e seria reinterpretado pelo navegador.
"""

import uuid
from pathlib import Path

from flask import current_app


class UploadRejeitado(ValueError):
    """Arquivo enviado nao pode ser gravado.

    Levanta erro em vez de silenciosamente ignorar: um arquivo barrado precisa
    aparecer para o operador como erro, nunca como "salvo com sucesso".
    """


# Assinaturas binarias por tipo aceito. O offset do PDF e proposital: o
# cabecalho %PDF fica nas posicoes 0-3, o que impede um PDF com script
# embutido de passar como JPEG.
ASSINATURAS = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".gif": (b"GIF87a", b"GIF89a"),
    # WebP e "RIFF" nos bytes 0-3 e "WEBP" nos bytes 8-11.
    ".webp": (b"RIFF",),
}

ASSINATURA_WEBP_EM = 8
ASSINATURA_WEBP_VALIDA = b"WEBP"


def _cabecalho_valido(caminho, extensao):
    with caminho.open("rb") as arquivo:
        cabecalho = arquivo.read(32)
    if extensao == ".webp":
        return (
            cabecalho[:4] == ASSINATURAS[".webp"][0]
            and cabecalho[ASSINATURA_WEBP_EM : ASSINATURA_WEBP_EM + 4]
            == ASSINATURA_WEBP_VALIDA
        )
    return any(cabecalho.startswith(ass) for ass in ASSINATURAS[extensao])


class FileStorageService:
    def salvar(self, arquivo, sub_pasta):
        """Grava um arquivo enviado e devolve o caminho relativo.

        Levanta `UploadRejeitado` quando o arquivo viola extensao, conteudo ou
        tamanho. A validacao acontece ANTES da escrita: um arquivo recusado
        nunca chega ao disco.
        """
        if arquivo is None or not arquivo.filename:
            return None

        nome_original = arquivo.filename
        extensao = ""
        if "." in nome_original:
            # rfind +1: um nome como "foto.png.exe" vira ".exe", e nao ".png.exe".
            extensao = nome_original[nome_original.rfind(".") :].lower()

        permitidas = current_app.config["UPLOAD_EXTENSOES_PERMITIDAS"]
        if extensao not in permitidas:
            raise UploadRejeitado(
                f'Tipo de arquivo não permitido: "{extensao or nome_original}". '
                f"Envie uma imagem ({', '.join(sorted(permitidas))})."
            )

        tamanho_maximo = current_app.config["UPLOAD_MAX_FILE_SIZE"]
        tamanho_declarado = getattr(arquivo, "content_length", 0) or 0
        if tamanho_declarado > tamanho_maximo:
            raise UploadRejeitado(
                f"Arquivo maior que o limite de {tamanho_maximo // (1024 * 1024)} MB."
            )

        # Nome gerado no servidor: o nome enviado pelo cliente nao influence a
        # gravacao, o que elimina traversal e colisao de nome.
        nome_arquivo = f"{uuid.uuid4()}{extensao}"

        raiz = Path(current_app.config["UPLOAD_DIR"]).resolve()
        destino_dir = (raiz / sub_pasta).resolve()
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / nome_arquivo

        arquivo.save(destino)

        try:
            if not _cabecalho_valido(destino, extensao):
                destino.unlink(missing_ok=True)
                raise UploadRejeitado(
                    "O conteúdo do arquivo não corresponde a uma imagem válida."
                )
        except UploadRejeitado:
            raise
        except OSError:
            destino.unlink(missing_ok=True)
            raise UploadRejeitado("Não foi possível validar o arquivo enviado.")

        if destino.stat().st_size > tamanho_maximo:
            destino.unlink(missing_ok=True)
            raise UploadRejeitado(
                f"Arquivo maior que o limite de {tamanho_maximo // (1024 * 1024)} MB."
            )

        return f"{sub_pasta}/{nome_arquivo}".replace("\\", "/")

    def remover(self, caminho_relativo):
        if not caminho_relativo or not caminho_relativo.strip():
            return
        try:
            raiz = Path(current_app.config["UPLOAD_DIR"]).resolve()
            destino = (raiz / caminho_relativo).resolve()
            # So apaga o que estiver de fato dentro de uploads/. Um caminho
            # relativo adulterado no banco nao pode alcançar o banco de dados.
            if destino == raiz or raiz not in destino.parents:
                return
            destino.unlink(missing_ok=True)
        except OSError:
            pass


file_storage_service = FileStorageService()
