# Regulamento: resumo pesquisável

> Transcrito de `instruções.pdf` (o PDF é imagem, sem texto). A fonte oficial é o regulamento em `.md` (`py operacao/juiz.py instrucoes` salva em `docs/regulamento.md`). Os números das seções são os do regulamento.

## 2. Formato do dia (12 h)

| Momento | O que acontece |
|---|---|
| H−1 a H0 | Abertura: regras, tutorial em Bangkok, PalavrasChave, teste de conexão |
| H0 a H7:30 | Jogo: **6 agências pontuadas** liberadas aos poucos (algumas só na 2ª metade) |
| H4 | **Revelação:** pesos da nota e custos de obra (Anexo H4, `GET /catalogo`) |
| Durante o jogo | Eventos operacionais ao vivo (seção 11) |
| H7:30 | **Congelamento:** fim dos testes e dos envios finais |
| H7:30 a H8 | Preparação; API só leitura |
| H8 a H11 | Apresentações: 12 min + 5 min de perguntas |

Fases em `GET /status` (`fase`): `pre`, `neblina` (H0–H4), `clara` (H4–congelamento), `congelado`.

## 4. Cenário e dados

- Dados fictícios; 8 modelos de carro com specs públicas. Categorias: Bronze < Prata < Ouro < Diamante.
- Contrato é ida e volta na mesma agência → **agências independentes**.
- **Devolução em km:** `SOC = km / autonomia_do_modelo × 100`, nunca acima do SOC de saída.
- Com recarga ilimitada, todos os contratos são atendíveis: todo cliente perdido é culpa da estratégia.
- Tempo em minutos desde 00:00 de **domingo, 17/10/2049**. **T0 = minuto 1080** (domingo 18:00).
- **Semanas públicas 1–4** (dados entregues, testes); **semanas ocultas** 4 seguintes (envio final, nota final). O juiz simula o horizonte inteiro.

## 5. Regras de operação do juiz

**5.1 Atendimento**
- Na retirada: carro da categoria pedida **ou superior** com **SOC ≥ 80%**. Downgrade nunca.
- SOC alvo fixo em 80% (não é parâmetro).
- Escolha: menor upgrade → menor SOC → não plugado → menor `id` (alfabético). O mesmo desempate final vale para a fila.
- Sem carro apto: **cliente perdido**, sem espera.
- Agência fechada: ninguém retira nem desconecta. Todos os contratos retiram em horário de funcionamento.
- Carro retirado plugado é desplugado na hora.
- **Ordem no mesmo minuto:** devoluções → abertura, início/fim da ponta e eventos → fim de recarga → retiradas → fechamento.

**5.2 Pátio, vagas e fila**
- Devolvido com SOC < 80% vai para a fila de recarga.
- Plugados ≤ saídas instaladas ≤ vagas elétricas.
- Plugar e desplugar **só com a agência aberta**; a recarga continua com ela fechada.
- Ao chegar a 80%: desplugado se aberta; se fechada, **segura a saída** até abrir.

**5.3 Potência**
- Carro limitado pela curva (AC ou DC) no degrau de 5% de SOC: média de duas linhas da tabela, índice `min(19, floor(SOC/5))`.
- Carregador de 2 saídas: nominal dividido entre os carros conectados; a sobra de um vai para o outro.
- **Limite da agência:** B3 = kW útil da entrada; A4/SE = **demanda contratada**.
- Divisão do limite: `igual` ou em ordem de `prioridade`.
- **Ponta:** seg–sex, 18:00–21:00. Com `evitar_ponta`: 0 kW, os carros continuam plugados.
- Medição em **janelas de 15 min**.

**5.4 O juiz não modela:** perdas AC/DC, fator de potência (= 1), manobra entre vagas, degradação de bateria.

**5.5 Entrada:** `kW útil = kVA × 1,0 × 0,9`.

## 6. A submissão

```json
{
  "agencia": "Bangkok",
  "carregadores": {"dc_60x2": 1, "ac_7": 2},
  "entrada": "a4_150",
  "demanda_contratada_kw": 60,
  "politica": {"prioridade": "proxima_retirada", "evitar_ponta": false, "divisao": "prioridade"}
}
```

| Parâmetro | Opções | Padrão |
|---|---|---|
| `prioridade` | `menor_soc`, `chegada`, `proxima_retirada` | `menor_soc` |
| `divisao` | `igual`, `prioridade` | `igual` |
| `evitar_ponta` | `true`, `false` | `false` |

