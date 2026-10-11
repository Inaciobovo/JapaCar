<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JAPACAR - Login</title>
    <link rel="stylesheet" href="{{ asset('vendor/bootstrap/css/bootstrap.min.css') }}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="{{ asset('css/style.css') }}?v={{ @filemtime(public_path('css/style.css')) ?: '1' }}">
</head>
<body class="login-page">
<div class="login-wrapper">
    <div class="login-card">
        <div class="login-logo">JP</div>
        <h1>JAPACAR</h1>
        <p class="subtitle">Sistema de gestão da oficina</p>

        @if ($errors->any())
            <div class="alert alert-danger" role="alert">{{ $errors->first() }}</div>
        @endif

        <form action="{{ route('login') }}" method="post">
            @csrf
            <div class="mb-3">
                <label for="login" class="form-label-custom">Usuário</label>
                <input type="text" class="form-control" id="login" name="login" value="{{ old('login') }}"
                       autofocus required placeholder="Digite seu usuário" autocomplete="username">
            </div>
            <div class="mb-4">
                <label for="password" class="form-label-custom">Senha</label>
                <div class="input-group position-relative">
                    <input type="password" class="form-control" id="password" name="password" required
                           placeholder="Digite sua senha" autocomplete="current-password">
                    <button type="button" class="password-toggle" id="passwordToggle"
                            data-password-toggle="password" aria-label="Mostrar senha">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
            </div>
            <button type="submit" class="login-btn">
                <i class="bi bi-box-arrow-in-right me-1"></i> Entrar
            </button>
        </form>
    </div>
</div>
<script src="{{ asset('vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
<script src="{{ asset('js/app.js') }}"></script>
</body>
</html>
