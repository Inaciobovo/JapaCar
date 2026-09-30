import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

MOBILE_PATTERN = re.compile(
    r"(?i)(android|iphone|ipod|ipad|opera mini|opera mobi|windows phone|iemobile|"
    r"blackberry|bb10|playbook|mobi|tablet)"
)

# Teto de um valor monetário. Acima disso o dado é erro de digitação, não
# orçamento: um `1e309` ou um `-1.000,00` em um orçamento corrompe o saldo e o
# relatório financeiro sem nenhuma rejeição.
VALOR_MAXIMO = Decimal("99999999.99")


def parse_valor(valor):
    """Converte string monetária pt-BR ('1.234,56') para Decimal.

    Remove pontos de milhar e converte vírgula decimal em ponto.
    Retorna None para valores vazios/inválidos.
    """
    if valor is None or not valor.strip():
        return None
    try:
        return Decimal(valor.strip().replace(".", "").replace(",", "."))
    except (InvalidOperation, ValueError, ArithmeticError):
        return None


def valor_valido(valor, *, minimo=Decimal("0"), maximo=VALOR_MAXIMO):
    """Diz se um Decimal é aceitável como valor monetário.

    Rejeita negativo, zero quando não faz sentido, NaN/Infinity e valores
    absurdos. `Decimal` aceita `NaN` e `Infinity`, e ambos explodem em uma
    soma no relatório.
    """
    if valor is None:
        return False
    if valor.is_nan() or valor.is_infinite():
        return False
    return minimo <= valor <= maximo


def somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def cpf_valido(cpf):
    """Confere os dois dígitos verificadores do CPF.

    Cadastro de cliente é a base de dados pessoais mais sensível do sistema
    (CPF, telefone, endereço); aceitar qualquer 11 dígitos gera duplicidade
    silenciosa quando a pessoa digita um dígito errado.
    """
    digitos = somente_digitos(cpf)
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False
    # O DV1 pesa os 9 primeiros dígitos (pesos 10..2) e o DV2 pesa os 10
    # primeiros (pesos 11..2). Incluir o 10º dígito no cálculo do DV1 — como
    # fazia a versão anterior — rejeita quase todo CPF válido.
    for quantidade, menor_peso in ((9, 2), (10, 2)):
        soma = sum(
            int(digitos[i]) * (quantidade + 1 - i) for i in range(quantidade)
        )
        resto = (soma * 10) % 11
        esperado = 0 if resto == 10 else resto
        if int(digitos[quantidade]) != esperado:
            return False
    return True


def parse_valor_zero(valor):
    v = parse_valor(valor)
    return v if v is not None else Decimal("0")


def parse_data(valor, default=None):
    """Tenta yyyy-MM-dd, depois dd/MM/yyyy; retorna default no fim.

    Espelha OrcamentoService.parseData.
    """
    if valor is not None and valor.strip():
        texto = valor.strip()
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            pass
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            pass
    if default is not None:
        return default
    return date.today()


def eh_dispositivo_movel(user_agent):
    if not user_agent:
        return False
    ua = user_agent.lower()
    tem_marcador = bool(MOBILE_PATTERN.search(ua))
    token_mobile = "mobile" in ua
    desktop_windows = "windows nt" in ua
    return tem_marcador or (token_mobile and not desktop_windows)


def active_page_for(uri):
    if not uri or uri == "/":
        return "dashboard"
    if uri.startswith("/clientes"):
        return "clientes"
    if uri.startswith("/veiculos"):
        return "veiculos"
    if uri.startswith("/checklists"):
        return "checklists"
    if uri.startswith("/atendimentos"):
        return "atendimentos"
    if uri.startswith("/orcamentos"):
        return "orcamentos"
    if uri.startswith("/relatorios"):
        return "relatorios"
    if uri.startswith("/despesas"):
        return "despesas"
    return ""


def format_brl(valor):
    try:
        v = Decimal(valor) if valor is not None else Decimal("0")
    except (ValueError, InvalidOperation):
        v = Decimal("0")
    s = f"{v:,.2f}"
    s = s.replace(",", "\u00a0").replace(".", ",").replace("\u00a0", ".")
    return s


def format_datetime(value, pattern="%d/%m/%Y %H:%M"):
    if value is None:
        return ""
    return value.strftime(pattern)


def format_date(value):
    return value.strftime("%d/%m/%Y") if value else ""