# Requisitos formais: regras de operação do motor

> Requisitos do simulador próprio (`kit_kickoff/kit_kickoff/kickoff/motor.py`), derivados do regulamento das equipes (seções 4, 5, 6.3 e 11). As regras valem **igualmente para todas as agências**; o que muda por agência são os dados (vagas, horário, frota, contratos, entrada existente) e a submissão (carregadores, entrada, demanda, política).
>
> Convenção: **DEVE** = obrigatório para bater com o juiz. Cada requisito aponta a fonte, o método que o implementa e o teste que o verifica (`testes/test_etapaN.py`).

## Glossário

| Termo | Definição |
|---|---|
| SOC | Estado de carga da bateria, em % (0–100) |
| Alvo | SOC de 80%, fixo, não configurável |
| Apto | Carro no pátio com SOC ≥ alvo |
| Pátio | Carros presentes na agência (aptos, na fila ou plugados) |
| Fila | Carros no pátio com SOC < alvo aguardando saída de carregador |
| Ponto | Instância de carregador instalada (ex.: `dc_60x2-0`); tem 1 ou 2 saídas |
| Degrau | Faixa de 5% de SOC; índice `i = min(19, floor(SOC/5))` |
| Curva | 20 valores de kW por modelo (AC e DC), um por degrau |
| Limite da agência | B3: kW útil da entrada; A4/SE: demanda contratada |
| Ponta | Seg–sex, 18:00 ≤ hora < 21:00 |
| t | Minutos desde 17/10/2049 00:00 (domingo); T0 = 1080 |

---

## RO-01 Ordem dos acontecimentos no mesmo minuto
- **Requisito:** quando vários acontecimentos ocorrem no mesmo minuto, o sistema DEVE processá-los na ordem: (1) devoluções; (2) abertura, início/fim da ponta e eventos; (3) fim de recarga; (4) retiradas; (5) fechamento. Empates dentro do mesmo tipo seguem a ordem de agendamento.
- **Fonte:** 5.1 · **Implementação:** constantes `PRIO_*` e `rodar` (prontos no kit).
- **Aceitação:** um carro devolvido apto pode ser retirado no mesmo minuto; um carro que atinge 80% às 08:00 atende uma retirada das 08:00.

## RO-02 SOC na devolução
- **Requisito:** ao agendar a devolução de um contrato atendido, o sistema DEVE calcular `SOC = km_devolucao ÷ autonomia_km do modelo entregue × 100`, limitado ao SOC com que o carro saiu. Sem `km_devolucao`, o SOC de saída é mantido.
- **Fonte:** 4.1 · **Implementação:** `soc_devolucao` · **Teste:** `test_soc_devolucao_pela_autonomia_do_modelo`.
- **Aceitação:** 162 km num Dolphin GS (291 km) → 55,67%; os mesmos 162 km num Kwid (185 km) → 80% (teto do SOC de saída).

## RO-03 Entrada no pátio
- **Requisito:** todo carro que chega (estoque em T0 ou devolução) DEVE entrar no pátio. Se SOC < alvo, DEVE entrar na fila registrando o instante de entrada; caso contrário, fica apto. Em seguida o sistema DEVE tentar plugar a fila (RO-08) e recalcular as potências (RO-09).
- **Fonte:** 5.2 · **Implementação:** `entrar_patio`, `on_devolucao` · **Teste:** `test_devolucao_abaixo_de_80_entra_na_fila`.

## RO-04 Elegibilidade na retirada
- **Requisito:** na retirada, só DEVEM ser elegíveis os carros do pátio com categoria ≥ categoria pedida **e** SOC ≥ alvo. Downgrade NÃO DEVE ocorrer.
- **Fonte:** 5.1 · **Implementação:** `escolher_carro` · **Teste:** `test_downgrade_nunca`.

