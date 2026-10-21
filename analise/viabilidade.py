"""Viabilidade técnica de uma agência (papel P4): demanda, energia, carro × carregador, entrada, ponta.

Não depende do motor: só lê o kit da agência. Gera analise/relatorios/<AG>.md e imprime o mesmo texto.

  py analise/viabilidade.py AG [--dados DIR]
"""
import argparse
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent / "kit_kickoff" / "kit_kickoff"
sys.path.insert(0, str(KIT))

from kickoff import tempo  # noqa: E402
from kickoff.dados import carregar  # noqa: E402

DIAS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")
SOC_ALVO = 80
ORDEM_CARREGADORES = ("ac_7", "ac_11", "ac_22x2", "dc_30", "dc_60x2", "dc_120x2")


def hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def recarga_sozinho(modelo, car, de=20, ate=SOC_ALVO):
    """(kW médio, minutos) de `de`% a `ate`% sozinho no carregador, sem limite da agência."""
    curva = modelo.curva_ac if car.tipo == "AC" else modelo.curva_dc
    passo_kwh = modelo.bateria_kwh * 0.05
    horas = 0.0
    for i in range(de // 5, ate // 5):
        p = min(car.potencia_kw, curva[min(19, i)])
        if p <= 0:
            return 0.0, math.inf
        horas += passo_kwh / p
    energia = passo_kwh * (ate - de) / 5
    return energia / horas, horas * 60


def tabela(cab, linhas) -> list:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(str(x) for x in l) + " |" for l in linhas]
    return out


