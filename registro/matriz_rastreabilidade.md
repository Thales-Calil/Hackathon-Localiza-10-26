# Matriz de rastreabilidade da nota

> Gerado por `py analise/nota_local.py`. Liga cada item da nota (regulamento 8.1) à regra do motor que produz a
> métrica, ao peso e ao custo usados (com a fonte) e ao valor que o juiz devolveu para a mesma submissão.

## 1. Origem dos pesos

| Agência | Item | Peso | Fonte |
|---|---|---|---|
| Bangkok | certo | 15 | GET /catalogo (fase clara, 21/10); confere com a cascata de E1 e E8 |
| Bangkok | upgrade | 8 | GET /catalogo (fase clara, 21/10); confere com a cascata de E1 e E8 |
| Bangkok | nao_atendido | -200 | GET /catalogo (fase clara, 21/10); confere com a cascata de E1 e E8 |
| Bangkok | infraestrutura | -1 | GET /catalogo (fase clara, 21/10); confere com a cascata de E1 e E8 |
| Bangkok | energia_ponta_kwh | -0,5 | GET /catalogo (fase clara, 21/10); confere com a cascata de E1 e E8 |
| Bangkok | demanda_contratada | -2 | GET /catalogo (fase clara, 21/10); confere com a cascata de E1 e E8 |
| Istanbul | certo | 15 | GET /catalogo (fase clara, 21/10) |
| Istanbul | upgrade | 8 | GET /catalogo (fase clara, 21/10) |
| Istanbul | nao_atendido | -200 | GET /catalogo (fase clara, 21/10) |
| Istanbul | infraestrutura | -1 | GET /catalogo (fase clara, 21/10) |
| Istanbul | energia_ponta_kwh | -0,5 | GET /catalogo (fase clara, 21/10) |
| Istanbul | demanda_contratada | -2 | GET /catalogo (fase clara, 21/10) |
| Hanoi | certo | 15 | GET /catalogo (fase clara, 21/10) |
| Hanoi | upgrade | 8 | GET /catalogo (fase clara, 21/10) |
| Hanoi | nao_atendido | -200 | GET /catalogo (fase clara, 21/10) |
| Hanoi | infraestrutura | -1 | GET /catalogo (fase clara, 21/10) |
| Hanoi | energia_ponta_kwh | -0,5 | GET /catalogo (fase clara, 21/10) |
| Hanoi | demanda_contratada | -2 | GET /catalogo (fase clara, 21/10) |
| Marrakech | certo | 15 | GET /catalogo (fase clara, 21/10) |
| Marrakech | upgrade | 8 | GET /catalogo (fase clara, 21/10) |
| Marrakech | nao_atendido | -200 | GET /catalogo (fase clara, 21/10) |
| Marrakech | infraestrutura | -1 | GET /catalogo (fase clara, 21/10) |
| Marrakech | energia_ponta_kwh | -0,5 | GET /catalogo (fase clara, 21/10) |
| Marrakech | demanda_contratada | -2 | GET /catalogo (fase clara, 21/10) |
| Zurich | certo | 15 | GET /catalogo (fase clara, 21/10) |
| Zurich | upgrade | 8 | GET /catalogo (fase clara, 21/10) |
| Zurich | nao_atendido | -200 | GET /catalogo (fase clara, 21/10) |
| Zurich | infraestrutura | -1 | GET /catalogo (fase clara, 21/10) |
| Zurich | energia_ponta_kwh | -0,5 | GET /catalogo (fase clara, 21/10) |
| Zurich | demanda_contratada | -2 | GET /catalogo (fase clara, 21/10) |

Agências sem pesos próprios usam os de **Bangkok** (hipótese, marcada nas tabelas).

## 2. Origem dos custos de obra

