<header class="app-header">
    <button type="button" class="hamburger-btn" id="drawerOpen" aria-label="Abrir menu">
        <i class="bi bi-list"></i>
    </button>
    <div class="brand">
        <span class="brand-badge">JP</span>
        <span class="d-none d-sm-inline">JAPACAR</span>
    </div>
    <div class="user-info">
        <span>{{ $usuario?->login }}</span>
        <form action="{{ route('logout') }}" method="post" class="d-inline">
            @csrf
            <button type="submit" class="logout-link border-0 bg-transparent" title="Sair">
                <i class="bi bi-box-arrow-right"></i>
            </button>
        </form>
    </div>
    @include('fragments.drawer')
</header>
