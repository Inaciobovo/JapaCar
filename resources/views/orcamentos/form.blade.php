@extends('layouts.app')

@section('titulo', 'Novo orçamento')

@section('conteudo')
<h1 class="h3 mb-1">Novo orçamento</h1>
<p class="text-muted">
    Atendimento #{{ $atendimento->id }} ·
    <span class="badge bg-dark">{{ $atendimento->veiculo->placa }}</span>
    {{ $atendimento->veiculo->marca }} {{ $atendimento->veiculo->modelo }} ·
    {{ $atendimento->veiculo->cliente->nome }}
</p>

<form method="POST" action="{{ route('orcamentos.store') }}">
    @csrf
    <input type="hidden" name="atendimento_id" value="{{ $atendimento->id }}">

    <div class="card p-4">
        <div class="row g-3">
            <div class="col-md-4">
                <label class="form-label">Mão de obra (R$)</label>
                <input class="form-control" type="number" step="0.01" min="0" name="valor_mao_de_obra"
                       value="{{ old('valor_mao_de_obra', '0.00') }}" required>
            </div>
            <div class="col-md-8">
                <label class="form-label">Observações</label>
                <input class="form-control" name="observacoes" value="{{ old('observacoes') }}">
            </div>
        </div>
        <div class="form-text mt-2">As peças/itens são adicionados depois, na tela do orçamento.</div>
    </div>

    <div class="mt-3">
        <button class="btn btn-dark" type="submit">Criar orçamento</button>
        <a class="btn btn-outline-secondary" href="{{ route('atendimentos.show', $atendimento) }}">Cancelar</a>
    </div>
</form>
@endsection
