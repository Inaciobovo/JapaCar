<?php

use App\Http\Controllers\AtendimentoController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\ChecklistController;
use App\Http\Controllers\ClienteController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\OrcamentoController;
use App\Http\Controllers\PerfilController;
use App\Http\Controllers\VeiculoController;
use Illuminate\Support\Facades\Route;

Route::get('/', fn () => redirect()->route('atendimentos.index'));

Route::middleware('guest')->group(function () {
    Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
    Route::post('/login', [AuthController::class, 'login'])->middleware('throttle:login');
});

Route::middleware('auth')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

    Route::get('/painel', [DashboardController::class, 'index'])->name('painel');

    Route::get('/perfil/senha', [PerfilController::class, 'editSenha'])->name('perfil.senha.edit');
    Route::put('/perfil/senha', [PerfilController::class, 'updateSenha'])->name('perfil.senha.update');

    Route::prefix('clientes')->name('clientes.')->group(function () {
        Route::get('/', [ClienteController::class, 'index'])->name('index');
        Route::get('/novo', [ClienteController::class, 'create'])->name('create');
        Route::post('/', [ClienteController::class, 'store'])->name('store');
        Route::get('/{cliente}/editar', [ClienteController::class, 'edit'])->name('edit');
        Route::put('/{cliente}', [ClienteController::class, 'update'])->name('update');
        Route::post('/{cliente}/inativar', [ClienteController::class, 'inativar'])->name('inativar');
    });

    Route::prefix('veiculos')->name('veiculos.')->group(function () {
        Route::get('/', [VeiculoController::class, 'index'])->name('index');
        Route::get('/novo', [VeiculoController::class, 'create'])->name('create');
        Route::post('/', [VeiculoController::class, 'store'])->name('store');
        Route::get('/{veiculo}', [VeiculoController::class, 'show'])->name('show');
        Route::get('/{veiculo}/editar', [VeiculoController::class, 'edit'])->name('edit');
        Route::put('/{veiculo}', [VeiculoController::class, 'update'])->name('update');
    });

    Route::prefix('checklists')->name('checklists.')->group(function () {
        Route::get('/', [ChecklistController::class, 'index'])->name('index');
        Route::get('/novo', [ChecklistController::class, 'create'])->name('create');
        Route::post('/', [ChecklistController::class, 'store'])->name('store');
        Route::get('/{checklist}', [ChecklistController::class, 'show'])->name('show');
        Route::get('/{checklist}/editar', [ChecklistController::class, 'edit'])->name('edit');
        Route::put('/{checklist}', [ChecklistController::class, 'update'])->name('update');
        Route::post('/{checklist}/fotos', [ChecklistController::class, 'addFoto'])->name('fotos.store');
        Route::get('/fotos/{foto}/arquivo', [ChecklistController::class, 'serveFoto'])->name('fotos.arquivo');
        Route::post('/fotos/{foto}/remover', [ChecklistController::class, 'removeFoto'])->name('fotos.destroy');
    });

    Route::prefix('atendimentos')->name('atendimentos.')->group(function () {
        Route::get('/', [AtendimentoController::class, 'index'])->name('index');
        Route::get('/novo', [AtendimentoController::class, 'create'])->name('create');
        Route::post('/', [AtendimentoController::class, 'store'])->name('store');
        Route::get('/{atendimento}', [AtendimentoController::class, 'show'])->name('show');
        Route::post('/{atendimento}/finalizar', [AtendimentoController::class, 'finalizar'])->name('finalizar');
    });

    Route::prefix('orcamentos')->name('orcamentos.')->group(function () {
        Route::get('/', [OrcamentoController::class, 'index'])->name('index');
        Route::get('/novo', [OrcamentoController::class, 'create'])->name('create');
        Route::post('/', [OrcamentoController::class, 'store'])->name('store');
        Route::get('/{orcamento}', [OrcamentoController::class, 'show'])->name('show');
        Route::post('/{orcamento}/itens', [OrcamentoController::class, 'addItem'])->name('itens.store');
        Route::post('/itens/{item}/remover', [OrcamentoController::class, 'removeItem'])->name('itens.destroy');
        Route::post('/{orcamento}/pagamento', [OrcamentoController::class, 'registrarPagamento'])->name('pagamento');
    });
});