**6.2 Validação** (inválida = `422`, não cobra):
- Pelo menos 1 carregador; Σ saídas ≤ vagas (2 saídas contam 2).
- Entrada: manter ou **subir**, nunca descer. `b3_45` só como existente; pode ir para `b3_75` (continua B3).
- Demanda contratada: **só com entrada acima de 75 kVA** (A4/SE). Passos de 10 kW, de 30 até o teto da entrada. O juiz arredonda para o múltiplo de 10 mais próximo (75→80, 87,3→90). Omitida = teto da entrada. Em B3 é rejeitada.
- Chaves permitidas: `agencia`, `carregadores`, `entrada`, `demanda_contratada_kw`, `politica`.

**6.3 Exemplos (viram testes)**
- 6.3.1: Prata às 10:00, pátio Geely 82%, Dolphin Mini 95% plugado, MG4 100%, JAC 100% → sai o **Geely**. Geely a 78% → Dolphin Mini. Nenhum Prata → MG4 (upgrade).
- 6.3.2: Dolphin GS (44,9 kWh) 20%→80% sozinho num DC-60, sem limite: **36,7 min** (58,4 → 27,2 kW). 80→100% levaria +48,9 min.
- 6.3.3: A Kwid Bronze 30% (55,5 km, 10:00, reserva 14:00); B Dolphin Mini Prata 20% (56,0 km, 10:20, 13:15); C MG4 Ouro 55% (164,5 km, 10:40, 12:30); D Leapmotor Diamante 40% (115,2 km, 10:55, 12:30). `menor_soc` A,B,D,C · `chegada` A,B,C,D · `proxima_retirada` C,D,B,A.
- 6.3.4: escolhe o carregador que daria mais potência (dividindo o nominal com quem já está, pela curva), **ignorando limite e `divisao`**. Empate pelo id alfabético: `ac_11, ac_22x2, ac_7, dc_120x2, dc_30, dc_60x2`. Não troca depois.
- 6.3.5: limite 40,5, 2× DC-60, 4 carros (Geely 30% 71,5 kW; Dolphin GS 50%; Kwid 40% 26,6; JAC 75% 16,45). `igual`: 10,125 cada. `prioridade` (menor_soc: Kwid, Geely, JAC, Dolphin): Kwid 26,6, Geely 13,9, JAC 0, Dolphin 0. Com limite 80: `igual` 21,18 (JAC 16,45); `prioridade` Kwid 26,6, Geely 53,4.
- 6.3.6: MG4 43 kWh pluga seg 17:00 num AC-22 a 11 kW, de 29% a 80% (22 kWh, 2 h). Sem evitar: termina 19:00, 11 kWh na ponta. Com evitar: 17–18, parado 18–21, 21–22 → 0 kWh na ponta, mas segura a saída 3 h a mais.
- 6.3.7: `a4_150` (135 kW úteis) com demanda 80 → limite 80 kW (teto rígido, sem multa). Omitir = 130 kW na nota. 84→80, 85→90, 135→140 (rejeitado).

## 7. Catálogo

| Carregador | Tipo | kW | Saídas |
|---|---|---|---|
| `ac_7` | AC | 7 | 1 |
| `ac_11` | AC | 11 | 1 |
| `ac_22x2` | AC | 22 | 2 |
| `dc_30` | DC | 30 | 1 |
| `dc_60x2` | DC | 60 | 2 |
| `dc_120x2` | DC | 120 | 2 |

| Entrada | kVA | kW útil | Demanda máx. |
|---|---|---|---|
| `b3_45` | 45 | 40,5 | — |
| `b3_75` | 75 | 67,5 | — |
| `a4_150` | 150 | 135 | 130 |
| `a4_225` | 225 | 202,5 | 200 |
| `a4_300` | 300 | 270 | 270 |
| `se_500` | 500 | 450 | 450 |
| `se_750` | 750 | 675 | 670 |
| `se_1000` | 1000 | 900 | 900 |
| `se_1500` | 1500 | 1350 | 1350 |
| `se_2000` | 2000 | 1800 | 1800 |

Ampliar a entrada custa o **valor cheio** do novo nível (sem crédito pela existente); manter custa 0.

| Modelo | Categoria | Bateria kWh | Autonomia km | AC máx | DC máx |
|---|---|---|---|---|---|
| Renault Kwid E-Tech | Bronze | 26,8 | 185 | 7,4 | 30 |
| JAC E-JS1 | Bronze | 31,4 | 181 | 6,6 | 20 |
| Geely EX2 Pro | Prata | 39,0 | 289 | 6,6 | 80 |
| BYD Dolphin Mini GS | Prata | 38,9 | 280 | 6,6 | 40 |
| MG4 Urban Comfort | Ouro | 43,0 | 299 | 11,0 | 80 |
| BYD Dolphin GS | Ouro | 44,9 | 291 | 7,0 | 60 |
| BYD Dolphin Plus | Diamante | 60,5 | 427 | 11,0 | 80 |
| Leapmotor B10 BEV | Diamante | 56,2 | 288 | 11,0 | 140 |

