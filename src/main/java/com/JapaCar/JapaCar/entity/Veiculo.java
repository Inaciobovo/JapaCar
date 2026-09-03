package com.JapaCar.JapaCar.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
public class Veiculo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true)
    private String placa;

    private String modelo;
    private String ano;
    private String manutencaoNecessaria;

    @ManyToOne
    @JoinColumn(name = "cliente_id")
    private Cliente cliente;
}
