<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules\Password;

class PerfilController extends Controller
{
    public function editSenha()
    {
        return view('perfil.senha');
    }

    public function updateSenha(Request $request)
    {
        $dados = $request->validate([
            'senha_atual' => ['required', 'string'],
            'senha' => ['required', 'confirmed', Password::min(8)],
        ]);

        $usuario = $request->user();

        if (! Hash::check($dados['senha_atual'], $usuario->password)) {
            return back()->withErrors(['senha_atual' => 'A senha atual não confere.']);
        }

        $usuario->update(['password' => $dados['senha']]);

        return back()->with('status', 'Senha alterada com sucesso.');
    }
}
