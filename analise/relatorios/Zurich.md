# Viabilidade técnica: Zurich

## Agência

| Item | Valor |
|---|---|
| Vagas elétricas (máx. de saídas) | 4 |
| Frota | 255 |
| Entrada existente | b3_75 (67.5 kW úteis) |
| Horário | Seg 08:00-20:00 · Ter 08:00-20:00 · Qua 08:00-20:00 · Qui 08:00-20:00 · Sex 08:00-20:00 · Sáb 08:00-14:00 · Dom fechado |
| Horas abertas por semana | 66 |
| Aberta na ponta (seg–sex 18–21h)? | Seg, Ter, Qua, Qui, Sex |

## Frota em T0

| Categoria | Modelo | Qtd |
|---|---|---|
| Bronze | JAC E-JS1 | 42 |
| Bronze | Renault Kwid E-Tech | 49 |
| Prata | BYD Dolphin Mini GS | 35 |
| Prata | Geely EX2 Pro | 23 |
| Ouro | BYD Dolphin GS | 49 |
| Ouro | MG4 Urban Comfort | 39 |
| Diamante | BYD Dolphin Plus | 11 |
| Diamante | Leapmotor B10 BEV | 7 |

Situação: em_contrato=226, estoque_pronto=29

## Demanda (janela pública, 4 semanas)

- **867 contratos**, média de 31.0 por dia; dia mais cheio: 82 retiradas.
- Duração do contrato: mediana 108.4 h (p10 24.5 h, p90 425.5 h).

| Categoria | Contratos | % do total |
|---|---|---|
| Bronze | 315 | 36% |
| Prata | 197 | 23% |
| Ouro | 291 | 34% |
| Diamante | 64 | 7% |

| Dia | Retiradas |
|---|---|
| Seg | 298 |
| Ter | 133 |
| Qua | 100 |
| Qui | 97 |
| Sex | 165 |
| Sáb | 74 |
| Dom | 0 |

Horas com mais retiradas: 18h (112), 09h (91), 16h (88), 17h (85).

## Energia a repor (estimativa)

Estimativa com a bateria e a autonomia **médias da categoria pedida** (o juiz usa o modelo que saiu, que pode ser um upgrade). Serve para dimensionar a potência; não substitui a simulação.

| Indicador | Valor |
|---|---|
| Devoluções com SOC < 80% (vão para a fila) | 866 de 867 (100%) |
| Devoluções com a agência fechada | 0 (só plugam na abertura) |
| Energia total na janela | 18,574 kWh |
| Média por dia | 663 kWh |
| Pior dia | 1,516 kWh |
| Potência média se carregasse 24 h | 27.6 kW |
| Potência média só nas horas abertas | 70.4 kW |
| Pior dia em 10 h de recarga | 151.6 kW |

Comparar com a entrada existente: **67.5 kW úteis**. Se a potência média passa perto do limite, a fila cresce e clientes se perdem.

## Carro × carregador (20% → 80%, sozinho, sem limite da agência)

Célula = kW médio · minutos. Em 2 saídas, cada carro recebe metade do nominal quando as duas estão ocupadas.

| Modelo | ac_7 | ac_11 | ac_22x2 | dc_30 | dc_60x2 | dc_120x2 |
|---|---|---|---|---|---|---|
| JAC E-JS1 (Bronze) | 6.6 · 171 | 6.6 · 171 | 6.6 · 171 | 18.5 · 61 | 18.5 · 61 | 18.5 · 61 |
| Renault Kwid E-Tech (Bronze) | 7.0 · 138 | 7.4 · 130 | 7.4 · 130 | 26.0 · 37 | 26.0 · 37 | 26.0 · 37 |
| BYD Dolphin Mini GS (Prata) | 6.6 · 212 | 6.6 · 212 | 6.6 · 212 | 30.0 · 47 | 36.8 · 38 | 36.8 · 38 |
| Geely EX2 Pro (Prata) | 6.6 · 213 | 6.6 · 213 | 6.6 · 213 | 30.0 · 47 | 56.1 · 25 | 60.9 · 23 |
| BYD Dolphin GS (Ouro) | 7.0 · 231 | 7.0 · 231 | 7.0 · 231 | 29.7 · 54 | 44.0 · 37 | 44.0 · 37 |
| MG4 Urban Comfort (Ouro) | 7.0 · 221 | 11.0 · 141 | 11.0 · 141 | 30.0 · 52 | 60.0 · 26 | 76.6 · 20 |
| BYD Dolphin Plus (Diamante) | 7.0 · 311 | 11.0 · 198 | 11.0 · 198 | 30.0 · 73 | 57.7 · 38 | 66.8 · 33 |
| Leapmotor B10 BEV (Diamante) | 7.0 · 289 | 11.0 · 184 | 11.0 · 184 | 30.0 · 67 | 59.4 · 34 | 93.0 · 22 |

