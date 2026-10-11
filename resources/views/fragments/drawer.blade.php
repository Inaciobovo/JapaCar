<div class="nav-drawer-backdrop" id="navDrawerBackdrop"></div>
<aside class="nav-drawer" id="navDrawer">
    <div class="drawer-header">
        <span class="brand-badge">JP</span>
        <span>JAPACAR</span>
        <button type="button" class="drawer-close" id="drawerClose" aria-label="Fechar menu">
            <i class="bi bi-x-lg"></i>
        </button>
    </div>
    <nav class="drawer-nav">
        <div class="drawer-section">Gestão</div>
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
        <div class="drawer-section">Oficina</div>
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
    <div class="drawer-footer">
        <div class="user-line">
            <span class="avatar"><i class="bi bi-person"></i></span>
            <span>{{ $usuario?->login }}</span>
        </div>
        <form action="{{ route('logout') }}" method="post">
            @csrf
            <button type="submit" class="logout-btn">
                <i class="bi bi-box-arrow-right"></i> Sair
            </button>
        </form>
    </div>
</aside>
