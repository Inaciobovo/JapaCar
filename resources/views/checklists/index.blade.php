@extends('layouts.app')

@section('titulo', 'Checklists')

@section('conteudo')
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h3 mb-0">Checklists de entrada</h1>
    <a class="btn btn-dark" href="{{ route('checklists.create') }}">Novo checklist</a>
</div>

<div class="card">
    <table class="table mb-0 align-middle">
        <thead>
        <tr>
            <th>Data</th>
            <th>Veículo</th>
            <th>Cliente</th>
            <th>Km</th>
            <th>Fotos</th>
            <th class="text-end">Ações</th>
        </tr>
        </thead>
        <tbody>
        @forelse ($checklists as $checklist)
            <tr>
                <td>{{ $checklist->data_entrada?->format('d/m/Y H:i') }}</td>
                <td>
                    <a href="{{ route('veiculos.show', $checklist->veiculo) }}">
                        {{ $checklist->veiculo->placa }}
                    </a>
                    <div class="text-muted small">{{ $checklist->veiculo->marca }} {{ $checklist->veiculo->modelo }}</div>
                </td>
                <td>{{ $checklist->veiculo->cliente->nome }}</td>
                <td>{{ $checklist->quilometragem ? number_format($checklist->quilometragem, 0, ',', '.') : '—' }}</td>
                <td><span class="badge bg-secondary">{{ $checklist->fotos_count ?? $checklist->fotos->count() }}</span></td>
                <td class="text-end">
                    <a class="btn btn-sm btn-outline-secondary" href="{{ route('checklists.edit', $checklist) }}">Editar</a>
                </td>
            </tr>
        @empty
            <tr><td colspan="6" class="text-center text-muted py-4">Nenhum checklist registrado.</td></tr>
        @endforelse
        </tbody>
    </table>
</div>

<div class="mt-3">{{ $checklists->links() }}</div>
@endsection