| Tipo | Item | Custo | Fonte |
|---|---|---|---|
| carregadores | ac_7 | 250 | GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250) |
| carregadores | dc_30 | 3.500 | GET /catalogo (fase clara, 21/10); confere com a dedução E1 (3500) |
| carregadores | ac_11 | 1.100 | GET /catalogo (fase clara, 21/10) |
| carregadores | ac_22x2 | 1.500 | GET /catalogo (fase clara, 21/10) |
| carregadores | dc_60x2 | 7.300 | GET /catalogo (fase clara, 21/10) |
| carregadores | dc_120x2 | 15.800 | GET /catalogo (fase clara, 21/10) |
| entradas | _existente | 0 | regulamento 7.2: manter a entrada existente custa 0 |
| entradas | b3_75 | 5.000 | GET /catalogo (fase clara, 21/10) |
| entradas | a4_150 | 6.500 | GET /catalogo (fase clara, 21/10) |
| entradas | a4_225 | 8.200 | GET /catalogo (fase clara, 21/10) |
| entradas | a4_300 | 10.000 | GET /catalogo (fase clara, 21/10) |
| entradas | se_500 | 18.800 | GET /catalogo (fase clara, 21/10) |
| entradas | se_750 | 24.400 | GET /catalogo (fase clara, 21/10) |
| entradas | se_1000 | 30.000 | GET /catalogo (fase clara, 21/10) |
| entradas | se_1500 | 41.200 | GET /catalogo (fase clara, 21/10) |
| entradas | se_2000 | 52.500 | GET /catalogo (fase clara, 21/10) |
| entradas | b3_45 | **?** | GET /catalogo: sem custo (só vale como entrada existente) |

## 3. Item × regra × cálculo × juiz (submissões testadas no juiz)

### `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I01_base_ac7x3_dc30_b3_75.json`

3× ac_7 + 1× dc_30 · b3_75 · proxima_retirada/igual · resposta: `operacao/respostas/Istanbul/console_I01.json` · pesos de Istanbul

| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |
|---|---|---|---|---|---|---|---|
| certo | RO-04, RO-05 (escolha do carro, sem upgrade) | 1.288 | 1.288 | 15 | 19.320 | 19.320 | sim |
| upgrade | RO-05 (menor upgrade) | 3 | 3 | 8 | 24 | 24 | sim |
| nao_atendido | RO-06 (cliente perdido) | 2 | 2 | -200 | -400 | -400 | sim |
| demanda_contratada | 6.2, 6.3.7 (validar.demanda_kw) | 0 | 0 | -2 | 0 | 0 | sim |
| energia_ponta_kwh | RO-16 + medição RO-19 | 2.625,6 | 2.625,6 | -0,5 | -1.312,8 | -1.312,8 | sim |
| infraestrutura | 7.1, 7.2 (custos do catálogo) | 9.250 | 9.250 | -1 | -9.250 | -9.250 | sim |
| **nota** | | | | | **8.381,2** | **8.381,2** | sim |

Custos usados: ac_7=250 (GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250)); dc_30=3500 (GET /catalogo (fase clara, 21/10); confere com a dedução E1 (3500)); b3_75=5000 (GET /catalogo (fase clara, 21/10))

### `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H09_ac7x3_chegada_evitar.json`

3× ac_7 · b3_45 · chegada/igual · evitar_ponta · resposta: `operacao/respostas/Bangkok/151441_teste_completo_12023e70e2.json` · pesos de Bangkok

| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |
|---|---|---|---|---|---|---|---|
| certo | RO-04, RO-05 (escolha do carro, sem upgrade) | 270 | 270 | 15 | 4.050 | 4.050 | sim |
| upgrade | RO-05 (menor upgrade) | 0 | 0 | 8 | 0 | 0 | sim |
| nao_atendido | RO-06 (cliente perdido) | 1 | 1 | -200 | -200 | -200 | sim |
| demanda_contratada | 6.2, 6.3.7 (validar.demanda_kw) | 0 | 0 | -2 | 0 | 0 | sim |
| energia_ponta_kwh | RO-16 + medição RO-19 | 0 | 0 | -0,5 | 0 | 0 | sim |
| infraestrutura | 7.1, 7.2 (custos do catálogo) | 750 | 750 | -1 | -750 | -750 | sim |
| **nota** | | | | | **3.100** | **3.100** | sim |

Custos usados: ac_7=250 (GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250)); entrada b3_45=0 (existente)

### `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H13_ac7x3_proxret_evitar.json`

3× ac_7 · b3_45 · proxima_retirada/igual · evitar_ponta · resposta: `operacao/respostas/Bangkok/151544_teste_completo_72fbf8d93b.json` · pesos de Bangkok

| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |
|---|---|---|---|---|---|---|---|
| certo | RO-04, RO-05 (escolha do carro, sem upgrade) | 270 | 270 | 15 | 4.050 | 4.050 | sim |
| upgrade | RO-05 (menor upgrade) | 0 | 0 | 8 | 0 | 0 | sim |
| nao_atendido | RO-06 (cliente perdido) | 1 | 1 | -200 | -200 | -200 | sim |
| demanda_contratada | 6.2, 6.3.7 (validar.demanda_kw) | 0 | 0 | -2 | 0 | 0 | sim |
| energia_ponta_kwh | RO-16 + medição RO-19 | 0 | 0 | -0,5 | 0 | 0 | sim |
| infraestrutura | 7.1, 7.2 (custos do catálogo) | 750 | 750 | -1 | -750 | -750 | sim |
| **nota** | | | | | **3.100** | **3.100** | sim |

Custos usados: ac_7=250 (GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250)); entrada b3_45=0 (existente)

### `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E8_ac7x3_evitar.json`

3× ac_7 · b3_45 · menor_soc/igual · evitar_ponta · resposta: `operacao/respostas/Bangkok/console_E8_ac7x3_evitar.json` · pesos de Bangkok

| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |
|---|---|---|---|---|---|---|---|
| certo | RO-04, RO-05 (escolha do carro, sem upgrade) | 267 | 267 | 15 | 4.005 | 4.005 | sim |
| upgrade | RO-05 (menor upgrade) | 2 | 2 | 8 | 16 | 16 | sim |
| nao_atendido | RO-06 (cliente perdido) | 2 | 2 | -200 | -400 | -400 | sim |
| demanda_contratada | 6.2, 6.3.7 (validar.demanda_kw) | 0 | 0 | -2 | 0 | 0 | sim |
| energia_ponta_kwh | RO-16 + medição RO-19 | 0 | 0 | -0,5 | 0 | 0 | sim |
| infraestrutura | 7.1, 7.2 (custos do catálogo) | 750 | 750 | -1 | -750 | -750 | sim |
| **nota** | | | | | **2.871** | **2.871** | sim |

Custos usados: ac_7=250 (GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250)); entrada b3_45=0 (existente)

### `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#1`

2× ac_7 + 1× dc_30 · b3_45 · menor_soc/igual · resposta: `operacao/respostas/Bangkok/151338_teste_completo_8230a35b8a.json` · pesos de Bangkok

| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |
|---|---|---|---|---|---|---|---|
| certo | RO-04, RO-05 (escolha do carro, sem upgrade) | 271 | 271 | 15 | 4.065 | 4.065 | sim |
| upgrade | RO-05 (menor upgrade) | 0 | 0 | 8 | 0 | 0 | sim |
| nao_atendido | RO-06 (cliente perdido) | 0 | 0 | -200 | 0 | 0 | sim |
| demanda_contratada | 6.2, 6.3.7 (validar.demanda_kw) | 0 | 0 | -2 | 0 | 0 | sim |
| energia_ponta_kwh | RO-16 + medição RO-19 | 101,1 | 101,1 | -0,5 | -50,5 | -50,5 | sim |
| infraestrutura | 7.1, 7.2 (custos do catálogo) | 4.000 | 4.000 | -1 | -4.000 | -4.000 | sim |
| **nota** | | | | | **14,5** | **14,5** | sim |

Custos usados: ac_7=250 (GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250)); dc_30=3500 (GET /catalogo (fase clara, 21/10); confere com a dedução E1 (3500)); entrada b3_45=0 (existente)

### `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E1_base.json`

2× ac_7 + 1× dc_30 · b3_45 · menor_soc/igual · resposta: `operacao/respostas/Bangkok/151338_teste_completo_8230a35b8a.json` · pesos de Bangkok

| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |
|---|---|---|---|---|---|---|---|
| certo | RO-04, RO-05 (escolha do carro, sem upgrade) | 271 | 271 | 15 | 4.065 | 4.065 | sim |
| upgrade | RO-05 (menor upgrade) | 0 | 0 | 8 | 0 | 0 | sim |
| nao_atendido | RO-06 (cliente perdido) | 0 | 0 | -200 | 0 | 0 | sim |
| demanda_contratada | 6.2, 6.3.7 (validar.demanda_kw) | 0 | 0 | -2 | 0 | 0 | sim |
| energia_ponta_kwh | RO-16 + medição RO-19 | 101,1 | 101,1 | -0,5 | -50,5 | -50,5 | sim |
| infraestrutura | 7.1, 7.2 (custos do catálogo) | 4.000 | 4.000 | -1 | -4.000 | -4.000 | sim |
| **nota** | | | | | **14,5** | **14,5** | sim |

