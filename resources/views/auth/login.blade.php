<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Entrar · JAPACAR</title>
    <link rel="stylesheet" href="{{ asset('vendor/bootstrap/css/bootstrap.min.css') }}">
    <style>body { background: #212529; }</style>
</head>
<body class="d-flex align-items-center" style="min-height: 100vh;">
<div class="container" style="max-width: 420px;">
    <div class="card p-4">
        <h1 class="h4 mb-1 text-center">JAPACAR</h1>
        <p class="text-muted text-center mb-4">Gestão de oficina</p>

        @if ($errors->any())
            <div class="alert alert-danger">{{ $errors->first() }}</div>
        @endif

        <form method="POST" action="{{ route('login') }}">
            @csrf
            <div class="mb-3">
                <label class="form-label" for="login">Login</label>
                <input class="form-control" id="login" name="login" value="{{ old('login') }}" autofocus required>
            </div>
            <div class="mb-3">
                <label class="form-label" for="password">Senha</label>
                <input class="form-control" type="password" id="password" name="password" required>
            </div>
            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" id="remember" name="remember" value="1">
                <label class="form-check-label" for="remember">Manter conectado</label>
            </div>
            <button class="btn btn-dark w-100" type="submit">Entrar</button>
        </form>
    </div>
</div>
<script src="{{ asset('vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
</body>
</html>