## RO-05 Escolha do carro
- **Requisito:** entre os elegíveis, o sistema DEVE escolher pela ordem: menor upgrade (rank entregue − rank pedido) → menor SOC → não plugado antes de plugado → menor `id` alfabético.
- **Fonte:** 5.1, 6.3.1 · **Implementação:** `escolher_carro` · **Testes:** `test_631_*`, `test_empate_em_80_vai_pelo_menor_id`.
- **Aceitação (6.3.1, contrato Prata):** Geely 82%, Dolphin Mini 95% plugado, MG4 100%, JAC 100% → Geely. Geely a 78% → Dolphin Mini (desplugado na hora). Sem Prata apto → MG4.

## RO-06 Cliente perdido
- **Requisito:** sem carro elegível, o contrato DEVE ser registrado como não atendido no instante da retirada, sem espera nem reserva posterior. Todo contrato processado (atendido ou perdido) DEVE ser marcado como retirado para efeito de RO-07.
- **Fonte:** 5.1 · **Implementação:** `escolher_carro` + `on_retirada` (pronto) · **Teste:** `test_bangkok_sem_recarga_atende_so_o_estoque` (22 atendidos sem recarga).

## RO-07 Ordem da fila (`prioridade`)
- **Requisito:** a fila DEVE ser reordenada a cada tentativa de plugar, segundo a política:
  - `chegada`: menor instante de entrada na fila; carros da fila em T0 empatam;
  - `menor_soc`: menor autonomia restante em **km** (`autonomia_km × SOC/100`), não em %;
  - `proxima_retirada`: menor horário da próxima reserva compatível (primeiro contrato ainda não retirado, em ordem de horário, com categoria ≤ a do carro); sem reserva vai para o fim; empate pelo **maior** SOC.
  
  Em todas, o último desempate DEVE ser o menor `id`.
- **Fonte:** 6.3.3 · **Implementação:** `chave_prioridade`, `_proxima_reserva`, `ordenar_fila` · **Testes:** `test_633_*`.
- **Aceitação (6.3.3):** `menor_soc` A,B,D,C · `chegada` A,B,C,D · `proxima_retirada` C,D,B,A.

## RO-08 Plugar a fila
- **Requisito:** com a agência **aberta**, o sistema DEVE percorrer a fila na ordem de RO-07 e plugar cada carro no ponto escolhido por RO-10 enquanto houver saída livre em operação. Com a agência fechada, NÃO DEVE plugar. A tentativa DEVE ocorrer quando um carro chega, quando uma recarga termina, quando a agência abre e quando um carregador volta a operar.
- **Fonte:** 5.2, 6.3.3 · **Implementação:** `plugar_fila` · **Testes:** `test_fila_anda_quando_termina_a_recarga`, `test_fechada_nao_pluga`.

## RO-09 Ocupação
- **Requisito:** em todo instante, plugados ≤ saídas instaladas ≤ vagas elétricas. Violação DEVE ser registrada em `violacoes`.
- **Fonte:** 5.2, 6.2 · **Implementação:** `checar_ocupacao` (pronto), chamado em `plugar_fila` · **Teste:** `test_plugados_nunca_passam_das_saidas`.

## RO-10 Escolha do carregador
- **Requisito:** o carro DEVE ir para o ponto em operação, com saída livre, que lhe daria a maior potência estimada: a nominal do ponto dividida igualmente entre ele e os carros que ainda carregam ali (sobra redistribuída), cada um limitado pela própria curva (AC ou DC conforme o ponto). A estimativa NÃO DEVE considerar o limite da agência nem a `divisao`. Empate: o primeiro ponto em ordem alfabética do id (`ac_11, ac_22x2, ac_7, dc_120x2, dc_30, dc_60x2`). O carro NÃO DEVE trocar de ponto depois de plugado.
- **Fonte:** 6.3.4 · **Implementação:** `escolher_ponto` · **Teste:** `test_634_escolhe_o_dc60`.
- **Aceitação (6.3.4):** DC-60 com Geely 30% e AC-22 vazio; Dolphin GS 20% vai para o DC-60 (30 kW contra 7). O seguinte, com o DC-60 cheio, vai para o AC-22.

