@extends('layouts.app')

@section('titulo', 'Alterar Senha')

@section('conteudo')
<div class="d-flex align-items-center mb-2">
    <a href="{{ route('atendimentos.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title mb-0">Alterar Senha</h1>
</div>
<p class="page-subtitle">Defina uma nova senha de acesso ao sistema</p>

@include('fragments.alerts')

<form action="{{ route('perfil.senha.update') }}" method="post" class="form-card">
    @csrf
    @method('PUT')

    <div class="mb-3">
        <label class="form-label-custom">Senha atual *</label>
        <input type="password" name="senha_atual" class="form-control" required autocomplete="current-password">
    </div>
    <div class="mb-3">
        <label class="form-label-custom">Nova senha *</label>
        <input type="password" name="senha" class="form-control" required autocomplete="new-password">
        <div class="form-text">Mínimo de 8 caracteres.</div>
    </div>
    <div class="mb-3">
        <label class="form-label-custom">Confirmar nova senha *</label>
        <input type="password" name="senha_confirmation" class="form-control" required autocomplete="new-password">
    </div>

    <div class="form-actions">
        <button type="submit" class="btn btn-japacar">
            <i class="bi bi-check-lg me-1"></i> Salvar senha
        </button>
        <a href="{{ route('atendimentos.index') }}" class="btn btn-outline-secondary">
            <i class="bi bi-x-lg me-1"></i> Cancelar
        </a>
    </div>
</form>
@endsection
