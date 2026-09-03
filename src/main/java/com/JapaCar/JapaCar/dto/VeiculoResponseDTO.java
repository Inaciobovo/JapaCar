package com.JapaCar.JapaCar.dto;

public record VeiculoResponseDTO(
        Long id,
        String placa,
        String modelo,
        Integer ano,
        String manutencaoNecessaria,
        String nomeCliente
) {}