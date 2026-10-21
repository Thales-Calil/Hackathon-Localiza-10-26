"""Caderno de hipóteses: cada submissão testada no juiz nasce como hipótese, com previsão do nosso motor.

Fluxo: nova (registra e prevê) -> P1 testa no juiz -> checar (compara previsto x juiz, calcula a leitura
contra a base) -> concluir (texto da conclusão) -> relatorio (registro/hipoteses.md).

  py analise/hipoteses.py nova ID SUB.json "hipótese" [--base ID] [--autor NOME]
  py analise/hipoteses.py checar ID [--resposta ARQ.json] [--manual nota=65 atendimento_pct=100 ...]
  py analise/hipoteses.py concluir ID "conclusão"
  py analise/hipoteses.py relatorio
  py analise/hipoteses.py listar

`checar` sem --resposta procura no operacao/log_juiz.csv o último teste com a mesma submissão normalizada.
--manual serve para notas vistas no console web (valores digitados).
"""
import argparse
import json
import os
import sys
from datetime import datetime
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

BASE = RAIZ / "registro" / "hipoteses.jsonl"
RELATORIO = RAIZ / "registro" / "hipoteses.md"

FISICAS = ("contratos", "atendimento_pct", "pico_kw", "energia_kwh")  # o juiz devolve já na Neblina
PONTUADAS = ("certos", "upgrades", "nao_atendidos", "energia_ponta_kwh", "demanda_contratada_kw")


def ler() -> dict:
    if not BASE.exists():
        return {}
    regs = [json.loads(l) for l in BASE.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {r["id"]: r for r in regs}


def gravar(regs: dict) -> None:
    BASE.parent.mkdir(exist_ok=True)
    BASE.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in regs.values()), encoding="utf-8")


def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(RAIZ)).replace("\\", "/")
    except ValueError:
        return str(p)


def prever(sub: dict) -> tuple:
    ag = sub["agencia"]
    cat_path = KIT / "dados" / "catalogo.json"
    cat = json.loads(cat_path.read_text(encoding="utf-8-sig")) if cat_path.exists() else None
    cen = carregar(KIT / "dados", ag, cat)
    erros = validar.validar(sub, cen)
    if erros:
        raise SystemExit("submissão inválida: " + "; ".join(erros))
    norm = validar.normalizar(sub, cen)
    r = simular.avaliar(sub, {ag: cen}, KIT / "dados", cat, [], False)
    return norm, juiz.chave(norm), {"nota": r.get("nota"), "metricas": r["metricas"], "violacoes": r["violacoes"]}


def cmd_nova(a) -> None:
    regs = ler()
    if a.id in regs and not a.substituir:
        raise SystemExit(f"{a.id} já existe (use --substituir)")
    if a.base and a.base not in regs:
        raise SystemExit(f"base {a.base} não registrada")
    sub = json.loads(Path(a.sub).read_text(encoding="utf-8-sig"))
    norm, k, prev = prever(sub)
    regs[a.id] = {
        "id": a.id, "criada_em": datetime.now().isoformat(timespec="seconds"),
        "autor": a.autor or os.environ.get("OPERADOR", os.environ.get("USERNAME", "")),
        "hipotese": a.hipotese, "base": a.base, "sub": rel(a.sub), "submissao": norm, "chave": k,
        "previsto": prev, "juiz": None, "checagem": None, "conclusao": None, "status": "aberta",
    }
    gravar(regs)
    m = prev["metricas"]
    print(f"{a.id} registrada (chave {k}). Previsão do motor: certos={m['certos']} upg={m['upgrades']} "
          f"perdidos={m['nao_atendidos']} ponta={m['energia_ponta_kwh']:.1f} kWh pico={m['pico_kw']:.1f} kW "
          f"nota={prev['nota']}")
    print(f"Teste no juiz: py operacao/juiz.py teste {sub['agencia']} {rel(a.sub)} --completo")


def resposta_do_juiz(reg: dict, a) -> tuple:
    if a.manual:
        r = {"metricas": {}}
        for par in a.manual:
            k, v = par.split("=", 1)
            (r if k == "nota" else r["metricas"])[k] = float(v.replace(",", "."))
        return r, "manual"
    if a.resposta:
        return json.loads(Path(a.resposta).read_text(encoding="utf-8-sig")), rel(a.resposta)
    achados = [l for l in juiz.ler_log() if l["acao"] == "teste" and l["chave"] == reg["chave"]
               and l["agencia"] == reg["submissao"]["agencia"] and not l["nota"].startswith("ERRO")]
    if not achados:
        raise SystemExit("nenhum teste com essa submissão no operacao/log_juiz.csv; use --resposta ou --manual")
    arq = RAIZ / achados[-1]["arquivo"]
    return json.loads(arq.read_text(encoding="utf-8")), rel(arq)


