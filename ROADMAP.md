# Roadmap: Hackathon Recarga Inteligente (Grupo 10)

> Fonte: `instruções.pdf` (regulamento das equipes) e `teste.pdf` (console de testes), 21/10. Resumo das regras em [docs/regulamento_resumo.md](docs/regulamento_resumo.md).

## O jogo em 5 linhas

1. Em cada agência escolhemos **carregadores**, **entrada elétrica**, **demanda contratada** (só A4/SE) e **política** (`prioridade`, `divisao`, `evitar_ponta`).
2. O **juiz** simula 4 semanas e dá uma nota em **pontos**: + clientes atendidos (certo > upgrade), − perdidos, − kW de demanda contratada, − kWh na ponta, − custo de obra.
3. A **nota final** = soma das 6 agências pontuadas no **envio final**, avaliado em **semanas ocultas**. Bangkok é tutorial: não pontua.
4. **m7Coins (1.000)** só pagam consultas ao juiz. Sobra não vale nada, mas acabar cedo nos deixa cegos nas agências que abrem tarde.
5. **Pesos e custos só aparecem em H4.** Até lá sabemos *o que* pontua, não *quanto*.

**Quem ganha:** quem tem um **modelo próprio fiel ao juiz** (o kit + nosso `motor.py`) e testa offline à vontade. O juiz serve só para confirmar.

---

## Equipe e papéis

| Papel | Responsável | Missão | Entrega principal | Pastas |
|---|---|---|---|---|
| **P1 · Operador do juiz** (requisições) | ___ | Única pessoa que fala com a API. Cuida do orçamento, dos cooldowns, dos kits novos, dos eventos e dos **envios finais** | `operacao/log_juiz.csv` sempre atualizado | `operacao/` |
| **P2 · Motor** (codificação, caminho crítico) | ___ | Etapas 2→5 do `motor.py`, uma por vez | `comparar.py` → `OK: bate com o juiz` | `kit_kickoff/kit_kickoff/kickoff/motor.py` |
| **P3 · Testes e fidelidade** (codificação) | ___ | Escreve o teste de cada etapa **antes** do P2. Prepara as etapas 6 e 7 em funções à parte. Fecha o ciclo com o P1 (juiz → `comparar.py` → corrige) | `testes/test_etapaN.py` | `kit_kickoff/kit_kickoff/testes/` |
| **P4 · Engenharia e otimização** | ___ | Viabilidade técnica por agência (carro × carregador, energia, entrada, ponta). Busca de configurações. Leitura dos pesos na Neblina | `analise/relatorios/<AG>.md` e ranking de candidatos | `analise/` |
| **P5 · Dashboard e pitch** | ___ | Dashboard obrigatório (13.1), registro de decisões, roteiro de 12 min | Dashboard + PDF do pitch | `dashboard/`, `registro/` |

Integrantes cadastrados: Thales, Davi, Jorge M, João Veloso, Jose K.

Sugestão de perfil: P2 e P3 são quem programa melhor em Python. P4 é quem tem formação de elétrica (há prêmio de "melhor engenharia elétrica"). P1 é organizado e atento a horário. P5 é quem apresenta.

### Regras da equipe (não negociáveis)

1. **Só o P1 chama a API**, sempre por `py operacao/juiz.py`. Os outros pedem ao P1 (canal da equipe: "teste X na agência Y, completo/placar, por quê").
2. **Só o P2 edita o `motor.py`.** O P3 entrega funções e testes; o P2 integra. Não mexer em `dados.py`, `validar.py`, `potencia.py`, `medicao.py`, `nota.py`, `tempo.py`, `modelo.py`.
3. **A PalavraChave fica no `.env`**, que não é versionado. Nunca no Git, no chat ou em print.
4. **Toda decisão vai para `registro/registro_decisoes.md`** com o dado que a justificou: vira slide.
5. **Git:** uma branch por papel (`motor`, `testes`, `analise`, `dashboard`, `operacao`). Merge na `main` pelo P2 só com a suíte de testes passando.

