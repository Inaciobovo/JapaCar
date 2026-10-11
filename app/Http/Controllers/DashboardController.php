<?php

namespace App\Http\Controllers;

use App\Models\Atendimento;
use App\Models\Cliente;
use App\Models\Veiculo;

class DashboardController extends Controller
{
    public function index()
    {
        return view('painel', [
            'totalClientes' => Cliente::where('ativo', true)->count(),
            'totalVeiculos' => Veiculo::count(),
            'atendimentosAbertos' => Atendimento::where('status', 'EM_ANDAMENTO')->count(),
        ]);
    }
}
