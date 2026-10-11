<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('titulo', 'JAPACAR') · JAPACAR</title>
    <link rel="stylesheet" href="{{ asset('vendor/bootstrap/css/bootstrap.min.css') }}">
    <style>
        body { background: #f5f6f8; }
        .navbar-brand { font-weight: 700; letter-spacing: .04em; }
        .card { border: 0; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
        .thumb { width: 90px; height: 90px; object-fit: cover; border-radius: .35rem; }
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
        <a class="navbar-brand" href="{{ route('atendimentos.index') }}">JAPACAR</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#menu">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="menu">
            @auth
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ route('painel') }}">Painel</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ route('clientes.index') }}">Clientes</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ route('veiculos.index') }}">Veículos</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ route('checklists.index') }}">Checklists</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ route('atendimentos.index') }}">Atendimentos</a></li>
                </ul>
                <span class="navbar-text text-light me-3">
                    {{ Auth::user()->nome }} · {{ Auth::user()->perfilDescricao() }}
                </span>
                <a class="btn btn-outline-light btn-sm me-2" href="{{ route('perfil.senha.edit') }}">Senha</a>
                <form method="POST" action="{{ route('logout') }}" class="d-inline">
                    @csrf
                    <button class="btn btn-outline-light btn-sm" type="submit">Sair</button>
                </form>
            @endauth
        </div>
    </div>
</nav>

<main class="container pb-5">
    @if (session('status'))
        <div class="alert alert-success alert-dismissible fade show">
            {{ session('status') }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    @endif

    @if ($errors->any())
        <div class="alert alert-danger">
            <strong>Corrija os itens abaixo:</strong>
            <ul class="mb-0">
                @foreach ($errors->all() as $erro)
                    <li>{{ $erro }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    @yield('conteudo')
</main>

<script src="{{ asset('vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
</body>
</html>