---

## Linha do tempo

H0 = início do jogo, logo depois da abertura. Não há relógio automático: vale o `GET /status` (`py operacao/juiz.py status`).

### Fase 0 · Abertura (H−1 a H0): ambiente pronto em todas as máquinas

| Quem | Tarefa | Pronto quando |
|---|---|---|
| Todos | `git clone` do repositório. Python 3.10+ (`python --version`). Rodar `py -m unittest discover -s testes` dentro de `kit_kickoff/kit_kickoff` | 11 testes OK |
| Todos | Ler [docs/regulamento_resumo.md](docs/regulamento_resumo.md) e a seção do próprio papel no regulamento | — |
| P1 | Criar `.env` (copiar de `.env.exemplo`). Rodar `py operacao/juiz.py status`, `instrucoes` e `kit` de cada agência liberada (Bangkok, Istanbul, Hanoi) | `dados/<AG>/` existe para todas; `docs/regulamento.md` salvo |
| P1 | Primeiro teste em Bangkok com `exemplo_submissao.json` (grátis) | Resposta salva em `operacao/respostas/Bangkok/` |
| P5 | Definir o nome da equipe? (`PUT /equipe/nome`, uma vez só) | Decidido em grupo |

### Fase 1 · Neblina, motor fiel (H0 a ~H2:30)

> **Status (21/10):** as etapas 2 a 7 já estão implementadas no `motor.py`, com 31 testes novos (`testes/test_etapa2.py` … `test_etapa7.py`) cobrindo os exemplos 6.3.1 a 6.3.6. Requisitos e suposições em [docs/requisitos_regras_operacao.md](docs/requisitos_regras_operacao.md). **Falta a etapa 8:** validar contra o juiz em Bangkok com `comparar.py`. Os papéis P2 e P3 passam a ser corrigir as divergências e confirmar as suposições S-01 a S-06. A etapa 7 (eventos) usa um formato provisório até o primeiro anúncio.

| Quem | Tarefa | Pronto quando |
|---|---|---|
| P2 | Etapa 2 (retirada/devolução) → etapa 3 (fila, plug, curva) → etapa 4 (limite e `divisao`) → etapa 5 (horário e ponta) | Cada etapa com o critério "Pronto quando" do `LEIAME.md` do kit |
| P3 | Uma etapa à frente do P2: `testes/test_etapa2.py` com o 6.3.1; `test_etapa3.py` com 6.3.2 (36,7 min) e 6.3.4; `test_etapa4.py` com 6.3.5; `test_etapa5.py` com 6.3.6 | O teste falha antes e passa depois da etapa |
| P1 + P3 | **Ciclo de fidelidade em Bangkok** (grátis, 1 teste/min): depois de cada etapa, teste `--completo` e `py comparar.py` | Primeira janela divergente indicada ao P2 |
| P4 | `py analise/viabilidade.py <AG>` para cada agência. Ler e anotar no relatório: demanda por dia e hora, energia por dia, abre à noite (ponta importa)?, carros que não aproveitam DC, entrada mínima | Uma hipótese de configuração por agência |
| P5 | Esqueleto do dashboard com os dados de Bangkok (`simular.py --series`). Registro de decisões no ar | Dashboard abre com dados de exemplo |

### Fase 2 · Neblina, fidelidade total e leitura dos pesos (~H2:30 a H4)

| Quem | Tarefa | Pronto quando |
|---|---|---|
| P3 (+P2 integra) | Etapa 6 (`menor_soc` em km, `proxima_retirada`: 6.3.3 gera C,D,B,A). Etapa 7 só se houver evento anunciado | `comparar.py` OK em todas as combinações de política |
| P1 | Bateria em Bangkok: 3 prioridades × 2 divisões × evitar_ponta × limite apertado/folgado | Etapa 8 do kit: OK em todas |
| P4 | `py analise/busca.py <AG>` nas agências liberadas. Ranking por métricas (sem nota ainda). **Leitura da Neblina (opcional, prêmio):** pares de testes que diferem em uma coisa só para estimar pesos | Top 3 por agência |
| P1 | Monitorar `status` a cada ~15 min: novas agências → `kit`; eventos → salvar `operacao/status_ultimo.json` | Nenhuma agência sem kit |

