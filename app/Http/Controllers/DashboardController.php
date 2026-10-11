<?php

namespace App\Http\Controllers;

use App\Models\Atendimento;
use App\Models\ChecklistEntrada;
use App\Models\Cliente;
use App\Models\Orcamento;
use App\Models\Veiculo;

class DashboardController extends Controller
{
    public function index()
    {
        return view('painel', [
            'totalClientes' => Cliente::where('ativo', true)->count(),
            'totalVeiculos' => Veiculo::count(),
            'totalChecklists' => ChecklistEntrada::count(),
            'atendimentosAbertos' => Atendimento::where('status', 'EM_ANDAMENTO')->count(),
            'orcamentosPendentes' => Orcamento::where('status', 'PENDENTE')->count(),
            'atendimentos' => Atendimento::with('veiculo.cliente')
                ->where('status', 'EM_ANDAMENTO')
                ->latest()
                ->limit(8)
                ->get(),
        ]);
    }
}
