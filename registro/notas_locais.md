# Notas locais (nosso motor + pesos/custos conhecidos)

> Gerado por `py analise/nota_local.py`. Nota **parcial** = falta custo de algum item; é um teto (a obra que falta só desconta).
> Pesos e custos com a fonte de cada valor: `analise/pesos_custos.json` e a matriz de rastreabilidade.

| # | Submissão | Configuração | Certos/Upg/Perd | Ponta kWh | Obra | Nota local | Nota juiz | Δ (local − juiz) |
|---|---|---|---|---|---|---|---|---|
| 1 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I03_base_chegada.json` | 3× ac_7 + 1× dc_30 · b3_75 · chegada/igual | 1290/1/2 | 2.576,4 | 9.250 | **8.419,8** | — | — |
| 2 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I01_base_ac7x3_dc30_b3_75.json` | 3× ac_7 + 1× dc_30 · b3_75 · proxima_retirada/igual | 1288/3/2 | 2.625,6 | 9.250 | **8.381,2** | 8.381,2 | 0 ✔ |
| 3 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I10_ac22_ac7_dc30.json` | 1× ac_22x2 + 1× ac_7 + 1× dc_30 · b3_75 · proxima_retirada/igual | 1292/1/0 | 2.607,7 | 10.250 | **7.834,2** | — | — |
| 4 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I02_base_evitar_ponta.json` | 3× ac_7 + 1× dc_30 · b3_75 · proxima_retirada/igual · evitar_ponta | 1245/35/13 | 0 | 9.250 | **7.105** | — | — |
| 5 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I06_base_a4_150_dem60.json` | 3× ac_7 + 1× dc_30 · a4_150 · dem 60 · proxima_retirada/igual | 1288/3/2 | 2.625,6 | 10.750 | **6.761,2** | — | — |
| 6 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I04_base_menor_soc.json` | 3× ac_7 + 1× dc_30 · b3_75 · menor_soc/igual | 1279/3/11 | 2.658,3 | 9.250 | **6.429,8** | — | — |
| 7 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I08_ac7x2_dc60.json` | 2× ac_7 + 1× dc_60x2 · b3_75 · proxima_retirada/igual | 1292/0/1 | 2.753,6 | 12.800 | **5.003,2** | — | — |
| 8 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H09_ac7x3_chegada_evitar.json` | 3× ac_7 · b3_45 · chegada/igual · evitar_ponta | 270/0/1 | 0 | 750 | **3.100** | 3.100 | 0 ✔ |
| 9 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H13_ac7x3_proxret_evitar.json` | 3× ac_7 · b3_45 · proxima_retirada/igual · evitar_ponta | 270/0/1 | 0 | 750 | **3.100** | 3.100 | 0 ✔ |
| 10 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E8_ac7x3_evitar.json` | 3× ac_7 · b3_45 · menor_soc/igual · evitar_ponta | 267/2/2 | 0 | 750 | **2.871** | 2.871 | 0 ✔ |
| 11 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H15_ac7x4_chegada_evitar.json` | 4× ac_7 · b3_45 · chegada/igual · evitar_ponta | 270/0/1 | 0 | 1.000 | **2.850** | — | — |
| 12 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H12_ac22x2_ac7_chegada_evitar.json` | 1× ac_22x2 + 1× ac_7 · b3_45 · chegada/igual · evitar_ponta | 270/0/1 | 0 | 1.750 | **2.100** | — | — |
| 13 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I07_ac7x2_dc30.json` | 2× ac_7 + 1× dc_30 · b3_75 · proxima_retirada/igual | 1189/69/35 | 2.441,4 | 9.000 | **1.166,3** | — | — |
| 14 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H11_ac22x2_x2_evitar.json` | 2× ac_22x2 · b3_45 · menor_soc/igual · evitar_ponta | 271/0/0 | 0 | 3.000 | **1.065** | — | — |
| 15 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I05_base_entrada_existente_b3_45.json` | 3× ac_7 + 1× dc_30 · b3_45 · proxima_retirada/igual | 1157/78/58 | 2.373,8 | 4.250 | **942,1** | — | — |
| 16 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#3` | 1× dc_30 · b3_45 · menor_soc/igual · evitar_ponta | 271/0/0 | 0 | 3.500 | **565** | — | — |
| 17 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E3_dc30_evitar.json` | 1× dc_30 · b3_45 · menor_soc/igual · evitar_ponta | 271/0/0 | 0 | 3.500 | **565** | — | — |
| 18 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/H10_ac11x3_chegada_evitar.json` | 3× ac_11 · b3_45 · chegada/igual · evitar_ponta | 270/0/1 | 0 | 3.300 | **550** | — | — |
| 19 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E4_dc30.json` | 1× dc_30 · b3_45 · menor_soc/igual | 271/0/0 | 63,6 | 3.500 | **533,2** | — | — |
| 20 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E2_base_evitar.json` | 2× ac_7 + 1× dc_30 · b3_45 · menor_soc/igual · evitar_ponta | 271/0/0 | 0 | 4.000 | **65** | — | — |
| 21 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#1` | 2× ac_7 + 1× dc_30 · b3_45 · menor_soc/igual | 271/0/0 | 101,1 | 4.000 | **14,5** | 14,5 | 0 ✔ |
| 22 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E1_base.json` | 2× ac_7 + 1× dc_30 · b3_45 · menor_soc/igual | 271/0/0 | 101,1 | 4.000 | **14,5** | 14,5 | 0 ✔ |
| 23 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#6` | 2× ac_7 + 1× dc_30 · b3_45 · chegada/igual | 271/0/0 | 101,5 | 4.000 | **14,3** | — | — |
| 24 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#7` | 2× ac_7 + 1× dc_30 · b3_45 · proxima_retirada/prioridade | 270/0/1 | 99 | 4.000 | **-199,5** | — | — |
| 25 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#8` | 3× ac_22x2 · b3_45 · menor_soc/igual | 271/0/0 | 169,7 | 4.500 | **-519,8** | — | — |
| 26 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E5_dc60_evitar.json` | 1× dc_60x2 · b3_45 · menor_soc/igual · evitar_ponta | 271/0/0 | 0 | 7.300 | **-3.235** | — | — |
| 27 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#4` | 1× dc_60x2 · b3_45 · menor_soc/igual | 271/0/0 | 31,4 | 7.300 | **-3.250,7** | — | — |
| 28 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#5` | 1× dc_60x2 · b3_45 · menor_soc/prioridade | 271/0/0 | 31,6 | 7.300 | **-3.250,8** | — | — |
| 29 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E6_dc30_b3_75_evitar.json` | 1× dc_30 · b3_75 · menor_soc/igual · evitar_ponta | 271/0/0 | 0 | 8.500 | **-4.435** | — | — |
| 30 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#9` | 2× ac_11 + 1× dc_60x2 · b3_75 · menor_soc/igual | 271/0/0 | 11,8 | 14.500 | **-10.440,9** | — | — |
| 31 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#10` | 1× dc_120x2 + 1× dc_30 · a4_150 · dem 60 · proxima_retirada/prioridade · evitar_ponta | 271/0/0 | 0 | 25.800 | **-21.855** | — | — |
| 32 | `kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/E7_ac7_evitar.json` | 1× ac_7 · b3_45 · menor_soc/igual · evitar_ponta | 88/22/161 | 0 | 250 | **-30.954** | — | — |
| 33 | `kit_kickoff/kit_kickoff/submissoes/bangkok_manual.json#2` | 1× ac_7 · b3_45 · menor_soc/igual | 88/22/161 | 222,8 | 250 | **-31.065,4** | — | — |
| 34 | `kit_kickoff/kit_kickoff/submissoes/neblina_istanbul/I09_ac7x4_sem_dc.json` | 4× ac_7 · b3_75 · proxima_retirada/igual | 566/284/443 | 1.643,6 | 6.000 | **-84.659,8** | — | — |