O juiz usa a **curva**, não a ficha (ex.: Geely 80 kW na ficha, 73 kW na curva).

## 8. Pontuação

```
nota = (peso × certos) + (peso × upgrades) − (peso × não atendidos)
       − (peso × demanda contratada em kW) − (peso × kWh na ponta) − (peso × custo de obra)
```

- Demanda e custo de obra entram **inteiros** em cada janela avaliada. Demanda só em A4/SE.
- Os pesos podem ser ajustados pela organização durante o dia (`GET /catalogo`, campo `pesos`).
- **Nota final** = soma das 6 agências pontuadas (envio final, semanas ocultas). Agências maiores pesam mais. **Sem envio = 0.**
- Desempate: menos não atendidos nas ocultas → menor custo de obra → envio final mais cedo.

## 9. m7Coins

| Ação | m7Coins | Cooldown |
|---|---|---|
| Saldo inicial | 1.000 | — |
| Teste placar | 20 | 5 min por agência |
| Teste completo (placar + séries) | 50 (30 se o placar idêntico já foi pago) | 5 min por agência; ampliar placar → completo não exige nem reinicia o cooldown |
| Teste idêntico | 0 | não consome |
| 1º envio final por agência | 0 | — |
| Reenvio final | 80, 160, 320… (dobra) | 15 min por agência |
| Reenvio idêntico ao vigente | recusado | — |
| Bangkok | 0 | 1 min |

- **Idêntico** = mesma submissão normalizada **e** mesmos eventos ativos. Depois de um evento, volta a cobrar.
- Saldo nunca fica negativo (`402`). O 1º envio final é sempre possível.
- Teste não cobra obra; inválido (`422`) não cobra.

## 10. Neblina × Clara

| | Neblina (H0–H4) | Clara (H4–congelamento) |
|---|---|---|
| Pesos e custos | ocultos | publicados |
| Retorno do teste | nota + métricas físicas (contratos, atendimento_pct, pico_kw, energia_kwh) | + certos, upgrades, não atendidos, energia na ponta, demanda, custo_infra, **cascata de pontos** |

Dilema: gastar testando para inferir pesos ou confiar na engenharia. **Não há reenvio barato depois da revelação.**

## 11. Eventos ao vivo

- Ex.: limitação da concessionária, carregador fora de operação. Valem para todas as equipes, nos testes e nos envios finais.
- Aparecem em `GET /status` → `cartas` e `eventos_ativos` (agência e `params`). Também valem nas semanas públicas, para dar para testar.
- Envios finais já feitos são **reavaliados automaticamente**. Reagir custa o reenvio normal.

## 12. API

- Header `Authorization: Bearer <PalavraChave>`. **20 req/min por equipe** (todas as rotas e membros).
- Agência não liberada = `404 agencia_indisponivel`.
- Rotas: `GET /status`, `/equipe`, `PUT /equipe/nome` (uma vez), `GET /agencias/{id}`, `/kit`, `/contratos`, `/frota-t0`, `GET /catalogo`, `GET /instrucoes`, `GET /kit-kickoff`, `POST /teste/{id}?detalhe=placar|completo`, `POST /final/{id}`, `GET /placar`.
- Ordem das checagens: 401 → 429 rate → 413/422 corpo → 404 agência → (Bangkok no final: 403) → 403 congelado → 422 inválido → 409 idêntico → 429 cooldown → 402 saldo → 422 violação.
- `series` (completo): `potencia_kw`, `plugados_max`, `fila_max` a cada 15 min; `nao_atendidos_min`; `soc_retirada`.

## 13. Entregáveis

**13.1 Dashboard obrigatório.** Por agência: cascata de pontos (nosso modelo vs. juiz); potência a cada 15 min contra o limite e a ponta; ocupação de vagas e fila; SOC na retirada e perdidos por dia e hora. No consolidado: m7Coins gastos e custo de obra por agência; evolução da nota ao longo do dia; justificativa de entrada e demanda.

**13.2 Apresentação (12 + 5 min):** estratégia; como inferimos os pesos na Neblina; modelo próprio e quanto bate com o juiz; decisões por agência; reação aos eventos; o que faríamos com mais tempo.

**13.3 Prêmios:** geral = nota técnica. Especiais (júri, 0–5 por critério): melhor dashboard, melhor engenharia elétrica (entrada, demanda e ponta), **melhor modelagem** (menor erro contra o juiz com menos m7Coins), melhor leitura da Neblina.

## 14. Integridade

Não compartilhar a PalavraChave; não consultar o juiz por outra equipe; não tentar extrair dados ocultos. Erro estranho na API → avisar a organização.
