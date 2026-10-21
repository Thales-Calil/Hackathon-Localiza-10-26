# Hipóteses de Istanbul

> Geradas em 21/10 na fase Clara, com o catálogo oficial (custos e pesos). As notas abaixo são do **nosso motor**, que bateu exatamente com o juiz em Bangkok (E1, E8, H09, H13). **Nenhuma foi testada no juiz:** em Istanbul, cada teste custa m7Coins (placar 20, completo 50), e o envio final é decisão da equipe.

## Istanbul em números

- **Vagas e horário:** 4 vagas elétricas, aberta **24 h** todos os dias. A ponta (seg–sex, 18–21h) cai com a agência aberta.
- **Demanda:** 1.293 contratos (46 por dia, pico de 72) e ~1.140 kWh por dia a repor.
- **Entrada existente:** b3_45 (40,5 kW). Ampliar para b3_75 custa 5.000.
- **Pesos:** certo +15 · upgrade +8 · perdido −200 · demanda −2/kW · ponta −0,5/kWh · obra −1.

## Simular

```bash
cd kit_kickoff/kit_kickoff
py simular.py submissoes/neblina_istanbul/I01_base_ac7x3_dc30_b3_75.json
```

Para ver todas em ranking: `py analise/nota_local.py kit_kickoff/kit_kickoff/submissoes/neblina_istanbul`, na raiz do repositório.

## Hipóteses (uma mudança por vez em relação à base I01)

> Atualizado depois do teste pago da equipe em Istanbul (taxa 20): o juiz deu **8.381,19** para a I01, revelando uma regra que o motor não tinha (o estoque de T0 entra todo na fila antes de plugar). O motor foi corrigido e agora **reproduz a I01 exatamente** (1.288/3/2, energia 27.538,287 kWh). As demais notas abaixo já usam o motor corrigido.

| ID | Mudança em relação à I01 | Certos/Upg/Perd | Ponta kWh | Obra | **Nota prevista** | Δ vs I01 |
|---|---|---|---|---|---|---|
| **I03** | prioridade `chegada` | 1.290/1/2 | 2.576 | 9.250 | **8.420** | **+39** |
| I01 | **base:** 3× AC-7 + 1× DC-30 · b3_75 · `proxima_retirada`/igual | 1.288/3/2 | 2.626 | 9.250 | **8.381 ✔ juiz** | — |
| I10 | AC-22 + AC-7 + DC-30 | 1.292/1/0 | 2.608 | 10.250 | 7.834 | −547 |
| I02 | + `evitar_ponta` | 1.245/35/13 | 0 | 9.250 | 7.105 | −1.276 |
| I06 | a4_150 com demanda 60 | 1.288/3/2 | 2.626 | 10.750 | 6.761 | −1.620 |
| I04 | prioridade `menor_soc` | 1.279/3/11 | 2.658 | 9.250 | 6.430 | −1.951 |
| I08 | 2× AC-7 + DC-60 | 1.292/0/1 | 2.754 | 12.800 | 5.003 | −3.378 |
| I07 | tira 1 AC-7 | 1.189/69/35 | 2.441 | 9.000 | 1.166 | −7.215 |
| I05 | não amplia a entrada (b3_45) | 1.157/78/58 | 2.374 | 4.250 | 942 | −7.439 |
| I09 | só 4× AC-7, sem DC | 566/284/443 | 1.644 | 6.000 | −84.660 | −93.041 |

## Conclusões

1. **Melhor até agora: I03** (3× AC-7 + DC-30, b3_75, `chegada`), com **8.420** previstos, 39 acima da I01 testada. A busca completa com o motor corrigido está rodando e pode achar algo melhor.
2. **A ampliação para b3_75 se paga** (I05), **cada AC-7 vale muito mais do que custa** (I07) e **`evitar_ponta` não compensa em agência 24 h** (I02).
3. **A diferença entre as prioridades é pequena em Istanbul:** `chegada` e `proxima_retirada` perdem 2 clientes cada.

## Riscos para as semanas ocultas

- **Margem curta:** com só 2 perdidos na janela pública, um pico um pouco maior nas semanas ocultas pode gerar mais perdidos (−215 cada). A I10 (0 perdidos, ~550 pontos a menos) é a alternativa "com folga".
- **Evento:** um evento em Istanbul (ex.: corte na entrada) reduziria o limite de 67,5 kW. O pico da I01 é 51 kW, então há ~25% de folga.

## Se a equipe decidir conferir no juiz (pago)

Testar **só a I01, em placar** (20 m7Coins), e conferir se a nota bate com 8.826:

```bash
py operacao/juiz.py teste Istanbul kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I01_base_ac7x3_dc30_b3_75.json --sim
```

Depois, `py analise/hipoteses.py checar I01` registra a comparação no caderno.
