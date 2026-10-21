# Leitura da Neblina em Bangkok (testes grátis)

Objetivo: descobrir **quanto** cada item pesa na nota antes de H4, usando pares de testes que diferem em **uma coisa só**. Bangkok custa 0 m7Coins (cooldown de 1 min).

```
nota = w_certo·certos + w_upg·upgrades − w_perd·não_atendidos − w_dem·demanda_kW − w_ponta·kWh_ponta − w_obra·custo_obra
```

**Não entram na nota:** `pico_kw`, `energia_kwh` e `atendimento_pct` são só informativos (regulamento 8.1). Em B3 também não há demanda contratada.

## Rodar (P1, na raiz do repositório)

```bash
py operacao/juiz.py teste Bangkok kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E1_base.json --completo
```

Repita para cada arquivo (1 por minuto). Com `--completo`, o juiz devolve a série de potência em 15 min, e dá para conferir a energia na ponta do próprio juiz somando as janelas das 18h às 21h, seg–sex.

## Previsão do nosso motor (conferir se o juiz concorda)

| Teste | Configuração | Certos | Upg. | Perdidos | Ponta (kWh) | Nota do juiz |
|---|---|---|---|---|---|---|
| E1 | 2× AC-7 + DC-30 | 271 | 0 | 0 | 101,1 | 65 (?) |
| E2 | E1 + `evitar_ponta` | 271 | 0 | 0 | 0 | |
| E3 | 1× DC-30 + evitar | 271 | 0 | 0 | 0 | |
| E4 | 1× DC-30 | 271 | 0 | 0 | 63,6 | |
| E5 | 1× DC-60 (2 saídas) + evitar | 271 | 0 | 0 | 0 | |
| E6 | 1× DC-30 em b3_75 + evitar | 271 | 0 | 0 | 0 | |
| E7 | 1× AC-7 + evitar | 88 | 22 | 161 | 0 | |
| E8 | 3× AC-7 + evitar | 267 | 2 | 2 | 0 | |

Se `atendimento_pct` do juiz for diferente do nosso, o motor diverge: rodar `comparar.py` antes de inferir pesos.

## Contas (todas com o resto igual)

| Par | O que muda | Fórmula |
|---|---|---|
| E2 − E1 | só a energia na ponta (101,1 kWh) | `w_ponta = (nota_E2 − nota_E1) / 101,1` |
| E3 − E4 | só a energia na ponta (63,6 kWh), confirmação | `w_ponta = (nota_E3 − nota_E4) / 63,6` |
| E3 − E2 | tira 2× AC-7 | `w_obra·custo(ac_7) = (nota_E3 − nota_E2) / 2` |
| E5 − E3 | troca DC-30 por DC-60 | `w_obra·[custo(dc_60x2) − custo(dc_30)] = nota_E3 − nota_E5` |
| E6 − E3 | amplia a entrada para b3_75 | `w_obra·custo(b3_75) = nota_E3 − nota_E6` |
| E8 − E7 | +2× AC-7, e 179 certos a mais | `nota_E8 − nota_E7 + 2·[w_obra·custo(ac_7)]` = valor de atender 179 clientes a mais (com upgrades e perdidos) |

Como `certos + upgrades + perdidos = 271` é fixo, a nota só identifica **diferenças**: quanto vale trocar um perdido por um certo e um upgrade por um certo. É o que basta para decidir.

**Atenção:** os custos de obra são do catálogo (iguais em todas as agências), mas **os pesos podem ser diferentes por agência**. O que for inferido em Bangkok vale como estimativa; confirmar em H4.

Anotar tudo em `registro/registro_decisoes.md` (tabela "Leitura da Neblina"). Isso vale o prêmio de melhor leitura da Neblina.