### H4 · Revelação (Clara)

| Quem | Tarefa |
|---|---|
| P1 | `py operacao/juiz.py catalogo` (salva `dados/catalogo.json` com custos e pesos) e `instrucoes` (salva `docs/anexo_h4.md`) |
| P4 | Rodar `busca.py` de novo **com nota**. Comparar com o que foi inferido na Neblina |
| P5 | Atualizar o dashboard com a cascata de pontos |

### Fase 3 · Clara, decidir e enviar (H4 a ~H7)

| Quem | Tarefa | Pronto quando |
|---|---|---|
| P4 | Por agência: top 3 local com nota. Teste de robustez: demanda ±20%, um carregador a menos, evento | Candidato escolhido por agência |
| P1 | Confirmar no juiz só o 1º colocado (placar, 20). Completo só se a nota divergir do local | Diferença local × juiz < 1% |
| P1 | **1º envio final de cada agência** (grátis) assim que houver candidato confirmado | `finais` = número de agências liberadas |
| Todos | Agências liberadas tarde: mesmo pipeline (kit → viabilidade → busca → placar → final) em ~30 min | — |
| P1 + P4 | Eventos ao vivo: simular com `--eventos operacao/status_ultimo.json`, decidir se o reenvio (80, 160…) compensa | Decisão registrada |

### Fase 4 · Fechamento (H7 a H7:30)

- **H7:00:** checagem. Toda agência liberada tem envio final? Sem envio = 0 pontos.
- Reenvio só com ganho local claro **e** saldo. O desempate favorece menos perdidos, menor custo de obra e envio mais cedo.
- **H7:30:** congelamento. A API fica só em leitura.

### Fase 5 · Apresentação (H7:30 a H8, apresentações H8 a H11)

- P5 fecha o dashboard (13.1) e o PDF. Roteiro do 13.2 (12 min + 5 de perguntas): estratégia → leitura da Neblina → modelo próprio vs. juiz → decisões por agência → eventos → com mais tempo.
- Números conferidos no `log_juiz.csv` e nos relatórios. Ensaio cronometrado.

---

## Método: toda submissão é uma hipótese

Nada vai ao juiz sem estar registrado em `analise/hipoteses.py`. O caderno guarda a previsão do nosso motor **antes** do teste e a resposta do juiz **depois**. A diferença entre as duas mede a fidelidade do motor (prêmio de modelagem); a diferença contra a base mede os pesos (prêmio de leitura da Neblina).

1. **Formular** (P4): uma frase testável, mudando **uma coisa só** em relação a uma base. Ex.: "evitar_ponta zera a ponta sem perder clientes; a nota sobe".
2. **Registrar e prever** (P4): `py analise/hipoteses.py nova H09 SUB.json "frase" --base E3`. Grava a submissão normalizada e as métricas previstas pelo motor.
3. **Testar** (P1): `py operacao/juiz.py teste Bangkok SUB.json --completo`. Para nota vista no console web: `checar --manual`.
4. **Checar** (P4): `py analise/hipoteses.py checar H09`. Encontra a resposta no `log_juiz.csv`, compara previsto × juiz e calcula Δnota contra a base:
   - só a ponta mudou → `w_ponta`;
   - só a obra mudou → custo da obra em pontos (por unidade, se for um único tipo);
   - motor divergiu → leitura marcada **NÃO CONFIÁVEL** e o P2/P3 roda `comparar.py`.
5. **Concluir** (quem decidiu): `py analise/hipoteses.py concluir H09 "texto"`.
6. **Publicar**: `py analise/hipoteses.py relatorio` gera `registro/hipoteses.md`, tabela pronta para o dashboard e o pitch.

