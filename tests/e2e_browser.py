import os
import re
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "http://localhost:8090")

RESULTADOS = []


def check(nome, ok, detalhe=""):
    RESULTADOS.append((nome, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {nome}" + (f"  -> {detalhe}" if detalhe else ""))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        dispositivo = p.devices["iPhone 13"]
        context = browser.new_context(**dispositivo)
        page = context.new_page()
        erros_console = []
        erros_pagina = []
        page.on("console", lambda msg: erros_console.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: erros_pagina.append(str(exc)))
        page.on("dialog", lambda dlg: dlg.accept())

        # 1. Gate anonimo
        page.goto(BASE + "/")
        check("anonimo / redireciona para /login", "/login" in page.url)

        # 2. Login
        page.goto(BASE + "/login")
        check("login pagina carrega", "JAPACAR - Login" in page.title())
        page.fill("#username", "admin")
        page.fill("#password", "admin123")
        page.click("button.login-btn")
        try:
            page.wait_for_url(f"{BASE}/", timeout=8000)
            check("login entra no dashboard", "/login" not in page.url)
        except Exception as e:
            check("login entra no dashboard", False, str(e))

        # 3. Navegacao entre secoes
        for rota, titulo in [
            ("/clientes", "Clientes"),
            ("/veiculos", "Veículos"),
            ("/atendimentos", "Painel de Serviços"),
            ("/orcamentos", "Orçamentos"),
            ("/checklists", "Checklists"),
            ("/despesas", "Despesas"),
            ("/relatorios/orcamentos", "Relatório de Orçamentos"),
        ]:
            page.goto(BASE + rota)
            texto = (page.text_content("main") or "") + page.content()
            check(
                f"lista {rota} carrega",
                titulo in texto and "Internal Server Error" not in texto,
            )

        # 3b. Tela de Pecas foi removida
        page.goto(BASE + "/")
        check(
            "pecas removida da navegacao",
            "Peças" not in page.content() and "/pecas" not in page.content(),
        )

        # 4. Criar cliente
        pid = os.getpid()
        nome_cliente = f"Cliente E2E {pid}"
        cpf_cliente = f"{pid % 100:03d}.{pid % 200 + 100:03d}.{pid % 300 + 300:03d}-{pid % 90 + 10:02d}"
        page.goto(BASE + "/clientes/novo")
        page.fill("input[name=nome]", nome_cliente)
        page.fill("input[name=cpf]", cpf_cliente)
        page.fill("input[name=telefone]", "(11) 99999-0000")
        page.fill("input[name=email]", "e2e@example.com")
        page.fill("input[name=endereco]", "Rua E2E, 100")
        page.click(".form-actions button[type=submit]")
        page.wait_for_url("**/clientes")
        check("criar cliente redireciona p/ lista", page.url.endswith("/clientes"))
        page.fill("input[name=busca]", nome_cliente)
        page.click("form.search-bar button")
        page.wait_for_timeout(300)
        check("cliente aparece na busca", nome_cliente in page.content())

        # 5. Criar veiculo vinculado ao cliente criado
        placa = f"E2E{pid % 10000:04d}"
        modelo = f"Modelo E2E {pid}"
        page.goto(BASE + "/veiculos/novo")
        page.fill("input[name=placa]", placa)
        page.fill("input[name=marca]", "Marca E2E")
        page.fill("input[name=modelo]", modelo)
        page.fill("input[name=ano]", "2021")
        page.fill("input[name=cor]", "Azul")
        page.select_option("select[name='cliente.id']", label=nome_cliente)
        page.click(".form-actions button[type=submit]")
        page.wait_for_url("**/veiculos")
        page.fill("input[name=busca]", modelo)
        page.click("form.search-bar button")
        page.wait_for_timeout(300)
        check("veiculo aparece na busca", placa in page.content() or modelo in page.content())

        # 5b. Editar veiculo criado
        card = page.locator(".list-card", has_text=modelo).first
        card.locator("a[href*='/editar']").click()
        page.wait_for_url("**/veiculos/*/editar")
        page.fill("input[name=cor]", "Verde")
        page.click(".form-actions button[type=submit]")
        page.wait_for_url("**/veiculos")
        page.fill("input[name=busca]", modelo)
        page.click("form.search-bar button")
        page.wait_for_timeout(300)
        check("editar veiculo salva mudancas", "Verde" in page.content())

        # 5c. Remover veiculo com historico deve ser bloqueado
        page.goto(BASE + "/veiculos")
        page.locator("form[action*='/remover'] button").first.evaluate("b => b.click()")
        page.locator("div.alert").first.wait_for(state="visible", timeout=8000)
        msg = page.locator("div.alert").first.inner_text()
        check("remover veiculo com historico bloqueado", "não pode ser removido" in msg)

        # 5d. Remover veiculo criado (sem historico) deve funcionar
        page.fill("input[name=busca]", modelo)
        page.click("form.search-bar button")
        page.wait_for_timeout(300)
        card = page.locator(".list-card", has_text=modelo).first
        card.locator("form[action*='/remover'] button").evaluate("b => b.click()")
        page.locator("div.alert").first.wait_for(state="visible", timeout=8000)
        msg = page.locator("div.alert").first.inner_text()
        check("remover veiculo sem historico funciona", "Veículo removido." in msg)

        # 6. Criar despesa
        desc = f"Despesa E2E {pid}"
        page.goto(BASE + "/despesas/nova")
        page.fill("input[name=descricao]", desc)
        page.fill("input[name=valorText]", "12,50")
        page.fill("input[name=data]", "2026-09-21")
        page.select_option("select[name=categoria]", label="Produtos")
        page.click(".form-actions button[type=submit]")
        page.wait_for_url("**/despesas")
        check("despesa aparece na lista", desc in page.content())

        # 7. Paginas de detalhe
        page.goto(BASE + "/atendimentos")
        html = page.content()
        m = re.search(r"/atendimentos/(\d+)/editar", html)
        if m:
            at_id = m.group(1)
            ok_detalhe = True
            for rota in (f"/atendimentos/{at_id}", f"/atendimentos/{at_id}/editar", f"/atendimentos/{at_id}/finalizar"):
                page.goto(BASE + rota)
                conteudo = page.content()
                if "Internal Server Error" in conteudo or "Not Found" in conteudo:
                    ok_detalhe = False
                    check(f"detalhe {rota}", False)
            if ok_detalhe:
                check("detalhes/editar/finalizar atendimento carregam", True)
        else:
            check("atendimento da lista abre detalhe", False, "sem link /editar na lista")

        # 8. PDF de orcamento
        page.goto(BASE + "/orcamentos")
        html = page.content()
        m = re.search(r"/orcamentos/(\d+)/editar", html)
        if m:
            orc_id = m.group(1)
            page.goto(BASE + f"/orcamentos/{orc_id}/editar")
            check("editar orcamento carrega", "Orçamento" in page.content())
            resp = context.request.get(BASE + f"/orcamentos/{orc_id}/pdf")
            check(
                "pdf gerado (200 application/pdf)",
                resp.status == 200
                and resp.headers.get("content-type", "").startswith("application/pdf")
                and len(resp.body()) > 500,
                f"{resp.status} {resp.headers.get('content-type')} {len(resp.body())} bytes",
            )
        else:
            check("orcamento encontrado p/ pdf", False, "sem link /editar na lista")

        # 9. Estaticos
        for path in ("/css/style.css", "/js/app.js", "/static/vendor/bootstrap/css/bootstrap.min.css"):
            r = context.request.get(BASE + path)
            check(f"estatico {path}", r.status == 200, str(r.status))

        # 10. Logout via drawer
        page.goto(BASE + "/")
        page.click("#drawerOpen")
        page.eval_on_selector(
            "form[action='/logout'] button[type=submit]", "b => b.click()"
        )
        try:
            page.wait_for_url("**/login**", timeout=8000)
            check("logout do drawer redireciona p/ login", True)
        except Exception as e:
            check("logout do drawer redireciona p/ login", False, str(e))

        # 11. Erros de console/pagina
        # 404 esperado: /sw.js e favicon (PWA preservada como no original). Qualquer outro erro reprova.
        console_ruins = [e for e in erros_console if "404" not in e and "favicon" not in e.lower() and "sw.js" not in e.lower()]
        check("sem erros de console", len(console_ruins) == 0, "; ".join(console_ruins[:5]))
        check("sem erros de pagina", len(erros_pagina) == 0, "; ".join(erros_pagina[:5]))

        browser.close()

    falhas = [n for n, ok in RESULTADOS if not ok]
    print(f"\nE2E: {len(RESULTADOS) - len(falhas)}/{len(RESULTADOS)} passaram")
    if falhas:
        print("FALHOU:", ", ".join(falhas))
        sys.exit(1)


if __name__ == "__main__":
    main()