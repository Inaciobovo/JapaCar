<?php

namespace App\Providers;

use App\Support\Japacar;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\View;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Register any application services.
     */
    public function boot(): void
    {
        View::share('deviceClass', Japacar::deviceClass());
        View::share('isMobile', Japacar::isMobile());

        View::composer('*', function ($view) {
            $usuario = auth()->user();
            $rotaAtual = request()->route()?->getName() ?? '';

            $view->with([
                'usuario' => $usuario,
                'podeVerFinanceiro' => (bool) $usuario?->isAdmin(),
                'activePage' => match (true) {
                    str_starts_with($rotaAtual, 'clientes') => 'clientes',
                    str_starts_with($rotaAtual, 'veiculos') => 'veiculos',
                    str_starts_with($rotaAtual, 'checklists') => 'checklists',
                    str_starts_with($rotaAtual, 'atendimentos') => 'atendimentos',
                    str_starts_with($rotaAtual, 'orcamentos') => 'orcamentos',
                    str_starts_with($rotaAtual, 'painel') => 'dashboard',
                    default => 'atendimentos',
                },
            ]);
        });

        // Duas janelas de proteção no login: por (login + IP) e por IP,
        // para frear força bruta em uma conta e varredura de várias contas.
        RateLimiter::for('login', function (Request $request) {
            $chave = mb_strtolower((string) $request->input('login'));

            return [
                Limit::perMinute(5)->by($chave.'|'.$request->ip()),
                Limit::perMinute(20)->by($request->ip()),
            ];
        });
    }
}
