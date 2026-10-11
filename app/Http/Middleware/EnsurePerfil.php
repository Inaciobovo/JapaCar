<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsurePerfil
{
    /**
     * Restringe a rota aos perfis informados (ex.: perfil:ADMIN).
     */
    public function handle(Request $request, Closure $next, string ...$perfis): Response
    {
        $usuario = $request->user();

        if ($usuario === null || ! in_array($usuario->perfil, $perfis, true)) {
            abort(403, 'Acesso restrito.');
        }

        return $next($request);
    }
}
