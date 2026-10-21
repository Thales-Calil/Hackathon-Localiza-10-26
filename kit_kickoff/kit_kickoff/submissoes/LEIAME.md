# Submissões para teste manual

`bangkok_manual.json` é uma lista de 10 cenários de Bangkok, cada um exercitando uma regra do motor (JSON não aceita comentários, então o propósito de cada um está aqui).

```bash
py simular.py submissoes/bangkok_manual.json
```

| # | Cenário | O que exercita | O que esperar |
|---|---|---|---|
| 1 | 2× AC-7 + DC-30, política padrão | Exemplo do kit | Referência para comparar o resto |
| 2 | Só 1× AC-7 | Capacidade insuficiente (RO-06) | Muitos clientes perdidos |
| 3 | 1× DC-30 + `evitar_ponta` | Ponta (RO-16), candidato barato | `energia_ponta_kwh` = 0 |
| 4 | 1× DC-60 (2 saídas) em b3_45, `igual` | Limite apertado: 60 kW em 40,5 (RO-12) | `pico_kw` ≤ 40,5 |
| 5 | Igual ao 4, com `divisao: prioridade` | Divisão sequencial (RO-11, RO-12) | Comparar com o 4 |
| 6 | Exemplo com `prioridade: chegada` | Fila FIFO (RO-07) | Comparar com o 1 |
| 7 | Exemplo com `proxima_retirada` + `prioridade` | Fila por reserva (RO-07) | Comparar com o 1 |
| 8 | 3× AC-22 (6 saídas = todas as vagas) | Ocupação máxima (RO-09) | Sem violações |
| 9 | DC-60 + 2× AC-11 em b3_75 | Ampliação de entrada B3 (67,5 kW) | `pico_kw` ≤ 67,5 |
| 10 | DC-120 + DC-30 em a4_150 com demanda 60 | Demanda contratada (6.3.7) | `pico_kw` ≤ 60 e `demanda_contratada_kw` = 60 |

Para testar um cenário isolado ou criar outro, copie um bloco para um arquivo próprio (ex.: `submissoes/bangkok_dc30.json`). O `operacao/juiz.py` exige um arquivo com **uma** submissão, não uma lista.