## RO-11 Potência, camada 1 (carregador)
- **Requisito:** em cada ponto, a potência nominal DEVE ser repartida só entre os carros conectados com SOC < alvo, com teto na curva de cada um no degrau atual: `igual` → enchimento de água (`potencia.enchimento_agua`); `prioridade` → sequencial na ordem de RO-07 (`potencia.sequencial`). Carro no alvo recebe 0. Ponto fora de operação e ponta com `evitar_ponta` dão 0 a todos.
- **Fonte:** 5.3, 6.3.5 · **Implementação:** `recalcular_potencias`.
- **Aceitação (6.3.5):** camada 1 `igual`: Geely 30, Dolphin GS 30, Kwid 26,6, JAC 16,45. `prioridade`: Geely 60, Dolphin GS 0, Kwid 26,6, JAC 16,45.

## RO-12 Potência, camada 2 (limite da agência)
- **Requisito:** a soma das potências DEVE ser ≤ limite da agência (B3: kW útil; A4/SE: demanda contratada), repartido com a mesma `divisao`, usando como teto de cada carro o valor da camada 1. As potências DEVEM ser recalculadas a cada mudança: plug, desplug, troca de degrau, início/fim da ponta, abertura e evento.
- **Fonte:** 5.3, 6.3.5, 6.3.7 · **Implementação:** `recalcular_potencias` · **Testes:** `test_635_*`, `test_pico_nunca_passa_do_limite_em_bangkok`.
- **Aceitação (6.3.5):** limite 40,5: `igual` 10,125 cada; `prioridade` Kwid 26,6, Geely 13,9, JAC 0, Dolphin 0. Limite 80: `igual` 21,1833 (JAC 16,45); `prioridade` Kwid 26,6, Geely 53,4.

## RO-13 Degraus e fim de recarga
- **Requisito:** a potência DEVE ser constante dentro de cada degrau de 5%. O sistema DEVE agendar o fim do degrau em `t + (limite − SOC)/100 × bateria/kW × 60` min, com `limite = min(alvo, 5·(i+1))`, invalidando agendamentos anteriores (token). Potência 0 → nenhum agendamento.
- **Fonte:** 5.3, 6.3.2 · **Implementação:** `agendar_fim_degrau`, `on_fim_recarga` · **Teste:** `test_632_dolphin_gs_20_a_80_no_dc60_em_36_7_min`.
- **Aceitação (6.3.2):** Dolphin GS (44,9 kWh) de 20% a 80% sozinho num DC-60, sem limite: 36,7 min.

## RO-14 Chegada ao alvo
- **Requisito:** ao atingir 80%, o carro DEVE ser desplugado se a agência estiver aberta e a fila DEVE ser replugada. Com a agência fechada, o carro DEVE continuar plugado a 0 kW, segurando a saída até a abertura.
- **Fonte:** 5.2 · **Implementação:** `on_fim_recarga` · **Testes:** `test_632_*`, `test_fechada_segura_a_saida_ate_abrir`.

## RO-15 Abertura e fechamento
- **Requisito:** com a agência fechada, NÃO DEVE haver retirada, plug ou desplug; a recarga DEVE continuar. Na abertura, o sistema DEVE desplugar os carros parados no alvo e depois plugar a fila.
- **Fonte:** 5.1, 5.2 · **Implementação:** `on_abertura`, `on_fechamento` · **Teste:** `test_fechada_segura_a_saida_ate_abrir`.

## RO-16 Horário de ponta
- **Requisito:** com `evitar_ponta`, de segunda a sexta das 18:00 às 21:00 todos os carros DEVEM ficar a 0 kW, permanecendo plugados; plugar continua permitido. Sem `evitar_ponta`, a energia nesse intervalo é medida como energia na ponta.
- **Fonte:** 5.3, 6.3.6 · **Implementação:** `on_ponta` + `recalcular_potencias` · **Testes:** `test_636_*`, `test_bangkok_evitar_ponta_zera_energia_na_ponta`.
- **Aceitação (6.3.6):** MG4 29%→80% num AC-22 a 11 kW, plugado seg 17:00: sem evitar termina 19:00; com evitar termina 22:00, com 0 kWh na ponta.