def comparar_modelo(prev: dict, jz: dict, manual: bool) -> list:
    """Divergências entre o nosso motor e o juiz nas métricas que o juiz devolveu."""
    div = []
    for k, vj in jz.get("metricas", {}).items():
        vp = prev["metricas"].get(k)
        if vp is None or not isinstance(vj, (int, float)):
            continue
        if k == "energia_kwh":
            ok = abs(vp - vj) <= 0.01 * max(abs(vj), 1e-9)
        elif manual:  # valor lido do console, arredondado na tela
            ok = abs(vp - vj) <= max(0.05, 0.001 * abs(vj))
        else:
            ok = abs(vp - vj) <= 1e-6
        if not ok:
            div.append(f"{k}: motor {vp:.4g} × juiz {vj:.4g}")
    return div


def leitura_contra_base(reg: dict, base: dict) -> dict:
    """Δnota do juiz contra a base e o que ele permite inferir (usa as métricas pontuadas do NOSSO motor)."""
    if not base or not base.get("juiz") or base["juiz"].get("nota") is None or reg["juiz"].get("nota") is None:
        return {}
    dn = reg["juiz"]["nota"] - base["juiz"]["nota"]
    mp, mb = reg["previsto"]["metricas"], base["previsto"]["metricas"]
    dm = {k: mp.get(k, 0) - mb.get(k, 0) for k in PONTUADAS if abs(mp.get(k, 0) - mb.get(k, 0)) > 1e-6}
    s, b = reg["submissao"], base["submissao"]
    mesma_obra = s["carregadores"] == b["carregadores"] and s["entrada"] == b["entrada"]
    out = {"delta_nota": dn, "delta_metricas_motor": dm, "mesma_obra": mesma_obra}
    if mesma_obra and list(dm) == ["energia_ponta_kwh"]:
        out["inferencia"] = f"w_ponta ≈ {-dn / dm['energia_ponta_kwh']:.4g} pontos por kWh na ponta"
    elif not mesma_obra and not dm:
        delta = {k: s["carregadores"].get(k, 0) - b["carregadores"].get(k, 0)
                 for k in sorted(set(s["carregadores"]) | set(b["carregadores"]))
                 if s["carregadores"].get(k, 0) != b["carregadores"].get(k, 0)}
        mudou = ", ".join(f"{q:+d} {k}" for k, q in delta.items())
        if s["entrada"] != b["entrada"]:
            mudou += (", " if mudou else "") + f"entrada {b['entrada']} → {s['entrada']}"
        texto = f"obra ({mudou}) mudou a nota em {dn:+.4g}: w_obra·Δcusto = {-dn:.4g} pontos"
        if len(delta) == 1 and s["entrada"] == b["entrada"]:
            (k, q), = delta.items()
            texto += f" → cada {k} ≈ {-dn / q:.4g} pontos de obra"
        out["inferencia"] = texto
    elif mesma_obra and set(dm) <= {"certos", "upgrades", "nao_atendidos"}:
        out["inferencia"] = (f"mesma obra, muda o atendimento ({dm}): Δnota {dn:+.4g} = "
                             "w_certo·Δcertos + w_upg·Δupg − w_perd·Δperdidos")
    else:
        out["inferencia"] = "mais de um item mudou: usar como equação no sistema de pesos"
    return out


