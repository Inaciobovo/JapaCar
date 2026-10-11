@extends('layouts.app')

@section('titulo', 'Alterar senha')

@section('conteudo')
<h1 class="h3 mb-4">Alterar senha</h1>

<div class="card p-4" style="max-width: 520px;">
    <form method="POST" action="{{ route('perfil.senha.update') }}">
        @csrf
        @method('PUT')
        <div class="mb-3">
            <label class="form-label">Senha atual</label>
            <input class="form-control" type="password" name="senha_atual" required>
            @error('senha_atual')<div class="text-danger small">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label class="form-label">Nova senha</label>
            <input class="form-control" type="password" name="senha" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Confirmar nova senha</label>
            <input class="form-control" type="password" name="senha_confirmation" required>
            <div class="form-text">Mínimo de 8 caracteres.</div>
        </div>
        <button class="btn btn-dark" type="submit">Salvar</button>
    </form>
</div>
@endsection
