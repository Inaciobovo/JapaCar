<nav class="bottom-nav">
    @if ($podeVerFinanceiro)
        <a href="{{ route('painel') }}" @class(['active' => $activePage === 'dashboard'])>
            <i class="bi bi-speedometer2"></i>
            <span>Dashboard</span>
        </a>
    @endif
    <a href="{{ route('clientes.index') }}" @class(['active' => $activePage === 'clientes'])>
        <i class="bi bi-people"></i>
        <span>Clientes</span>
    </a>
    <a href="{{ route('atendimentos.index') }}" @class(['active' => $activePage === 'atendimentos'])>
        <i class="bi bi-tools"></i>
        <span>Serviços</span>
    </a>
    <a href="{{ route('orcamentos.index') }}" @class(['active' => $activePage === 'orcamentos'])>
        <i class="bi bi-file-earmark-text"></i>
        <span>Orçamentos</span>
    </a>
</nav>