**Nota local de todos os JSON:** `py analise/nota_local.py` usa o nosso motor e `analise/pesos_custos.json` (cada peso e custo com a fonte). Gera `registro/notas_locais.md` (ranking) e `registro/matriz_rastreabilidade.md`/`.csv` (item da nota × regra do motor × peso/custo × juiz). A cada teste novo: salvar o par `X.sub.json` + `X.json` em `operacao/respostas/<AG>/`, preencher o custo descoberto em `pesos_custos.json` e rodar de novo.

Hipóteses pré-registradas para Bangkok: E1–E8 (`kit_kickoff/kit_kickoff/submissoes/neblina_bangkok/LEIAME.md`).

## Orçamento de m7Coins (1.000)

| Uso | m7Coins | Observação |
|---|---|---|
| Bangkok (fidelidade) | 0 | Ilimitado até o congelamento; cooldown de 1 min; teste idêntico não consome |
| Leitura da Neblina (até H4) | até 200 | ~10 testes placar, só depois de o motor bater com o juiz |
| Confirmar candidatos (Clara) | ~300 | 6 agências × (1–2 placar + 1 completo eventual a 30) |
| Eventos ao vivo | ~150 | Teste da reação na agência afetada |
| Reenvios finais | ~240 | 1º envio é grátis; reenvio: 80, 160, 320… por agência |
| Reserva para agências tardias | ~110 | Não gastar antes da última liberação |

Preços: placar 20, completo 50 (30 se o placar idêntico já foi pago). Cooldown: 5 min por agência para teste pago e 15 min por agência para envio final. `juiz.py` calcula o custo, confere o cooldown e só gasta com `--sim`.

---

## Mapa do repositório

```
ROADMAP.md                   este arquivo
.env.exemplo                 copiar para .env e preencher (não versionado)
docs/regulamento_resumo.md   regras e números do regulamento (texto pesquisável)
operacao/juiz.py             P1: única porta para a API (log, cache, custo, cooldown)
operacao/log_juiz.csv        histórico de chamadas (gerado)
operacao/respostas/<AG>/     submissão + resposta de cada teste (para comparar.py)
analise/viabilidade.py       P4: relatório técnico por agência
analise/busca.py             P4: grade de configurações → simulação local → ranking
dashboard/README.md          P5: checklist do dashboard obrigatório (13.1)
registro/registro_decisoes.md  decisões, gastos, pesos inferidos, eventos
kit_kickoff/kit_kickoff/     kit oficial (motor, simulador, comparador, dados)
```

## Comandos do dia a dia

```bash
# todos (dentro de kit_kickoff/kit_kickoff)
py -m unittest discover -s testes
py simular.py exemplo_submissao.json
py comparar.py SUB.json RESPOSTA.json

# P1 (na raiz do repositório)
py operacao/juiz.py status
py operacao/juiz.py kit Istanbul
py operacao/juiz.py teste Bangkok kit_kickoff/kit_kickoff/exemplo_submissao.json --completo
py operacao/juiz.py teste Istanbul sub.json --sim
py operacao/juiz.py final Istanbul sub.json --sim
py operacao/juiz.py gastos

# P4 (na raiz do repositório)
py analise/viabilidade.py Istanbul
py analise/busca.py Istanbul --top 15
```

## Base reaproveitada (pasta `Localiza_Hackathon/`)

| Arquivo | Para quê |
|---|---|
| `06_Kit_Pronto/identidade_visual/guia_visual_pitch.md` e `modelo_slides.html` | Cores da marca (#006828 · #78D91D · #EEF6C3) no dashboard e no PDF |
| `05_Metodo_Hackathon/pitch.md` | Dicas de apresentação (título = conclusão, ensaio cronometrado) |
| `12_Dia_21/registro_decisoes.md` | Modelo do registro, adaptado em `registro/` |
| `04_Ideathon_Set26/aprendizados.md` | Lições do ideathon (estrutura e prototipação foram elogiadas) |

O case de hoje é **técnico** (simulação e otimização), não de survey ou cliente. Por isso o cartão de ideia e o survey da base **não entram** no caminho crítico.