Custos usados: ac_7=250 (GET /catalogo (fase clara, 21/10); confere com a dedução E8 (250)); dc_30=3500 (GET /catalogo (fase clara, 21/10); confere com a dedução E1 (3500)); entrada b3_45=0 (existente)

## 4. Submissões ainda não testadas no juiz (previsão)

| Submissão | Nota local | Itens (pontos) | O que falta para a nota ser exata |
|---|---|---|---|
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I03_base_chegada.json` | 8.419,8 | certo 19.350 · upgrade 8 · nao_atendido -400 · energia_ponta_kwh -1.288,2 · infraestrutura -9.250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I10_ac22_ac7_dc30.json` | 7.834,2 | certo 19.380 · upgrade 8 · energia_ponta_kwh -1.303,8 · infraestrutura -10.250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I02_base_evitar_ponta.json` | 7.105 | certo 18.675 · upgrade 280 · nao_atendido -2.600 · infraestrutura -9.250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I06_base_a4_150_dem60.json` | 6.761,2 | certo 19.320 · upgrade 24 · nao_atendido -400 · demanda_contratada -120 · energia_ponta_kwh -1.312,8 · infraestrutura -10.750 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I04_base_menor_soc.json` | 6.429,8 | certo 19.185 · upgrade 24 · nao_atendido -2.200 · energia_ponta_kwh -1.329,2 · infraestrutura -9.250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I08_ac7x2_dc60.json` | 5.003,2 | certo 19.380 · nao_atendido -200 · energia_ponta_kwh -1.376,8 · infraestrutura -12.800 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H15_ac7x4_chegada_evitar.json` | 2.850 | certo 4.050 · nao_atendido -200 · infraestrutura -1.000 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H12_ac22x2_ac7_chegada_evitar.json` | 2.100 | certo 4.050 · nao_atendido -200 · infraestrutura -1.750 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I07_ac7x2_dc30.json` | 1.166,3 | certo 17.835 · upgrade 552 · nao_atendido -7.000 · energia_ponta_kwh -1.220,7 · infraestrutura -9.000 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H11_ac22x2_x2_evitar.json` | 1.065 | certo 4.065 · infraestrutura -3.000 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I05_base_entrada_existente_b3_45.json` | 942,1 | certo 17.355 · upgrade 624 · nao_atendido -11.600 · energia_ponta_kwh -1.186,9 · infraestrutura -4.250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#3` | 565 | certo 4.065 · infraestrutura -3.500 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E3_dc30_evitar.json` | 565 | certo 4.065 · infraestrutura -3.500 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H10_ac11x3_chegada_evitar.json` | 550 | certo 4.050 · nao_atendido -200 · infraestrutura -3.300 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E4_dc30.json` | 533,2 | certo 4.065 · energia_ponta_kwh -31,8 · infraestrutura -3.500 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E2_base_evitar.json` | 65 | certo 4.065 · infraestrutura -4.000 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#6` | 14,3 | certo 4.065 · energia_ponta_kwh -50,7 · infraestrutura -4.000 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#7` | -199,5 | certo 4.050 · nao_atendido -200 · energia_ponta_kwh -49,5 · infraestrutura -4.000 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#8` | -519,8 | certo 4.065 · energia_ponta_kwh -84,8 · infraestrutura -4.500 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E5_dc60_evitar.json` | -3.235 | certo 4.065 · infraestrutura -7.300 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#4` | -3.250,7 | certo 4.065 · energia_ponta_kwh -15,7 · infraestrutura -7.300 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#5` | -3.250,8 | certo 4.065 · energia_ponta_kwh -15,8 · infraestrutura -7.300 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E6_dc30_b3_75_evitar.json` | -4.435 | certo 4.065 · infraestrutura -8.500 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#9` | -10.440,9 | certo 4.065 · energia_ponta_kwh -5,9 · infraestrutura -14.500 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#10` | -21.855 | certo 4.065 · demanda_contratada -120 · infraestrutura -25.800 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E7_ac7_evitar.json` | -30.954 | certo 1.320 · upgrade 176 · nao_atendido -32.200 · infraestrutura -250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#2` | -31.065,4 | certo 1.320 · upgrade 176 · nao_atendido -32.200 · energia_ponta_kwh -111,4 · infraestrutura -250 | nada |
| `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I09_ac7x4_sem_dc.json` | -84.659,8 | certo 8.490 · upgrade 2.272 · nao_atendido -88.600 · energia_ponta_kwh -821,8 · infraestrutura -6.000 | nada |
