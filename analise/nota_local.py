"""Nota local de cada submissão + matriz de rastreabilidade (nosso cálculo × juiz × fonte de cada peso e custo).

Usa o NOSSO motor para as métricas e analise/pesos_custos.json para pesos e custos (com a fonte de cada um).
Custo desconhecido não trava: a nota sai "parcial" (é um teto, pois obra só desconta) e a matriz diz o que falta.
Quando há resposta do juiz para a mesma submissão normalizada em operacao/respostas/<AG>/, compara item a item.

  py analise/nota_local.py [ARQ_OU_PASTA ...]   (padrão: kit_kickoff/kit_kickoff/submissoes)

Gera registro/notas_locais.md (ranking), registro/matriz_rastreabilidade.md e .csv.
"""
import csv
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
KIT = RAIZ / "kit_kickoff" / "kit_kickoff"
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(RAIZ / "operacao"))

import juiz  # noqa: E402
import simular  # noqa: E402
from kickoff import validar  # noqa: E402
from kickoff.dados import carregar  # noqa: E402
from kickoff.nota import ITENS  # noqa: E402

PESOS_CUSTOS = AQUI / "pesos_custos.json"
SAIDA = RAIZ / "registro"
RESPOSTAS = RAIZ / "operacao" / "respostas"

# item da nota -> requisito do motor que produz a métrica (docs/requisitos_regras_operacao.md) ou regra do catálogo
REGRA = {
    "certo": "RO-04, RO-05 (escolha do carro, sem upgrade)",
    "upgrade": "RO-05 (menor upgrade)",
    "nao_atendido": "RO-06 (cliente perdido)",
    "demanda_contratada": "6.2, 6.3.7 (validar.demanda_kw)",
    "energia_ponta_kwh": "RO-16 + medição RO-19",
    "infraestrutura": "7.1, 7.2 (custos do catálogo)",
}


def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(RAIZ)).replace("\\", "/")
    except ValueError:
        return str(p)


def arquivos(alvos) -> list:
    out = []
    for a in alvos:
        p = Path(a)
        out += sorted(p.rglob("*.json")) if p.is_dir() else [p]
    return [p for p in out if not p.name.endswith(".sub.json")]


def submissoes(p: Path) -> list:
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    lista = d if isinstance(d, list) else [d]
    return [(f"{rel(p)}#{i + 1}" if len(lista) > 1 else rel(p), s) for i, s in enumerate(lista)
            if isinstance(s, dict) and "carregadores" in s]


def custo_obra(norm: dict, cen, pc: dict) -> tuple:
    """(custo conhecido, [itens sem custo], [fontes usadas])."""
    total, faltam, fontes = 0.0, [], []
    for k, n in norm["carregadores"].items():
        c = pc["custos"]["carregadores"].get(k, {})
        if c.get("valor") is None:
            faltam.append(f"{n}× {k}")
        else:
            total += n * c["valor"]
            fontes.append(f"{k}={c['valor']} ({c['fonte']})")
    e = norm["entrada"]
    if e == cen.agencia.entrada_existente:
        fontes.append(f"entrada {e}=0 (existente)")
    else:
        c = pc["custos"]["entradas"].get(e, {})
        if c.get("valor") is None:
            faltam.append(f"entrada {e}")
        else:
            total += c["valor"]
            fontes.append(f"{e}={c['valor']} ({c['fonte']})")
    return total, faltam, fontes


def respostas_do_juiz(ag: str, cen) -> dict:
    """chave normalizada -> (arquivo, resposta) para tudo salvo em operacao/respostas/<AG>/ (juiz.py ou console)."""
    achadas = {}
    pasta = RESPOSTAS / ag
    # da mais antiga para a mais recente: a resposta mais nova de cada submissão prevalece
    for sub_path in sorted(pasta.glob("*.sub.json"), key=lambda p: p.stat().st_mtime) if pasta.is_dir() else []:
        resp_path = sub_path.with_name(sub_path.name[: -len(".sub.json")] + ".json")
        if not resp_path.exists():
            continue
        sub = json.loads(sub_path.read_text(encoding="utf-8-sig"))
        sub.setdefault("agencia", ag)
        if validar.validar(sub, cen):
            continue
        achadas[juiz.chave(validar.normalizar(sub, cen))] = (resp_path, json.loads(resp_path.read_text(encoding="utf-8")))
    return achadas


