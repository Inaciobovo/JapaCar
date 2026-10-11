<?php

return [
    'oficina' => [
        'nome' => env('OFICINA_NOME', 'JAPACAR'),
        'subtitulo' => env('OFICINA_SUBTITULO', 'Oficina Mecânica'),
        'telefone' => env('OFICINA_TELEFONE', ''),
        'endereco' => env('OFICINA_ENDERECO', ''),
    ],

    'perfis' => [
        'ADMIN' => 'Administrador',
        'MECANICO' => 'Mecânico',
    ],

    'status_atendimento' => [
        'EM_ANDAMENTO' => 'Em andamento',
        'FINALIZADO' => 'Finalizado',
    ],

    'status_orcamento' => [
        'PENDENTE' => 'Pendente',
        'APROVADO' => 'Aprovado',
        'RECUSADO' => 'Recusado',
    ],

    'status_pagamento' => [
        'PENDENTE' => 'Pendente',
        'PARCIAL' => 'Parcial',
        'PAGO' => 'Pago',
    ],

    'forma_pagamento' => [
        'DINHEIRO' => 'Dinheiro',
        'PIX' => 'Pix',
        'CARTAO_DEBITO' => 'Cartão de débito',
        'CARTAO_CREDITO' => 'Cartão de crédito',
        'TRANSFERENCIA' => 'Transferência',
        'BOLETO' => 'Boleto',
        'OUTROS' => 'Outros',
    ],

    'nivel_combustivel' => [
        'CHEIO' => 'Tanque cheio',
        'TRES_QUARTOS' => '3/4 - Três quartos',
        'METADE' => '1/2 - Metade',
        'UM_QUARTO' => '1/4 - Um quarto',
        'RESERVA' => 'Reserva',
        'VAZIO' => 'Vazio',
    ],
];
