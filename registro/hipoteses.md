# Caderno de hipóteses

> Gerado por `py analise/hipoteses.py relatorio`. Não editar à mão: a fonte é `registro/hipoteses.jsonl`.

| ID | Hipótese | Base | Submissão | Previsto (certos/upg/perd · ponta kWh) | Nota juiz | Obra juiz | Modelo bate? | Δnota | Leitura | Conclusão | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | Referência: exemplo do kit (2x AC-7 + DC-30, política padrão) | — | `{"ac_7": 2, "dc_30": 1} b3_45 · menor_soc/igual` | 271/0/0 · 101.1 | 14.5 | 4000 | sim | — | — | — | testada |
| E2 | evitar_ponta zera a energia na ponta sem perder clientes; a nota sobe | E1 | `{"ac_7": 2, "dc_30": 1} b3_45 · menor_soc/igual · evitar_ponta` | 271/0/0 · 0.0 | — | — | — | — | — | — | aberta |
| E3 | 1 DC-30 basta para 100%; tirar 2 AC-7 reduz a obra e a nota sobe | E2 | `{"dc_30": 1} b3_45 · menor_soc/igual · evitar_ponta` | 271/0/0 · 0.0 | — | — | — | — | — | — | aberta |
| E4 | Sem evitar_ponta o DC-30 gasta 63,6 kWh na ponta (confirma o peso da ponta) | E3 | `{"dc_30": 1} b3_45 · menor_soc/igual` | 271/0/0 · 63.6 | — | — | — | — | — | — | aberta |
| E5 | DC-60 no lugar do DC-30 não melhora o atendimento; mede a diferença de obra | E3 | `{"dc_60x2": 1} b3_45 · menor_soc/igual · evitar_ponta` | 271/0/0 · 0.0 | — | — | — | — | — | — | aberta |
| E6 | Ampliar para b3_75 não melhora nada; mede o custo da entrada | E3 | `{"dc_30": 1} b3_75 · menor_soc/igual · evitar_ponta` | 271/0/0 · 0.0 | — | — | — | — | — | — | aberta |
| E7 | 1 AC-7 não dá conta: muitos perdidos e upgrades | E3 | `{"ac_7": 1} b3_45 · menor_soc/igual · evitar_ponta` | 88/22/161 · 0.0 | — | — | — | — | — | — | aberta |
| E8 | 3 AC-7 quase chegam a 100% (2 perdidos); mede o valor de atender | E7 | `{"ac_7": 3} b3_45 · menor_soc/igual · evitar_ponta` | 267/2/2 · 0.0 | 2871 | 750 | sim | — | — | — | testada |
| H09 | Trocar menor_soc por chegada com 3 AC-7 evita os upgrades e 1 perdido: nota 2871 → 3100 | E8 | `{"ac_7": 3} b3_45 · chegada/igual · evitar_ponta` | 270/0/1 · 0.0 | 3100.0 | 750 | sim | 229.0 | mesma obra, muda o atendimento ({'certos': 3, 'upgrades': -2, 'nao_atendidos': -1}): Δnota +229 = w_certo·Δcertos + w_upg·Δupg − w_perd·Δperdidos | — | testada |
| H10 | 3 AC-11 perdem só 1 cliente; mede o custo do AC-11 | E1 | `{"ac_11": 3} b3_45 · chegada/igual · evitar_ponta` | 270/0/1 · 0.0 | — | — | — | — | — | — | aberta |
| H11 | 2 AC-22 (4 saídas) atendem 100%; mede o custo do AC-22 | E1 | `{"ac_22x2": 2} b3_45 · menor_soc/igual · evitar_ponta` | 271/0/0 · 0.0 | — | — | — | — | — | — | aberta |
| H12 | AC-22 + AC-7 perdem só 1 cliente; combinação barata | E1 | `{"ac_22x2": 1, "ac_7": 1} b3_45 · chegada/igual · evitar_ponta` | 270/0/1 · 0.0 | — | — | — | — | — | — | aberta |
| H13 | proxima_retirada com 3 AC-7 também chega a 3100 (270/0/1) | E8 | `{"ac_7": 3} b3_45 · proxima_retirada/igual · evitar_ponta` | 270/0/1 · 0.0 | 3100.0 | 750 | sim | 229.0 | mesma obra, muda o atendimento ({'certos': 3, 'upgrades': -2, 'nao_atendidos': -1}): Δnota +229 = w_certo·Δcertos + w_upg·Δupg − w_perd·Δperdidos | — | testada |
| H15 | 4º AC-7 não salva o cliente perdido (270/0/1): seguro de 250 que não paga em Bangkok | H09 | `{"ac_7": 4} b3_45 · chegada/igual · evitar_ponta` | 270/0/1 · 0.0 | — | — | — | — | — | — | aberta |
