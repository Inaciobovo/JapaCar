@extends('layouts.app')

@section('titulo', $veiculo->placa)

@section('conteudo')
<div class="d-flex justify-content-between align-items-start mb-3">
    <div>
        <h1 class="h3 mb-1">
            <span class="badge bg-dark">{{ $veiculo->placa }}</span>
            {{ $veiculo->marca }} {{ $veiculo->modelo }}
        </h1>
        <div class="text-muted">
            Cliente: {{ $veiculo->cliente->nome }}
            @if ($veiculo->ano) · Ano {{ $veiculo->ano }} @endif
            @if ($veiculo->cor) · {{ $veiculo->cor }} @endif
        </div>
    </div>
    <div>
        <a class="btn btn-outline-secondary" href="{{ route('veiculos.edit', $veiculo) }}">Editar</a>
        <a class="btn btn-dark" href="{{ route('checklists.create', ['veiculo_id' => $veiculo->id]) }}">Novo checklist</a>
        <a class="btn btn-dark" href="{{ route('atendimentos.create', ['veiculo_id' => $veiculo->id]) }}">Novo atendimento</a>
    </div>
</div>

<h2 class="h5 mt-4">Checklists de entrada</h2>
@forelse ($veiculo->checklistEntradas->sortByDesc('data_entrada') as $checklist)
    <div class="card p-3 mb-2">
        <div class="d-flex justify-content-between">
            <div>
                <strong>{{ $checklist->data_entrada?->format('d/m/Y H:i') }}</strong>
                <span class="text-muted">
                    · {{ $checklist->quilometragem ? number_format($checklist->quilometragem, 0, ',', '.') . ' km' : 'km não informado' }}
                    · Combustível: {{ $checklist->nivelCombustivelDescricao() ?? '—' }}
                </span>
                <div>{{ $checklist->observacoes_gerais }}</div>
            </div>
            <a class="btn btn-sm btn-outline-secondary align-self-start" href="{{ route('checklists.edit', $checklist) }}">Editar</a>
        </div>
        @if ($checklist->fotos->isNotEmpty())
            <div class="d-flex gap-2 mt-2 flex-wrap">
                @foreach ($checklist->fotos as $foto)
                    <img class="thumb" src="{{ route('checklists.fotos.arquivo', $foto) }}" alt="Foto do checklist">
                @endforeach
            </div>
        @endif
    </div>
@empty
    <p class="text-muted">Nenhum checklist registrado.</p>
@endforelse

<h2 class="h5 mt-4">Atendimentos</h2>
@forelse ($veiculo->atendimentos->sortByDesc('created_at') as $atendimento)
    <div class="card p-3 mb-2 d-flex justify-content-between flex-row align-items-center">
        <div>
            <a href="{{ route('atendimentos.show', $atendimento) }}#">Atendimento #{{ $atendimento->id }}</a>
            <span class="badge bg-{{ $atendimento->finalizado() ? 'success' : 'warning' }}">{{ $atendimento->statusDescricao() }}</span>
        </div>
        <a class="btn btn-sm btn-outline-secondary" href="{{ route('atendimentos.show', $atendimento) }}">Abrir</a>
    </div>
@empty
    <p class="text-muted">Nenhum atendimento registrado.</p>
@endforelse
@endsection
