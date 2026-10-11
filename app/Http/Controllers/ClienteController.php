<?php

namespace App\Http\Controllers;

use App\Models\Cliente;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class ClienteController extends Controller
{
    public function index(Request $request)
    {
        $busca = trim((string) $request->query('q', ''));

        $clientes = Cliente::query()
            ->when($busca !== '', function ($query) use ($busca) {
                $query->where(function ($sub) use ($busca) {
                    $sub->where('nome', 'like', "%{$busca}%")
                        ->orWhere('cpf', 'like', "%{$busca}%")
                        ->orWhere('telefone', 'like', "%{$busca}%");
                });
            })
            ->orderBy('nome')
            ->paginate(20)
            ->withQueryString();

        return view('clientes.index', compact('clientes', 'busca'));
    }

    public function create()
    {
        return view('clientes.form', ['cliente' => new Cliente]);
    }

    public function store(Request $request)
    {
        $cliente = Cliente::create($this->validados($request));

        return redirect()
            ->route('clientes.index')
            ->with('status', "Cliente \"{$cliente->nome}\" criado.");
    }

    public function edit(Cliente $cliente)
    {
        return view('clientes.form', compact('cliente'));
    }

    public function update(Request $request, Cliente $cliente)
    {
        $cliente->update($this->validados($request, $cliente));

        return redirect()->route('clientes.index')->with('status', 'Cliente atualizado.');
    }

    public function inativar(Cliente $cliente)
    {
        $cliente->update(['ativo' => ! $cliente->ativo]);

        return back()->with('status', $cliente->ativo ? 'Cliente reativado.' : 'Cliente inativado.');
    }

    /**
     * @return array<string, mixed>
     */
    private function validados(Request $request, ?Cliente $cliente = null): array
    {
        $dados = $request->validate([
            'nome' => ['required', 'string', 'max:255'],
            'cpf' => ['nullable', 'string', 'max:255', Rule::unique('clientes', 'cpf')->ignore($cliente?->id)],
            'telefone' => ['nullable', 'string', 'max:255'],
            'email' => ['nullable', 'email', 'max:255'],
            'endereco' => ['nullable', 'string', 'max:255'],
        ]);

        $dados['cpf'] = $dados['cpf'] ?? null;

        return $dados;
    }
}
