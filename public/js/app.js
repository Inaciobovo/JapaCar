// JAPACAR - JS auxiliar
(function () {
    'use strict';

    // Confirmação para formulários de exclusão
    document.addEventListener('submit', function (e) {
        const form = e.target;
        if (form.matches('[data-confirm]')) {
            const message = form.getAttribute('data-confirm') || 'Tem certeza que deseja excluir?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        }
    });

    // Service Worker: desligado de propósito.
    // Um SW registrado em "/" assume o escopo do origin inteiro e passa a
    // servir respostas de uma origem diferente da do sistema, o que anula o
    // ganho de segurança do registro de operator. Como o sistema não é um PWA
    // offline, o registro não traz benefício e só aumenta superfície.

    // Máscara simples de placa (ABC-1234 ou ABC1D23)
    function applyPlacaMask(input) {
        if (!input) return;
        input.addEventListener('input', function () {
            let value = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            if (value.length > 7) value = value.slice(0, 7);
            if (value.length > 3) {
                value = value.slice(0, 3) + '-' + value.slice(3);
            }
            input.value = value;
        });
    }

    // Máscara simples de CPF (000.000.000-00)
    function applyCpfMask(input) {
        if (!input) return;
        input.addEventListener('input', function () {
            let value = input.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            value = value
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            input.value = value;
        });
    }

    // Máscara simples de telefone ((00) 00000-0000)
    function applyPhoneMask(input) {
        if (!input) return;
        input.addEventListener('input', function () {
            let value = input.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            if (value.length > 2) {
                value = '(' + value.slice(0, 2) + ') ' + value.slice(2);
            }
            if (value.length > 10) {
                value = value.slice(0, 10) + '-' + value.slice(10);
            } else if (value.length > 9) {
                value = value.slice(0, 9) + '-' + value.slice(9);
            }
            input.value = value;
        });
    }

    // Máscara de moeda brasileira (1.234,56)
    function applyValorMask(input) {
        if (!input) return;
        input.addEventListener('input', function () {
            let digits = input.value.replace(/\D/g, '');
            if (digits.length === 0) {
                input.value = '';
                return;
            }
            let padded = digits.padStart(3, '0');
            let cents = padded.slice(-2);
            let reais = padded.slice(0, -2);
            reais = reais.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            input.value = reais + ',' + cents;
        });
    }

    // Detecta o tamanho real da tela e ajusta o layout (mobile x desktop)
    function initDeviceClass() {
        const BREAKPOINT = 992;
        const query = '(max-width: ' + (BREAKPOINT - 1) + 'px)';
        const mq = window.matchMedia ? window.matchMedia(query) : null;

        function apply() {
            const body = document.body;
            if (!body) return;
            const isMobile = mq ? mq.matches : window.innerWidth < BREAKPOINT;
            body.classList.toggle('device-mobile', isMobile);
            body.classList.toggle('device-desktop', !isMobile);
            document.body.setAttribute('data-device', isMobile ? 'mobile' : 'desktop');
        }

        apply();

        if (mq && mq.addEventListener) {
            mq.addEventListener('change', apply);
        } else if (mq && mq.addListener) {
            mq.addListener(apply);
        } else {
            window.addEventListener('resize', apply, { passive: true });
        }

        window.addEventListener('orientationchange', function () {
            setTimeout(apply, 150);
        });
    }

    // Menu drawer (mobile)
    function initDrawer() {
        const drawer = document.getElementById('navDrawer');
        const backdrop = document.getElementById('navDrawerBackdrop');
        const openBtn = document.getElementById('drawerOpen');
        const closeBtn = document.getElementById('drawerClose');
        if (!drawer || !backdrop) return;

        function openDrawer() {
            drawer.classList.add('open');
            backdrop.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
        function closeDrawer() {
            drawer.classList.remove('open');
            backdrop.classList.remove('show');
            document.body.style.overflow = '';
        }

        if (openBtn) openBtn.addEventListener('click', openDrawer);
        if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
        backdrop.addEventListener('click', closeDrawer);
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeDrawer();
        });
    }

    // Botão voltar ao topo
    function initBackToTop() {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'back-to-top';
        btn.setAttribute('aria-label', 'Voltar ao topo');
        btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        document.body.appendChild(btn);

        window.addEventListener('scroll', function () {
            const show = (window.scrollY || document.documentElement.scrollTop) > 400;
            btn.classList.toggle('show', show);
        }, { passive: true });

        btn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Alternar visibilidade de campos de senha
    function initPasswordToggles() {
        document.querySelectorAll('[data-password-toggle]').forEach(function (trigger) {
            trigger.addEventListener('click', function () {
                const target = document.getElementById(trigger.getAttribute('data-password-toggle'));
                if (!target) return;
                const isPassword = target.type === 'password';
                target.type = isPassword ? 'text' : 'password';
                const icon = trigger.querySelector('i');
                if (icon) {
                    icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
                }
            });
        });
    }

    // Soma dos itens do orçamento (atualiza total em tempo real)
    function initOrcamentoTotals() {
        const container = document.querySelector('[data-orcamento-items]');
        const totalLabel = document.querySelector('[data-orcamento-total]');
        const maoDeObra = document.querySelector('[data-orcamento-mao-de-obra]');
        if (!container || !totalLabel) return;

        const maskToNumber = function (v) {
            return parseFloat((v || '0').replace(/[^\d,]/g, '').replace(',', '.')) || 0;
        };

        function refresh() {
            let total = 0;
            container.querySelectorAll('.orcamento-item-valor').forEach(function (inp) {
                total += maskToNumber(inp.value);
            });
            total += maskToNumber(maoDeObra ? maoDeObra.value : 0);
            const formatted = total.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            totalLabel.textContent = 'R$ ' + formatted;
        }

        container.addEventListener('input', refresh);
        if (maoDeObra) maoDeObra.addEventListener('input', refresh);
        refresh();
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('input[data-mask="placa"]').forEach(applyPlacaMask);
        document.querySelectorAll('input[data-mask="cpf"]').forEach(applyCpfMask);
        document.querySelectorAll('input[data-mask="telefone"]').forEach(applyPhoneMask);
        document.querySelectorAll('input.valor').forEach(applyValorMask);

        // Auto-submit de filtros quando selecao muda
        document.querySelectorAll('select[data-auto-submit]').forEach(function (select) {
            select.addEventListener('change', function () {
                select.closest('form').submit();
            });
        });

        initDeviceClass();
        initDrawer();
        initBackToTop();
        initPasswordToggles();
        initOrcamentoTotals();
    });
})();