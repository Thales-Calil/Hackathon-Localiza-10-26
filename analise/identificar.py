"""Descobre qual submissão gerou uma resposta do juiz (a resposta não traz a submissão).

Simula com o nosso motor todas as submissões conhecidas da agência (JSON em kit_kickoff/kit_kickoff/submissoes
e operacao/respostas/<AG>/*.sub.json) e compara com as métricas da resposta: energia_kwh distingue até
submissões com a mesma nota.

  py analise/identificar.py RESPOSTA.json [--agencia AG] [--eventos operacao/status_ultimo.json]
"""
import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
KIT = RAIZ / "kit_kickoff" / "kit_kickoff"
sys.path.insert(0, str(KIT))

import simular  # noqa: E402
from kickoff import validar  # noqa: E402
from kickoff.dados import carregar  # noqa: E402

CAMPOS = ("certos", "upgrades", "nao_atendidos", "energia_kwh", "energia_ponta_kwh", "pico_kw", "custo_infra",
          "demanda_contratada_kw")


def candidatas(ag: str) -> list:
    out = []
    for p in sorted((KIT / "submissoes").rglob("*.json")) + sorted((RAIZ / "operacao" / "respostas" / ag).glob("*.sub.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except ValueError:
            continue
        for i, s in enumerate(d if isinstance(d, list) else [d]):
            if isinstance(s, dict) and "carregadores" in s and s.get("agencia", ag) == ag:
                out.append((f"{p.relative_to(RAIZ)}" + (f"#{i + 1}" if isinstance(d, list) else ""), {**s, "agencia": ag}))
    return out


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="py analise/identificar.py")
    ap.add_argument("resposta")
    ap.add_argument("--agencia")
    ap.add_argument("--eventos", default=str(RAIZ / "operacao" / "status_ultimo.json"))
    a = ap.parse_args(argv)

    resp = json.loads(Path(a.resposta).read_text(encoding="utf-8-sig"))
    ag = a.agencia or resp.get("agencia")
    mj = resp.get("metricas", {})
    cat = json.loads((KIT / "dados" / "catalogo.json").read_text(encoding="utf-8-sig"))
    cen = carregar(KIT / "dados", ag, cat)
    eventos = simular.ler_eventos(a.eventos if Path(a.eventos).exists() else None)

    vistas, achou = set(), []
    for nome, sub in candidatas(ag):
        if validar.validar(sub, cen):
            continue
        chave = json.dumps(validar.normalizar(sub, cen), sort_keys=True)
        if chave in vistas:
            continue
        vistas.add(chave)
        r = simular.avaliar(sub, {ag: cen}, KIT / "dados", cat, eventos, False)
        m = r["metricas"]
        difs = [k for k in CAMPOS if k in mj and k in m and abs(float(m[k]) - float(mj[k])) > max(1e-6, 1e-9 * abs(float(mj[k])))]
        if not difs:
            achou.append((nome, validar.normalizar(sub, cen), r.get("nota")))

    print(f"Resposta: nota {resp.get('nota')} · energia {mj.get('energia_kwh')} · {len(vistas)} submissões de {ag} simuladas")
    if not achou:
        print("Nenhuma submissão conhecida reproduz essa resposta. Salve a submissão usada (JSON do console) "
              "ao lado da resposta como X.sub.json.")
    for nome, norm, nota in achou:
        pol = norm["politica"]
        print(f"\n✔ {nome}\n  carregadores {norm['carregadores']} · entrada {norm['entrada']}"
              + (f" · demanda {norm['demanda_contratada_kw']}" if norm["demanda_contratada_kw"] else "")
              + f" · {pol['prioridade']}/{pol['divisao']}" + (" · evitar_ponta" if pol["evitar_ponta"] else "")
              + f" · nota local {nota}")
    if len(achou) > 1:
        print("\nMais de uma submissão reproduz exatamente a resposta: elas são equivalentes para o juiz.")


if __name__ == "__main__":
    main()