def avaliar(nome: str, sub: dict, pc: dict, cache: dict) -> dict:
    ag = sub.get("agencia", "Bangkok")
    if ag not in cache:
        cen = carregar(KIT / "dados", ag)
        cache[ag] = (cen, respostas_do_juiz(ag, cen))
    cen, juizes = cache[ag]
    erros = validar.validar(sub, cen)
    if erros:
        return {"nome": nome, "agencia": ag, "erros": erros}
    norm = validar.normalizar(sub, cen)
    r = simular.avaliar({**sub, "agencia": ag}, {ag: cen}, KIT / "dados", None, [], False)
    m = dict(r["metricas"])
    obra, faltam, fontes = custo_obra(norm, cen, pc)
    m["custo_infra"] = obra
    peso_ag = ag if ag in pc["pesos"] else pc["peso_padrao"]
    pesos = pc["pesos"][peso_ag]["valores"]
    itens = [[item, m[k], pesos[item], m[k] * pesos[item]] for item, k in ITENS]
    k = juiz.chave(norm)
    jz = juizes.get(k)
    return {
        "nome": nome, "agencia": ag, "norm": norm, "chave": k, "metricas": m, "itens": itens,
        "nota": sum(i[3] for i in itens), "parcial": bool(faltam), "faltam": faltam, "fontes_custo": fontes,
        "pesos_de": peso_ag, "pesos_hipotese": peso_ag != ag, "violacoes": r["violacoes"],
        "juiz": None if jz is None else {"arquivo": rel(jz[0]), **jz[1]},
    }


def conf(norm: dict) -> str:
    pol = norm["politica"]
    s = " + ".join(f"{q}× {k}" for k, q in norm["carregadores"].items()) + f" · {norm['entrada']}"
    if norm["demanda_contratada_kw"]:
        s += f" · dem {norm['demanda_contratada_kw']}"
    return s + f" · {pol['prioridade']}/{pol['divisao']}" + (" · evitar_ponta" if pol["evitar_ponta"] else "")


def num(x) -> str:
    if x is None:
        return "—"
    if x == 0:
        return "0"
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",") if isinstance(x, float) else f"{x:,}".replace(",", ".")


def itens_juiz(jz: dict) -> dict:
    if not jz:
        return {}
    if jz.get("pontos"):
        return {i[0]: i for i in jz["pontos"]["itens"]}
    return {}


