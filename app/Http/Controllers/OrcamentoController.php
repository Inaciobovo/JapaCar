<?php

namespace App\Http\Controllers;

use App\Models\Atendimento;
use App\Models\ItemServico;
use App\Models\Orcamento;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class OrcamentoController extends Controller
{
    public function create(Request $request)
    {
        $atendimento = Atendimento::with('veiculo.cliente')->findOrFail($request->integer('atendimento_id'));

        return view('orcamentos.form', [
            'atendimento' => $atendimento,
            'orcamento' => new Orcamento(['valor_mao_de_obra' => 0]),
        ]);
    }

    public function store(Request $request)
    {
        $dados = $request->validate([
            'atendimento_id' => ['required', 'integer', 'exists:atendimentos,id'],
            'valor_mao_de_obra' => ['required', 'numeric', 'min:0'],
            'observacoes' => ['nullable', 'string', 'max:255'],
        ]);

        $orcamento = Orcamento::create([
            'atendimento_id' => $dados['atendimento_id'],
            'valor_mao_de_obra' => $dados['valor_mao_de_obra'],
            'valor_pecas' => 0,
            'valor_total' => $dados['valor_mao_de_obra'],
            'status' => 'PENDENTE',
            'status_pagamento' => 'PENDENTE',
            'valor_pago' => 0,
            'observacoes' => $dados['observacoes'] ?? null,
        ]);

        return redirect()->route('orcamentos.show', $orcamento)->with('status', 'Orçamento criado.');
    }

    public function show(Orcamento $orcamento)
    {
        $orcamento->load(['atendimento.veiculo.cliente', 'itens']);

        return view('orcamentos.show', compact('orcamento'));
    }

    public function addItem(Request $request, Orcamento $orcamento)
    {
        $dados = $request->validate([
            'descricao' => ['required', 'string', 'max:500'],
            'quantidade' => ['required', 'integer', 'min:1', 'max:999'],
            'valor_unitario' => ['required', 'numeric', 'min:0'],
        ]);

        $orcamento->itens()->create($dados);

        $orcamento->load('itens');
        $orcamento->recalcularTotais();
        $orcamento->save();

        return back()->with('status', 'Item adicionado.');
    }

    public function removeItem(ItemServico $item)
    {
        $orcamento = $item->orcamento;
        $item->delete();

        $orcamento->load('itens');
        $orcamento->recalcularTotais();
        $orcamento->save();

        return back()->with('status', 'Item removido.');
    }

    public function registrarPagamento(Request $request, Orcamento $orcamento)
    {
        $dados = $request->validate([
            'valor_pago' => ['required', 'numeric', 'min:0'],
            'forma_pagamento' => ['required', Rule::in(array_keys(config('japacar.forma_pagamento')))],
            'data_pagamento' => ['required', 'date'],
        ]);

        $total = (float) $orcamento->valor_total;
        $pago = min((float) $dados['valor_pago'], $total);

        $orcamento->update([
            'valor_pago' => $pago,
            'forma_pagamento' => $dados['forma_pagamento'],
            'data_pagamento' => $dados['data_pagamento'],
            'status_pagamento' => $this->statusPara($pago, $total),
        ]);

        return back()->with('status', 'Pagamento registrado.');
    }

    private function statusPara(float $pago, float $total): string
    {
        if ($total > 0 && $pago >= $total) {
            return 'PAGO';
        }

        return $pago > 0 ? 'PARCIAL' : 'PENDENTE';
    }
}
