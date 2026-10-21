"""Busca de configurações por agência (papel P4): gera a grade, simula com o NOSSO motor e ranqueia.

Não chama a API. Com dados/catalogo.json pós-H4 ranqueia pela nota; antes, por clientes perdidos,
energia na ponta, saídas e entrada (menos é melhor).

  py analise/busca.py AG [--max-tipos 2] [--min-saidas 1] [--entradas existente|todas|b3_45,a4_150]
                         [--demandas 60,80] [--politicas padrao|todas] [--eventos ARQ] [--top 10]

Saídas: analise/saida/<AG>_busca.csv (tudo), <AG>_top.json (lista para simular.py) e
<AG>_melhor.json (uma submissão, pronta para `py operacao/juiz.py teste`).
"""
import argparse
import csv
import itertools
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent / "kit_kickoff" / "kit_kickoff"
sys.path.insert(0, str(KIT))

import simular  # noqa: E402
from kickoff.dados import carregar  # noqa: E402

POLITICAS_TODAS = [{"prioridade": p, "divisao": d, "evitar_ponta": e}
                   for p in ("menor_soc", "chegada", "proxima_retirada")
                   for d in ("igual", "prioridade") for e in (False, True)]


def combinacoes_carregadores(cen, max_tipos: int, min_saidas: int):
    """Todos os {modelo_id: qtd} com até `max_tipos` modelos e saídas entre min_saidas e as vagas."""
    vagas = cen.agencia.vagas
    tipos = sorted(cen.carregadores.values(), key=lambda c: c.id)
    for k in range(1, max_tipos + 1):
        for grupo in itertools.combinations(tipos, k):
            faixas = [range(1, vagas // c.saidas + 1) for c in grupo]
            for qtds in itertools.product(*faixas):
                saidas = sum(q * c.saidas for q, c in zip(qtds, grupo))
                if min_saidas <= saidas <= vagas:
                    yield {c.id: q for c, q in zip(grupo, qtds)}


def entradas_validas(cen, pedido: str) -> list:
    existente = cen.entradas[cen.agencia.entrada_existente]
    acima = [e for e in sorted(cen.entradas.values(), key=lambda e: e.kva)
             if e.kva >= existente.kva and (e.id != "b3_45" or existente.id == "b3_45")]
    if pedido == "existente":
        return [existente.id]
    if pedido == "todas":
        return [e.id for e in acima]
    ids = [x.strip() for x in pedido.split(",") if x.strip()]
    return [i for i in ids if i in {e.id for e in acima}]


def grade(cen, a) -> list:
    pols = POLITICAS_TODAS if a.politicas == "todas" else [{}]
    if getattr(a, "politica", None):
        pols = [json.loads(a.politica)]
    demandas = [int(x) for x in a.demandas.split(",")] if a.demandas else [None]
    if getattr(a, "hardware", None):
        # fase 2: parte dos hardwares (carregadores + entrada) de uma lista já ranqueada
        vistos, subs = set(), []
        for h in json.loads(Path(a.hardware).read_text(encoding="utf-8-sig")):
            chave = (json.dumps(h["carregadores"], sort_keys=True), h["entrada"])
            if chave in vistos:
                continue
            vistos.add(chave)
            b3 = cen.entradas[h["entrada"]].kva <= 75
            for dem in ([None] if b3 else demandas):
                for pol in pols:
                    s = {"agencia": cen.agencia.nome, "carregadores": h["carregadores"], "entrada": h["entrada"]}
                    if dem is not None:
                        s["demanda_contratada_kw"] = dem
                    if pol:
                        s["politica"] = pol
                    subs.append(s)
        return subs
    subs = []
    for car in combinacoes_carregadores(cen, a.max_tipos, a.min_saidas):
        for ent in entradas_validas(cen, a.entradas):
            b3 = cen.entradas[ent].kva <= 75
            for dem in ([None] if b3 else demandas):
                for pol in pols:
                    s = {"agencia": cen.agencia.nome, "carregadores": car, "entrada": ent}
                    if dem is not None:
                        s["demanda_contratada_kw"] = dem
                    if pol:
                        s["politica"] = pol
                    subs.append(s)
    return subs


def ordem(r: dict, com_nota: bool):
    m = r["metricas"]
    saidas = r["saidas"]
    if com_nota:
        return (-(r["nota"] or 0), m["nao_atendidos"], saidas)
    return (m["nao_atendidos"], m.get("energia_ponta_kwh", 0), m.get("demanda_contratada_kw", 0), saidas, r["kw_util"])


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="py analise/busca.py")
    ap.add_argument("agencia")
    ap.add_argument("--dados", type=Path, default=KIT / "dados")
    ap.add_argument("--max-tipos", type=int, default=2)
    ap.add_argument("--min-saidas", type=int, default=1)
    ap.add_argument("--entradas", default="existente")
    ap.add_argument("--demandas", default="", help="kW para A4/SE, ex.: 60,80,100 (vazio = teto da entrada)")
    ap.add_argument("--politicas", choices=("padrao", "todas"), default="padrao")
    ap.add_argument("--eventos", help="operacao/status_ultimo.json ou lista de params")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--hardware", help="fase 2: JSON (lista) com hardwares já ranqueados; varia política/demanda")
    ap.add_argument("--sufixo", default="", help="sufixo dos arquivos de saída (ex.: _fase2)")
    ap.add_argument("--politica", help='uma política fixa em JSON, ex.: \'{"prioridade": "proxima_retirada"}\'')
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    cat_path = a.dados / "catalogo.json"
    cat = json.loads(cat_path.read_text(encoding="utf-8-sig")) if cat_path.exists() else None
    cen = carregar(a.dados, a.agencia, cat)
    eventos = simular.ler_eventos(a.eventos)
    subs = grade(cen, a)
    print(f"{len(subs)} configurações para simular em {a.agencia}")

    cenarios, resultados, t0 = {a.agencia: cen}, [], time.time()
    for i, s in enumerate(subs, 1):
        r = simular.avaliar(s, cenarios, a.dados, cat, eventos, False)
        if r.get("valido") and not r.get("violacoes"):
            r["sub"] = s
            r["saidas"] = sum(q * cen.carregadores[k].saidas for k, q in s["carregadores"].items())
            r["kw_util"] = cen.entradas[s["entrada"]].kw_util
            resultados.append(r)
        if i % 50 == 0 or i == len(subs):
            print(f"  {i}/{len(subs)} · {time.time() - t0:.0f} s", flush=True)

    com_nota = any(r.get("nota") is not None for r in resultados)
    resultados.sort(key=lambda r: ordem(r, com_nota))

    saida = AQUI / "saida"
    saida.mkdir(exist_ok=True)
    colunas = ["nota", "contratos", "certos", "upgrades", "nao_atendidos", "atendimento_pct", "pico_kw",
               "energia_kwh", "energia_ponta_kwh", "demanda_contratada_kw", "custo_infra"]
    with (saida / f"{a.agencia}_busca{a.sufixo}.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["carregadores", "saidas", "entrada", "politica", *colunas])
        for r in resultados:
            m = r["metricas"]
            w.writerow([json.dumps(r["sub"]["carregadores"]), r["saidas"], r["sub"]["entrada"],
                        json.dumps(r["sub"].get("politica", "padrao")),
                        r.get("nota"), *[m.get(c, "") for c in colunas[1:]]])
    top = [r["sub"] for r in resultados[:a.top]]
    (saida / f"{a.agencia}_top{a.sufixo}.json").write_text(json.dumps(top, ensure_ascii=False, indent=1), encoding="utf-8")
    if top:
        (saida / f"{a.agencia}_melhor{a.sufixo}.json").write_text(json.dumps(top[0], ensure_ascii=False, indent=1),
                                                         encoding="utf-8")

    print(f"\nTop {min(a.top, len(resultados))} ({'por nota' if com_nota else 'sem nota: por perdidos, ponta, saídas'}):")
    for r in resultados[:a.top]:
        m = r["metricas"]
        print(f"  nota={r.get('nota')!s:>8} perdidos={m['nao_atendidos']:>4} atend={m['atendimento_pct']:>6}% "
              f"pico={m['pico_kw']:>6} ponta={m.get('energia_ponta_kwh', 0):>6} "
              f"{json.dumps(r['sub']['carregadores'])} {r['sub']['entrada']} {r['sub'].get('politica', '')}")
    print(f"\nArquivos em {saida.relative_to(AQUI.parent)}: {a.agencia}_busca.csv, {a.agencia}_top.json, {a.agencia}_melhor.json")
    if not com_nota:
        print("Sem catálogo pós-H4: a nota sai depois de `py operacao/juiz.py catalogo`.")


if __name__ == "__main__":
    main()