## RO-17 Retirada de carro plugado
- **Requisito:** um carro retirado plugado DEVE ser desplugado na hora e as potências recalculadas.
- **Fonte:** 5.1 · **Implementação:** `on_retirada` (pronto).

## RO-18 Eventos ao vivo
- **Requisito:** eventos anunciados DEVEM ser aplicados na agência e no instante indicados, recalculando as potências; ao voltar um carregador, a fila DEVE ser replugada. Carros plugados num carregador fora de operação ficam a 0 kW sem desplugar.
- **Fonte:** 11 · **Implementação:** `agendar_eventos`, `on_evento` · **Testes:** `test_etapa7.py`.
- **⚠ Provisório:** o formato de `params` só será conhecido no anúncio. Assumido: `[inicio_min, agencia, tipo, fim_min, valor]`, com `tipo` ∈ {`limite_kw`, `carregador_fora`}. Formato desconhecido gera um aviso em `Motor.avisos` e é ignorado. **Ajustar no primeiro anúncio** e validar com `comparar.py --eventos`.

## RO-19 Medição
- **Requisito:** energia e pico DEVEM ser medidos em janelas de 15 min; métricas só na janela avaliada (pública: 4 semanas a partir de T0), embora a simulação cubra o horizonte inteiro.
- **Fonte:** 4.2, 5.3 · **Implementação:** `Medidor` e `avancar` (prontos).

---

## Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF-01 | Determinismo: a mesma submissão DEVE gerar sempre o mesmo resultado (desempates explícitos por `id`) |
| RNF-02 | Tolerância numérica: comparações de SOC com o alvo usam ε = 1e-6; ao fim do degrau, o resíduo da integração é eliminado |
| RNF-03 | Só biblioteca padrão do Python 3.10+ |
| RNF-04 | Desempenho: uma simulação de 4+ semanas em ~0,5 s, permitindo buscas de milhares de configurações |
| RNF-05 | Fidelidade: `comparar.py` DEVE imprimir `OK: bate com o juiz` em Bangkok para todas as combinações de política (etapa 8) |

## Suposições a validar com o juiz (Bangkok, grátis)

| ID | Suposição | Onde | Como validar |
|---|---|---|---|
| S-01 | Na estimativa de RO-10, carro parado no alvo ocupando saída não absorve potência (cap 0) | `escolher_ponto` | Submissão com `ac_22x2` ou `dc_60x2` e agência fechando com carros a 80%; `comparar.py` |
| S-02 | `divisao: prioridade` também ordena a camada 1 dentro do carregador | `recalcular_potencias` | Já confirmada pelo exemplo 6.3.5 (Dolphin GS com 0 na camada 1) |
| S-03 | "Contrato ainda não retirado" = contrato ainda não processado (atendido ou perdido) | `_proxima_reserva` | Teste com `proxima_retirada` |
| S-04 | Com `chegada`, carros do estoque em T0 (fora da fila) não têm instante de entrada | `chave_prioridade` | Só afeta `divisao: prioridade`; conferir com o juiz |
| S-05 | Formato dos eventos (RO-18) | `agendar_eventos` | Anúncio oficial |
| S-06 | `autonomia_min_retirada_km` não é usado pelo juiz (só SOC ≥ 80%) | `escolher_carro` | Pergunta aos instrutores |

## Rastreabilidade

| Etapa do kit | Requisitos | Arquivo de teste |
|---|---|---|
| 2 | RO-02 a RO-06 | `test_etapa2.py` |
| 3 | RO-08 a RO-11, RO-13, RO-14 | `test_etapa3.py` |
| 4 | RO-11, RO-12 | `test_etapa4.py` |
| 5 | RO-15, RO-16 | `test_etapa5.py` |
| 6 | RO-07 | `test_etapa6.py` |
| 7 | RO-18 | `test_etapa7.py` |
| 8 | RNF-05 | `comparar.py` contra o juiz |