def relatorio(cen) -> str:
    ag = cen.agencia
    L = [f"# Viabilidade técnica: {ag.nome}", ""]
    ent0 = cen.entradas[ag.entrada_existente]

    # ---------- agência ----------
    noite = [DIAS[d] for d in range(5) if ag.horario[d] and ag.horario[d][1] > tempo.PONTA[0]]
    horas_abertas = sum((h[1] - h[0]) / 60 for h in ag.horario if h)
    L += ["## Agência", ""]
    L += tabela(["Item", "Valor"], [
        ["Vagas elétricas (máx. de saídas)", ag.vagas],
        ["Frota", ag.frota],
        ["Entrada existente", f"{ent0.id} ({ent0.kw_util:g} kW úteis)"],
        ["Horário", " · ".join(f"{DIAS[d]} {hhmm(h[0])}-{hhmm(h[1])}" if h else f"{DIAS[d]} fechado"
                               for d, h in enumerate(ag.horario))],
        ["Horas abertas por semana", f"{horas_abertas:g}"],
        ["Aberta na ponta (seg–sex 18–21h)?", ", ".join(noite) if noite else "não: a ponta cai com a agência fechada"],
    ])

    # ---------- frota ----------
    L += ["", "## Frota em T0", ""]
    por_modelo = Counter((v.categoria, v.modelo) for v in cen.veiculos)
    situ = Counter(v.situacao for v in cen.veiculos)
    L += tabela(["Categoria", "Modelo", "Qtd"],
                [[c, m, n] for (c, m), n in sorted(por_modelo.items(), key=lambda x: (cen.categorias[x[0][0]], x[0][1]))])
    L += ["", "Situação: " + ", ".join(f"{k}={v}" for k, v in sorted(situ.items()))]

    # ---------- demanda ----------
    ini, fim = tempo.JANELA_PUBLICA
    ctr = [c for c in cen.contratos if ini <= c.retirada_t < fim]
    dias = max(1, (fim - ini) // tempo.DIA)
    por_cat = Counter(c.categoria for c in ctr)
    por_dia_sem = Counter(tempo.dia_semana(c.retirada_t) for c in ctr)
    por_hora = Counter((c.retirada_t % tempo.DIA) // 60 for c in ctr)
    por_data = Counter(c.retirada_t // tempo.DIA for c in ctr)
    duracoes = [(c.devolucao_t - c.retirada_t) / 60 for c in ctr if c.devolucao_t]
    L += ["", "## Demanda (janela pública, 4 semanas)", ""]
    L += [f"- **{len(ctr)} contratos**, média de {len(ctr) / dias:.1f} por dia; dia mais cheio: "
          f"{max(por_data.values()) if por_data else 0} retiradas."]
    if duracoes:
        L += [f"- Duração do contrato: mediana {statistics.median(duracoes):.1f} h "
              f"(p10 {statistics.quantiles(duracoes, n=10)[0]:.1f} h, p90 {statistics.quantiles(duracoes, n=10)[-1]:.1f} h)."]
    L += ["", *tabela(["Categoria", "Contratos", "% do total"],
                      [[k, por_cat[k], f"{100 * por_cat[k] / max(1, len(ctr)):.0f}%"]
                       for k in sorted(por_cat, key=lambda x: cen.categorias[x])])]
    L += ["", *tabela(["Dia", "Retiradas"], [[DIAS[d], por_dia_sem.get(d, 0)] for d in range(7)])]
    pico_h = sorted(por_hora.items(), key=lambda x: -x[1])[:4]
    L += ["", "Horas com mais retiradas: " + ", ".join(f"{h:02d}h ({n})" for h, n in pico_h) + "."]

    # ---------- energia ----------
    medio = defaultdict(lambda: [0.0, 0.0])  # categoria -> [bateria média, autonomia média]
    for cat in cen.categorias:
        ms = [m for m in cen.modelos.values() if m.categoria == cat]
        if ms:
            medio[cat] = [statistics.mean(m.bateria_kwh for m in ms), statistics.mean(m.autonomia_km for m in ms)]
    energia_dia = Counter()
    abaixo = devol = fora_horario = 0
    for c in ctr:
        if c.devolucao_t is None or c.km_devolucao is None:
            continue
        bat, aut = medio[c.categoria]
        soc = min(100.0, c.km_devolucao / aut * 100)
        devol += 1
        if soc < SOC_ALVO:
            abaixo += 1
            energia_dia[c.devolucao_t // tempo.DIA] += bat * (SOC_ALVO - soc) / 100
        if not tempo.aberta(ag, c.devolucao_t):
            fora_horario += 1
    for v in cen.veiculos:
        m = cen.modelos[v.modelo]
        if v.situacao == "estoque_a_carregar":
            energia_dia[tempo.T0 // tempo.DIA] += m.bateria_kwh * max(0, SOC_ALVO - v.soc) / 100
        elif v.situacao == "em_contrato" and v.devolucao_t is not None and v.soc_devolucao is not None:
            energia_dia[v.devolucao_t // tempo.DIA] += m.bateria_kwh * max(0, SOC_ALVO - v.soc_devolucao) / 100
    total = sum(energia_dia.values())
    max_dia = max(energia_dia.values()) if energia_dia else 0
    L += ["", "## Energia a repor (estimativa)", "",
          "Estimativa com a bateria e a autonomia **médias da categoria pedida** (o juiz usa o modelo que saiu, "
          "que pode ser um upgrade). Serve para dimensionar a potência; não substitui a simulação.", ""]
    L += tabela(["Indicador", "Valor"], [
        ["Devoluções com SOC < 80% (vão para a fila)", f"{abaixo} de {devol} ({100 * abaixo / max(1, devol):.0f}%)"],
        ["Devoluções com a agência fechada", f"{fora_horario} (só plugam na abertura)"],
        ["Energia total na janela", f"{total:,.0f} kWh"],
        ["Média por dia", f"{total / dias:,.0f} kWh"],
        ["Pior dia", f"{max_dia:,.0f} kWh"],
        ["Potência média se carregasse 24 h", f"{total / dias / 24:,.1f} kW"],
        ["Potência média só nas horas abertas", f"{total / max(1, horas_abertas * dias / 7):,.1f} kW"],
        [f"Pior dia em 10 h de recarga", f"{max_dia / 10:,.1f} kW"],
    ])
    L += ["", f"Comparar com a entrada existente: **{ent0.kw_util:g} kW úteis**. "
              "Se a potência média passa perto do limite, a fila cresce e clientes se perdem."]

    # ---------- carro × carregador ----------
    cars = [cen.carregadores[k] for k in ORDEM_CARREGADORES if k in cen.carregadores]
    L += ["", "## Carro × carregador (20% → 80%, sozinho, sem limite da agência)", "",
          "Célula = kW médio · minutos. Em 2 saídas, cada carro recebe metade do nominal quando as duas estão ocupadas.", ""]
    linhas = []
    for m in sorted(cen.modelos.values(), key=lambda m: (m.rank, m.modelo)):
        cel = []
        for car in cars:
            kw, mins = recarga_sozinho(m, car)
            cel.append(f"{kw:.1f} · {mins:.0f}" if math.isfinite(mins) else "—")
        linhas.append([f"{m.modelo} ({m.categoria})", *cel])
    L += tabela(["Modelo", *[c.id for c in cars]], linhas)

    L += ["", "**Leitura rápida:**"]
    for m in sorted(cen.modelos.values(), key=lambda m: (m.rank, m.modelo)):
        pico_ac, pico_dc = max(m.curva_ac), max(m.curva_dc)
        L.append(f"- {m.modelo}: pico na curva AC {pico_ac:.1f} kW, DC {pico_dc:.1f} kW."
                 + (" DC-120 não acelera em relação ao DC-60 sozinho." if pico_dc <= 60 else "")
                 + (" DC-30 já entrega quase tudo." if pico_dc <= 32 else "")
                 + (" AC-22 não acelera em relação ao AC-11." if pico_ac <= 11 else ""))

    # ---------- entrada ----------
    L += ["", "## Entradas possíveis (nunca descer)", ""]
    linhas = []
    for e in sorted(cen.entradas.values(), key=lambda e: e.kva):
        if e.kva < ent0.kva or (e.id == "b3_45" and ent0.id != "b3_45"):
            continue
        linhas.append([e.id, f"{e.kw_util:g}", "não (B3)" if e.kva <= 75 else "sim (30 até o teto, passo 10)",
                       f"{int(e.kw_util // 30)}× DC-30 ou {int(e.kw_util // 60)}× DC-60 cheios",
                       "existente (custo 0)" if e.id == ent0.id else "ampliação (custo cheio, H4)"])
    L += tabela(["Entrada", "kW útil", "Demanda contratada?", "Comporta", "Custo"], linhas)

    # ---------- hipóteses ----------
    L += ["", "## Hipóteses para a busca (conferir no simulador)", "",
          f"1. Saídas: no máximo {ag.vagas}. Começar pela energia/dia e testar de {max(1, ag.vagas // 3)} a {ag.vagas} saídas.",
          f"2. Entrada: a existente ({ent0.kw_util:g} kW) é grátis. Só ampliar se a simulação mostrar perdas que "
          "valem mais que a obra (H4) mais a demanda contratada.",
          "3. Política: " + ("`evitar_ponta` pode valer a pena (agência aberta na ponta); medir os clientes perdidos."
                             if noite else "`evitar_ponta` quase não muda nada (fechada na ponta), mas a recarga "
                             "noturna seguida pode cair na ponta: medir `energia_ponta_kwh`."),
          "4. `divisao: prioridade` concentra potência: bom quando o limite é apertado e há retiradas logo em seguida.",
          "5. `proxima_retirada` tende a servir melhor os contratos do dia seguinte; comparar com `menor_soc`.", ""]
    return "\n".join(L)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="py analise/viabilidade.py")
    ap.add_argument("agencia")
    ap.add_argument("--dados", type=Path, default=KIT / "dados")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    texto = relatorio(carregar(a.dados, a.agencia))
    saida = AQUI / "relatorios" / f"{a.agencia}.md"
    saida.parent.mkdir(exist_ok=True)
    saida.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"\n(salvo em {saida.relative_to(AQUI.parent)})")


if __name__ == "__main__":
    main()
