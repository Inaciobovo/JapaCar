@extends('layouts.app')

@section('titulo', 'Painel')

@section('conteudo')
<h1 class="h3 mb-4">Painel</h1>
<div class="row g-3">
    <div class="col-md-4">
        <div class="card p-4">
            <div class="text-muted">Clientes ativos</div>
            <div class="display-6">{{ $totalClientes }}</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card p-4">
            <div class="text-muted">Veículos</div>
            <div class="display-6">{{ $totalVeiculos }}</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card p-4">
            <div class="text-muted">Atendimentos abertos</div>
            <div class="display-6">{{ $atendimentosAbertos }}</div>
        </div>
    </div>
</div>
@endsection
