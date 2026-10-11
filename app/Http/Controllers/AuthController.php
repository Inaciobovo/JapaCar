<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    public function showLogin()
    {
        return view('auth.login');
    }

    public function login(Request $request)
    {
        $dados = $request->validate([
            'login' => ['required', 'string'],
            'password' => ['required', 'string'],
        ]);

        $autenticado = Auth::attempt([
            'login' => $dados['login'],
            'password' => $dados['password'],
            'ativo' => true,
        ], $request->boolean('remember'));

        if (! $autenticado) {
            throw ValidationException::withMessages([
                'login' => 'Login ou senha inválidos, ou usuário inativo.',
            ]);
        }

        $request->session()->regenerate();

        return redirect()->intended(route('atendimentos.index'));
    }

    public function logout(Request $request)
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('login');
    }
}