def cmd_checar(a) -> None:
    regs = ler()
    reg = regs.get(a.id) or sys.exit(f"{a.id} não registrada")
    jz, fonte = resposta_do_juiz(reg, a)
    reg["juiz"] = {"nota": jz.get("nota"), "metricas": jz.get("metricas", {}), "violacoes": jz.get("violacoes", []),
                   "pontos": jz.get("pontos"), "fonte": fonte, "em": datetime.now().isoformat(timespec="seconds")}
    div = comparar_modelo(reg["previsto"], reg["juiz"], fonte == "manual")
    leitura = leitura_contra_base(reg, regs.get(reg.get("base")))
    base_ok = (regs.get(reg.get("base")) or {}).get("checagem", {}) or {}
    if leitura and (div or not base_ok.get("modelo_bate", True)):
        leitura["inferencia"] = "NÃO CONFIÁVEL (motor diverge do juiz aqui ou na base): " + leitura["inferencia"]
    reg["checagem"] = {"modelo_bate": not div, "divergencias": div, **leitura}
    reg["status"] = "testada"
    gravar(regs)
    c = reg["checagem"]
    obra = reg["juiz"]["metricas"].get("custo_infra", jz.get("custo_infra"))
    print(f"{a.id}: nota do juiz {reg['juiz']['nota']} · obra {obra if obra is not None else '?'} · "
          f"modelo {'BATE' if c['modelo_bate'] else 'DIVERGE'}")
    if jz.get("pontos"):
        print("  cascata: " + " · ".join(f"{i[0]} {i[1]:g}×{i[2]:g}={i[3]:g}" for i in jz["pontos"]["itens"]))
    for d in div:
        print(f"  ! {d}")
    if not c["modelo_bate"]:
        print("  -> rodar comparar.py com a resposta completa antes de usar esta hipótese para inferir pesos")
    if "delta_nota" in c:
        print(f"  Δnota vs {reg['base']}: {c['delta_nota']:+.4g} · Δmétricas (motor): {c['delta_metricas_motor']}")
        print(f"  leitura: {c['inferencia']}")


def cmd_concluir(a) -> None:
    regs = ler()
    reg = regs.get(a.id) or sys.exit(f"{a.id} não registrada")
    reg["conclusao"], reg["status"] = a.texto, "concluida"
    gravar(regs)
    print(f"{a.id} concluída")


def fmt(x, casas=1):
    return "—" if x is None else (f"{x:.{casas}f}" if isinstance(x, float) else str(x))


def cmd_relatorio(_a) -> None:
    regs = ler()
    L = ["# Caderno de hipóteses", "",
         "> Gerado por `py analise/hipoteses.py relatorio`. Não editar à mão: a fonte é `registro/hipoteses.jsonl`.", "",
         "| ID | Hipótese | Base | Submissão | Previsto (certos/upg/perd · ponta kWh) | Nota juiz | Obra juiz | Modelo bate? | Δnota | Leitura | Conclusão | Status |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in regs.values():
        m = r["previsto"]["metricas"]
        s = r["submissao"]
        pol = s["politica"]
        conf = (f"{json.dumps(s['carregadores'])} {s['entrada']}"
                + (f" dem {s['demanda_contratada_kw']}" if s["demanda_contratada_kw"] else "")
                + f" · {pol['prioridade']}/{pol['divisao']}" + (" · evitar_ponta" if pol["evitar_ponta"] else ""))
        c = r.get("checagem") or {}
        L.append("| " + " | ".join([
            r["id"], r["hipotese"], r.get("base") or "—", f"`{conf}`",
            f"{m['certos']}/{m['upgrades']}/{m['nao_atendidos']} · {m['energia_ponta_kwh']:.1f}",
            fmt((r.get("juiz") or {}).get("nota")),
            fmt(((r.get("juiz") or {}).get("metricas") or {}).get("custo_infra")),
            "—" if not c else ("sim" if c["modelo_bate"] else "**não**: " + "; ".join(c["divergencias"])),
            fmt(c.get("delta_nota")), c.get("inferencia", "—"), r.get("conclusao") or "—", r["status"],
        ]) + " |")
    RELATORIO.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"relatório: {rel(RELATORIO)} ({len(regs)} hipóteses)")


def cmd_listar(_a) -> None:
    for r in ler().values():
        print(f"{r['id']:6s} {r['status']:10s} nota={fmt((r.get('juiz') or {}).get('nota'))} {r['hipotese']}")


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="py analise/hipoteses.py")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("nova")
    p.add_argument("id")
    p.add_argument("sub")
    p.add_argument("hipotese")
    p.add_argument("--base")
    p.add_argument("--autor")
    p.add_argument("--substituir", action="store_true")
    p = sp.add_parser("checar")
    p.add_argument("id")
    p.add_argument("--resposta")
    p.add_argument("--manual", nargs="+", metavar="CHAVE=VALOR")
    p = sp.add_parser("concluir")
    p.add_argument("id")
    p.add_argument("texto")
    sp.add_parser("relatorio")
    sp.add_parser("listar")
    a = ap.parse_args(argv)
    {"nova": cmd_nova, "checar": cmd_checar, "concluir": cmd_concluir, "relatorio": cmd_relatorio,
     "listar": cmd_listar}[a.cmd](a)


if __name__ == "__main__":
    main()