**Leitura rápida:**
- JAC E-JS1: pico na curva AC 6.6 kW, DC 19.2 kW. DC-120 não acelera em relação ao DC-60 sozinho. DC-30 já entrega quase tudo. AC-22 não acelera em relação ao AC-11.
- Renault Kwid E-Tech: pico na curva AC 7.4 kW, DC 26.9 kW. DC-120 não acelera em relação ao DC-60 sozinho. DC-30 já entrega quase tudo. AC-22 não acelera em relação ao AC-11.
- BYD Dolphin Mini GS: pico na curva AC 6.6 kW, DC 38.1 kW. DC-120 não acelera em relação ao DC-60 sozinho. AC-22 não acelera em relação ao AC-11.
- Geely EX2 Pro: pico na curva AC 6.6 kW, DC 72.6 kW. AC-22 não acelera em relação ao AC-11.
- BYD Dolphin GS: pico na curva AC 7.0 kW, DC 58.3 kW. DC-120 não acelera em relação ao DC-60 sozinho. AC-22 não acelera em relação ao AC-11.
- MG4 Urban Comfort: pico na curva AC 11.0 kW, DC 80.0 kW. AC-22 não acelera em relação ao AC-11.
- BYD Dolphin Plus: pico na curva AC 11.0 kW, DC 79.6 kW. AC-22 não acelera em relação ao AC-11.
- Leapmotor B10 BEV: pico na curva AC 11.0 kW, DC 140.0 kW. AC-22 não acelera em relação ao AC-11.

## Entradas possíveis (nunca descer)

| Entrada | kW útil | Demanda contratada? | Comporta | Custo |
|---|---|---|---|---|
| b3_75 | 67.5 | não (B3) | 2× DC-30 ou 1× DC-60 cheios | existente (custo 0) |
| a4_150 | 135 | sim (30 até o teto, passo 10) | 4× DC-30 ou 2× DC-60 cheios | ampliação (custo cheio, H4) |
| a4_225 | 202.5 | sim (30 até o teto, passo 10) | 6× DC-30 ou 3× DC-60 cheios | ampliação (custo cheio, H4) |
| a4_300 | 270 | sim (30 até o teto, passo 10) | 9× DC-30 ou 4× DC-60 cheios | ampliação (custo cheio, H4) |
| se_500 | 450 | sim (30 até o teto, passo 10) | 15× DC-30 ou 7× DC-60 cheios | ampliação (custo cheio, H4) |
| se_750 | 675 | sim (30 até o teto, passo 10) | 22× DC-30 ou 11× DC-60 cheios | ampliação (custo cheio, H4) |
| se_1000 | 900 | sim (30 até o teto, passo 10) | 30× DC-30 ou 15× DC-60 cheios | ampliação (custo cheio, H4) |
| se_1500 | 1350 | sim (30 até o teto, passo 10) | 45× DC-30 ou 22× DC-60 cheios | ampliação (custo cheio, H4) |
| se_2000 | 1800 | sim (30 até o teto, passo 10) | 60× DC-30 ou 30× DC-60 cheios | ampliação (custo cheio, H4) |

## Hipóteses para a busca (conferir no simulador)

1. Saídas: no máximo 4. Começar pela energia/dia e testar de 1 a 4 saídas.
2. Entrada: a existente (67.5 kW) é grátis. Só ampliar se a simulação mostrar perdas que valem mais que a obra (H4) mais a demanda contratada.
3. Política: `evitar_ponta` pode valer a pena (agência aberta na ponta); medir os clientes perdidos.
4. `divisao: prioridade` concentra potência: bom quando o limite é apertado e há retiradas logo em seguida.
5. `proxima_retirada` tende a servir melhor os contratos do dia seguinte; comparar com `menor_soc`.
