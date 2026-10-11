<?php

namespace App\Http\Controllers;

use App\Models\Atendimento;
use App\Models\ChecklistEntrada;
use App\Models\Veiculo;
use Illuminate\Http\Request;

class AtendimentoController extends Controller
{
    public function index(Request $request)
    {
        $status = $request->query('status');

        $atendimentos = Atendimento::with('veiculo.cliente')
            ->when(in_array($status, ['EM_ANDAMENTO', 'FINALIZADO'], true), fn ($q) => $q->where('status', $status))
            ->latest()
            ->paginate(20)
            ->withQueryString();

        return view('atendimentos.index', compact('atendimentos', 'status'));
    }

    public function create(Request $request)
    {
        $veiculoId = $request->integer('veiculo_id') ?: null;

        return view('atendimentos.form', [
            'atendimento' => new Atendimento(['veiculo_id' => $veiculoId]),
            'veiculos' => Veiculo::with('cliente')->orderBy('placa')->get(),
            'checklists' => ChecklistEntrada::orderByDesc('data_entrada')->get(),
        ]);
    }

    public function store(Request $request)
    {
        $dados = $request->validate([
            'veiculo_id' => ['required', 'integer', 'exists:veiculos,id'],
            'checklist_entrada_id' => ['nullable', 'integer', 'exists:checklist_entradas,id'],
            'observacoes' => ['nullable', 'string', 'max:2000'],
        ]);

        $atendimento = Atendimento::create([
            'veiculo_id' => $dados['veiculo_id'],
            'checklist_entrada_id' => $dados['checklist_entrada_id'] ?? null,
            'status' => 'EM_ANDAMENTO',
            'observacoes' => $dados['observacoes'] ?? null,
        ]);

        return redirect()->route('atendimentos.show', $atendimento)->with('status', 'Atendimento aberto.');
    }

    public function show(Atendimento $atendimento)
    {
        $atendimento->load(['veiculo.cliente', 'checklistEntrada.fotos', 'orcamentos.itens']);

        return view('atendimentos.show', compact('atendimento'));
    }

    public function finalizar(Atendimento $atendimento)
    {
        if (! $atendimento->finalizado()) {
            $atendimento->update([
                'status' => 'FINALIZADO',
                'data_finalizacao' => now(),
            ]);
        }

        return back()->with('status', 'Atendimento finalizado.');
    }
}
