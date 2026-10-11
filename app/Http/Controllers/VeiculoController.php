<?php

namespace App\Http\Controllers;

use App\Models\Cliente;
use App\Models\Veiculo;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class VeiculoController extends Controller
{
    public function index(Request $request)
    {
        $busca = trim((string) $request->query('q', ''));

        $veiculos = Veiculo::with('cliente')
            ->when($busca !== '', function ($query) use ($busca) {
                $query->where(function ($sub) use ($busca) {
                    $sub->where('placa', 'like', "%{$busca}%")
                        ->orWhere('modelo', 'like', "%{$busca}%")
                        ->orWhere('marca', 'like', "%{$busca}%")
                        ->orWhereHas('cliente', fn ($c) => $c->where('nome', 'like', "%{$busca}%"));
                });
            })
            ->orderBy('placa')
            ->paginate(20)
            ->withQueryString();

        return view('veiculos.index', compact('veiculos', 'busca'));
    }

    public function create()
    {
        return view('veiculos.form', [
            'veiculo' => new Veiculo,
            'clientes' => Cliente::where('ativo', true)->orderBy('nome')->get(),
        ]);
    }

    public function store(Request $request)
    {
        $veiculo = Veiculo::create($this->validados($request));

        return redirect()
            ->route('veiculos.index')
            ->with('status', "Veículo {$veiculo->placa} cadastrado.");
    }

    public function show(Veiculo $veiculo)
    {
        $veiculo->load(['cliente', 'checklistEntradas.fotos', 'atendimentos.orcamentos']);

        return view('veiculos.show', compact('veiculo'));
    }

    public function edit(Veiculo $veiculo)
    {
        return view('veiculos.form', [
            'veiculo' => $veiculo,
            'clientes' => Cliente::orderBy('nome')->get(),
        ]);
    }

    public function update(Request $request, Veiculo $veiculo)
    {
        $veiculo->update($this->validados($request, $veiculo));

        return redirect()->route('veiculos.show', $veiculo)->with('status', 'Veículo atualizado.');
    }

    /**
     * @return array<string, mixed>
     */
    private function validados(Request $request, ?Veiculo $veiculo = null): array
    {
        return $request->validate([
            'placa' => ['required', 'string', 'max:255', Rule::unique('veiculos', 'placa')->ignore($veiculo?->id)],
            'modelo' => ['required', 'string', 'max:255'],
            'marca' => ['required', 'string', 'max:255'],
            'ano' => ['nullable', 'integer', 'between:1900,2100'],
            'cor' => ['nullable', 'string', 'max:255'],
            'cliente_id' => ['required', 'integer', 'exists:clientes,id'],
        ]);
    }
}
