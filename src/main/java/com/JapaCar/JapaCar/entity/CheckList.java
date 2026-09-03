package com.JapaCar.JapaCar.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.ManyToAny;

import java.time.LocalDateTime;

@Getter
@Setter
@Entity
public class CheckList {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String mecanicoResponsavel;
    private String observacoes;
    private LocalDateTime dataCriacao;

    @ManyToAny
    @JoinColumn(name = "veiculo_id")
    private Veiculo veiculo;

}