def gerar(res: list, pc: dict) -> None:
    SAIDA.mkdir(exist_ok=True)
    ok = [r for r in res if "erros" not in r]
    ok.sort(key=lambda r: -r["nota"])

    # ---------- ranking ----------
    L = ["# Notas locais (nosso motor + pesos/custos conhecidos)", "",
         "> Gerado por `py analise/nota_local.py`. Nota **parcial** = falta custo de algum item; é um teto (a obra que falta só desconta).",
         "> Pesos e custos com a fonte de cada valor: `analise/pesos_custos.json` e a matriz de rastreabilidade.", "",
         "| # | Submissão | Configuração | Certos/Upg/Perd | Ponta kWh | Obra | Nota local | Nota juiz | Δ (local − juiz) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ok, 1):
        m, jz = r["metricas"], r["juiz"]
        obra = num(m["custo_infra"]) + (f" + ? ({', '.join(r['faltam'])})" if r["parcial"] else "")
        nota = ("≤ " if r["parcial"] else "") + num(r["nota"])
        nj = jz.get("nota") if jz else None
        delta = "—" if nj is None else (num(r["nota"] - nj) + (" ⚠" if abs(r["nota"] - nj) > 1e-6 else " ✔"))
        L.append(f"| {i} | `{r['nome']}` | {conf(r['norm'])} | {m['certos']}/{m['upgrades']}/{m['nao_atendidos']} | "
                 f"{num(m['energia_ponta_kwh'])} | {obra} | **{nota}** | {num(nj)} | {delta} |")
    for r in res:
        if "erros" in r:
            L.append(f"| — | `{r['nome']}` | inválida: {'; '.join(r['erros'])} | | | | | | |")
    (SAIDA / "notas_locais.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---------- matriz de rastreabilidade ----------
    M = ["# Matriz de rastreabilidade da nota", "",
         "> Gerado por `py analise/nota_local.py`. Liga cada item da nota (regulamento 8.1) à regra do motor que produz a",
         "> métrica, ao peso e ao custo usados (com a fonte) e ao valor que o juiz devolveu para a mesma submissão.", "",
         "## 1. Origem dos pesos", "", "| Agência | Item | Peso | Fonte |", "|---|---|---|---|"]
    for ag, p in pc["pesos"].items():
        for item, v in p["valores"].items():
            M.append(f"| {ag} | {item} | {num(float(v))} | {p['fonte']} |")
    M += ["", f"Agências sem pesos próprios usam os de **{pc['peso_padrao']}** (hipótese, marcada nas tabelas).", "",
          "## 2. Origem dos custos de obra", "", "| Tipo | Item | Custo | Fonte |", "|---|---|---|---|"]
    for tipo in ("carregadores", "entradas"):
        for k, c in pc["custos"][tipo].items():
            M.append(f"| {tipo} | {k} | {num(c['valor']) if c['valor'] is not None else '**?**'} | {c['fonte']} |")
    M += ["", "## 3. Item × regra × cálculo × juiz (submissões testadas no juiz)", ""]
    linhas_csv = []
    testadas = [r for r in ok if r["juiz"]]
    if not testadas:
        M.append("Nenhuma submissão com resposta do juiz em `operacao/respostas/`.")
    for r in testadas:
        jz, ij = r["juiz"], itens_juiz(r["juiz"])
        M += [f"### `{r['nome']}`", "",
              f"{conf(r['norm'])} · resposta: `{jz['arquivo']}` · pesos de {r['pesos_de']}", "",
              "| Item | Regra que gera a métrica | Métrica (motor) | Métrica (juiz) | Peso | Pontos (motor) | Pontos (juiz) | Bate? |",
              "|---|---|---|---|---|---|---|---|"]
        for item, valor, peso, pts in r["itens"]:
            j = ij.get(item)
            vj, pj = (j[1], j[3]) if j else (None, None)
            bate = "—" if j is None else ("sim" if abs(valor - vj) <= 1e-6 and abs(pts - pj) <= 1e-6 else "**não**")
            M.append(f"| {item} | {REGRA[item]} | {num(valor)} | {num(vj)} | {num(float(peso))} | {num(pts)} | {num(pj)} | {bate} |")
            linhas_csv.append([r["nome"], item, REGRA[item], valor, vj, peso, pts, pj, bate.replace("*", "")])
        nj = jz.get("nota")
        M += [f"| **nota** | | | | | **{num(r['nota'])}** | **{num(nj)}** | "
              f"{'sim' if nj is not None and abs(r['nota'] - nj) <= 1e-6 else '**não**'} |", ""]
        M.append("Custos usados: " + "; ".join(r["fontes_custo"]) + "")
        M.append("")
    M += ["## 4. Submissões ainda não testadas no juiz (previsão)", "",
          "| Submissão | Nota local | Itens (pontos) | O que falta para a nota ser exata |", "|---|---|---|---|"]
    for r in ok:
        if r["juiz"]:
            continue
        itens = " · ".join(f"{i[0]} {num(i[3])}" for i in r["itens"] if i[3])
        falta = ", ".join(r["faltam"]) or "nada"
        if r["pesos_hipotese"]:
            falta += f"; pesos de {r['pesos_de']} (hipótese)"
        M.append(f"| `{r['nome']}` | {('≤ ' if r['parcial'] else '')}{num(r['nota'])} | {itens} | {falta} |")
        for item, valor, peso, pts in r["itens"]:
            linhas_csv.append([r["nome"], item, REGRA[item], valor, "", peso, pts, "", "não testada"])
    (SAIDA / "matriz_rastreabilidade.md").write_text("\n".join(M) + "\n", encoding="utf-8")
    with (SAIDA / "matriz_rastreabilidade.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["submissao", "item", "regra", "metrica_motor", "metrica_juiz", "peso", "pontos_motor", "pontos_juiz", "bate"])
        w.writerows(linhas_csv)


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    alvos = (argv if argv is not None else sys.argv[1:]) or [str(KIT / "submissoes")]
    pc = json.loads(PESOS_CUSTOS.read_text(encoding="utf-8"))
    cache, res = {}, []
    for p in arquivos(alvos):
        for nome, sub in submissoes(p):
            res.append(avaliar(nome, sub, pc, cache))
    gerar(res, pc)
    ok = sorted((r for r in res if "erros" not in r), key=lambda r: -r["nota"])
    for r in ok[:10]:
        jz = r["juiz"]
        print(f"{('≤' if r['parcial'] else ' ')}{r['nota']:8.1f}  juiz={jz.get('nota') if jz else '—':>6}  {r['nome']}")
    print(f"\n{len(res)} submissões · registro/notas_locais.md · registro/matriz_rastreabilidade.md (.csv)")


if __name__ == "__main__":
    main()
