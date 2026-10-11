<aside class="app-sidebar">
    <div class="sidebar-brand">
        <span class="brand-badge">JP</span>
        <span>JAPACAR</span>
    </div>
    <nav class="sidebar-nav">
        <div class="sidebar-section">Gestão</div>
        @if ($podeVerFinanceiro)
            <a href="{{ route('painel') }}" @class(['active' => $activePage === 'dashboard'])>
                <i class="bi bi-speedometer2"></i> Dashboard
            </a>
        @endif
        <a href="{{ route('clientes.index') }}" @class(['active' => $activePage === 'clientes'])>
            <i class="bi bi-people"></i> Clientes
        </a>
        <a href="{{ route('veiculos.index') }}" @class(['active' => $activePage === 'veiculos'])>
            <i class="bi bi-car-front"></i> Veículos
        </a>
        <div class="sidebar-section">Oficina</div>
        <a href="{{ route('atendimentos.index') }}" @class(['active' => $activePage === 'atendimentos'])>
            <i class="bi bi-tools"></i> Serviços
        </a>
        <a href="{{ route('checklists.index') }}" @class(['active' => $activePage === 'checklists'])>
            <i class="bi bi-clipboard-check"></i> Checklists
        </a>
        <a href="{{ route('orcamentos.index') }}" @class(['active' => $activePage === 'orcamentos'])>
            <i class="bi bi-file-earmark-text"></i> Orçamentos
        </a>
    </nav>
    <div class="sidebar-footer">
        <span>{{ $usuario?->login }}</span>
        <form action="{{ route('logout') }}" method="post" class="mt-2">
            @csrf
            <button type="submit" class="text-white-50 text-decoration-none p-0 border-0 bg-transparent" title="Sair">
                <i class="bi bi-box-arrow-right me-1"></i> Sair
            </button>
        </form>
    </div>
</aside>
