<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
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
