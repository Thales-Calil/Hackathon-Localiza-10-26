"""Roda hipóteses registradas no juiz, uma por vez respeitando o cooldown, e fecha o ciclo sozinho:

teste no juiz (operacao/juiz.py) -> checagem (analise/hipoteses.py) -> custos aprendidos com o custo_infra
(analise/pesos_custos.json) -> pesos da cascata -> nota local + matriz (analise/nota_local.py).

  py operacao/rodar_hipoteses.py H09 H13 H11 [--completo] [--sim] [--intervalo 62]

Em Bangkok o teste é grátis (cooldown de 1 min). Fora de Bangkok cada teste custa m7Coins e só sai com --sim.
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "analise"))

import hipoteses  # noqa: E402
import juiz  # noqa: E402
import nota_local  # noqa: E402

PESOS_CUSTOS = RAIZ / "analise" / "pesos_custos.json"


def passo(msg: str) -> None:
    print(f"\n[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def aprender(reg: dict, resp: dict, origem: str) -> list:
    """Atualiza pesos_custos.json com o que a resposta do juiz permite deduzir. Devolve o que aprendeu."""
    pc = json.loads(PESOS_CUSTOS.read_text(encoding="utf-8"))
    aprendeu = []
    norm, ag = reg["submissao"], reg["submissao"]["agencia"]

    itens = (resp.get("pontos") or {}).get("itens") or []
    if itens:
        valores = {i[0]: i[2] for i in itens}
        atual = pc["pesos"].get(ag)
        if atual is None:
            pc["pesos"][ag] = {"valores": valores, "fonte": f"cascata do juiz em {reg['id']} ({origem})"}
            aprendeu.append(f"pesos de {ag}: {valores}")
        elif atual["valores"] != valores:
            aprendeu.append(f"ATENÇÃO: pesos de {ag} mudaram: {atual['valores']} -> {valores}")
            pc["pesos"][ag] = {"valores": valores, "fonte": f"cascata do juiz em {reg['id']} ({origem}); antes: {atual['valores']}"}

    obra = (resp.get("metricas") or {}).get("custo_infra", resp.get("custo_infra"))
    if isinstance(obra, (int, float)):
        car = pc["custos"]["carregadores"]
        desconhecidos = [k for k in norm["carregadores"] if car.get(k, {}).get("valor") is None]
        conhecido = sum(q * car[k]["valor"] for k, q in norm["carregadores"].items() if k not in desconhecidos)
        existente = juiz.carregar(juiz.DADOS, ag).agencia.entrada_existente
        ent = norm["entrada"]
        ent_info = pc["custos"]["entradas"].get(ent, {"valor": None})
        ent_conhecida = ent == existente or ent_info.get("valor") is not None
        ent_valor = 0 if ent == existente else (ent_info.get("valor") or 0)
        if len(desconhecidos) == 1 and ent_conhecida:
            k = desconhecidos[0]
            q = norm["carregadores"][k]
            v = (obra - conhecido - ent_valor) / q
            car[k] = {"valor": v, "fonte": f"{reg['id']}: custo_infra {obra:g} − conhecidos {conhecido + ent_valor:g}, ÷ {q} ({origem})"}
            aprendeu.append(f"custo {k} = {v:g}")
        elif not desconhecidos and not ent_conhecida:
            v = obra - conhecido
            pc["custos"]["entradas"][ent] = {"valor": v, "fonte": f"{reg['id']}: custo_infra {obra:g} − carregadores {conhecido:g} ({origem})"}
            aprendeu.append(f"custo entrada {ent} = {v:g}")
        elif not desconhecidos and ent_conhecida and abs(conhecido + ent_valor - obra) > 1e-6:
            aprendeu.append(f"ATENÇÃO: custo_infra {obra:g} ≠ soma dos custos conhecidos {conhecido + ent_valor:g}")
    PESOS_CUSTOS.write_text(json.dumps(pc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return aprendeu


def ultima_resposta(reg: dict):
    achados = [l for l in juiz.ler_log() if l["acao"] == "teste" and l["chave"] == reg["chave"]
               and l["agencia"] == reg["submissao"]["agencia"] and not l["nota"].startswith("ERRO")]
    if not achados:
        return None, None
    arq = RAIZ / achados[-1]["arquivo"]
    return json.loads(arq.read_text(encoding="utf-8")), achados[-1]["arquivo"]


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="py operacao/rodar_hipoteses.py")
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--completo", action="store_true")
    ap.add_argument("--sim", action="store_true", help="autoriza gastar m7Coins (fora de Bangkok)")
    ap.add_argument("--intervalo", type=float, default=62, help="segundos entre testes (cooldown de Bangkok: 60)")
    a = ap.parse_args(argv)

    regs = hipoteses.ler()
    faltando = [i for i in a.ids if i not in regs]
    if faltando:
        raise SystemExit(f"hipóteses não registradas: {faltando}")

    passo("Conexão: GET /status")
    juiz.main(["status"])

    for n, hid in enumerate(a.ids):
        reg = hipoteses.ler()[hid]
        sub = RAIZ / reg["sub"]
        ag = reg["submissao"]["agencia"]
        passo(f"{hid}: teste no juiz ({ag}, {'completo' if a.completo else 'placar'}) · {reg['hipotese']}")
        args = ["teste", ag, str(sub)] + (["--completo"] if a.completo else []) + (["--sim"] if a.sim else [])
        for tentativa in range(3):
            try:
                juiz.main(args)
                break
            except SystemExit as e:
                msg = str(e)
                print(f"  {msg}")
                if "cooldown" in msg and tentativa < 2:
                    time.sleep(a.intervalo)
                    continue
                break

        resp, arq = ultima_resposta(reg)
        if resp is None:
            passo(f"{hid}: sem resposta válida do juiz; segue para a próxima")
            continue
        passo(f"{hid}: checagem previsto × juiz")
        hipoteses.main(["checar", hid])
        for item in aprender(reg, resp, arq):
            print(f"  aprendido: {item}")
        if n < len(a.ids) - 1:
            print(f"  aguardando {a.intervalo:.0f} s (cooldown)", flush=True)
            time.sleep(a.intervalo)

    passo("Nota local de todos os JSON + matriz de rastreabilidade")
    hipoteses.main(["relatorio"])
    nota_local.main([])


if __name__ == "__main__":
    main()
