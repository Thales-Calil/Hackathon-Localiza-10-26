# Dashboard obrigatório (seção 13.1): papel P5

Prêmio especial "melhor dashboard": clareza, completude e uso de dados. Visual da marca: `Localiza_Hackathon/06_Kit_Pronto/identidade_visual/guia_visual_pitch.md` (#006828 · #78D91D · #EEF6C3).

## Checklist por agência

| Bloco | Fonte dos dados | Comando |
|---|---|---|
| Cascata de pontos ganhos e perdidos, **nosso modelo vs. juiz** | nosso: `pontos` do `simular.py` (pós-H4); juiz: `pontos` da resposta do teste (Clara) em `operacao/respostas/<AG>/` | `py simular.py SUB.json` |
| Curva de potência em 15 min **contra o limite** e a janela de ponta | `series.publico.potencia_kw` + limite (kW útil ou demanda) + faixas seg–sex 18–21h | `py simular.py SUB.json --series` |
| Ocupação de vagas e tamanho da fila ao longo do tempo | `series.publico.plugados_max`, `fila_max`, vagas da agência | idem |
| Distribuição de SOC na retirada e clientes perdidos por dia e hora | `series.publico.soc_retirada`, `nao_atendidos_min` | idem |

## Checklist consolidado

| Bloco | Fonte |
|---|---|
| m7Coins gastos por agência | `operacao/log_juiz.csv` (`py operacao/juiz.py gastos`) |
| Custo de obra (pontos) por agência | `custo_infra` do `simular.py` e da resposta do juiz (pós-H4) |
| Evolução da nota ao longo do dia | `operacao/log_juiz.csv` (coluna `nota` por hora e agência) + `GET /placar` |
| Justificativa de entrada e demanda contratada | `analise/relatorios/<AG>.md` + `analise/saida/<AG>_busca.csv` + `registro/registro_decisoes.md` |
| Fidelidade do modelo (prêmio de modelagem) | saídas do `comparar.py` por teste: % de métricas que batem, m7Coins gastos |

## Sugestão de formato

Uma página HTML estática (sem servidor) que lê os JSON gerados, uma aba por agência + aba "Consolidado". Gerar os dados com um script `dashboard/gerar_dados.py` que roda `simular.py --series` na submissão vigente de cada agência e junta com o `log_juiz.csv`. Começar com Bangkok e dados de exemplo enquanto o motor não está pronto.
