package com.JapaCar.JapaCar.dto;

public record VeiculoRequestDTO(
        String placa,
        String modelo,
        Integer ano,
        String manutencaoNecessaria,
        Long clienteId
) {}