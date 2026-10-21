"""Única porta da equipe para a API do juiz (papel P1).

Antes de cada chamada: valida a submissão localmente (inválida não sai daqui), reaproveita
teste idêntico já feito, calcula o custo em m7Coins, confere o cooldown local e só gasta
com --sim. Depois: salva submissão e resposta em operacao/respostas/<AG>/ e anota em
operacao/log_juiz.csv.

  py operacao/juiz.py status
  py operacao/juiz.py kit AG
  py operacao/juiz.py catalogo
  py operacao/juiz.py instrucoes
  py operacao/juiz.py teste AG SUB.json [--completo] [--sim] [--forcar]
  py operacao/juiz.py final AG SUB.json [--sim]
  py operacao/juiz.py gastos

--forcar: refaz um teste idêntico (use depois de um evento novo na agência).
Credenciais: GAMEDAY_URL e GAMEDAY_TOKEN no ambiente ou em .env na raiz do repositório.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
KIT = RAIZ / "kit_kickoff" / "kit_kickoff"
sys.path.insert(0, str(KIT))

from kickoff import validar  # noqa: E402
from kickoff.api import Cliente, ErroApi  # noqa: E402
from kickoff.dados import carregar  # noqa: E402

DADOS = KIT / "dados"
LOG = AQUI / "log_juiz.csv"
RESPOSTAS = AQUI / "respostas"
STATUS = AQUI / "status_ultimo.json"
CAMPOS = ["hora", "acao", "agencia", "detalhe", "chave", "taxa", "saldo", "nota", "arquivo", "operador"]

TUTORIAL = "Bangkok"
PRECO = {"placar": 20, "completo": 50, "completo_pos_placar": 30}
COOLDOWN_TESTE_MIN = {"tutorial": 1, "pago": 5}
COOLDOWN_FINAL_MIN = 15
REENVIO_BASE = 80
LIMITE_REQ_MIN = 18  # margem sobre o limite de 20 req/min da equipe


def carregar_env() -> None:
    env = RAIZ / ".env"
    if not env.exists():
        return
    for linha in env.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def ler_log() -> list:
    if not LOG.exists():
        return []
    with LOG.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def anotar(**linha) -> None:
    novo = not LOG.exists()
    linha.setdefault("hora", datetime.now().isoformat(timespec="seconds"))
    linha.setdefault("operador", os.environ.get("OPERADOR", os.environ.get("USERNAME", "")))
    with LOG.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        w.writerow({k: linha.get(k, "") for k in CAMPOS})


def minutos_desde(hora: str) -> float:
    return (datetime.now() - datetime.fromisoformat(hora)).total_seconds() / 60


def respeitar_rate_limit() -> None:
    recentes = [r for r in ler_log() if minutos_desde(r["hora"]) < 1]
    if len(recentes) >= LIMITE_REQ_MIN:
        espera = 60 - (datetime.now() - datetime.fromisoformat(recentes[0]["hora"])).total_seconds()
        print(f"[rate limit] {len(recentes)} chamadas no último minuto; aguardando {espera:.0f} s")
        time.sleep(max(0, espera) + 1)


def chave(sub_norm: dict) -> str:
    return hashlib.sha1(json.dumps(sub_norm, sort_keys=True).encode()).hexdigest()[:10]


def preparar(ag: str, caminho: str):
    """Lê, valida e normaliza a submissão. Inválida encerra aqui, sem requisição."""
    sub = json.loads(Path(caminho).read_text(encoding="utf-8-sig"))
    if not isinstance(sub, dict):
        raise SystemExit("o arquivo deve ter UMA submissão (objeto JSON), não uma lista")
    sub.setdefault("agencia", ag)
    if sub["agencia"] != ag:
        raise SystemExit(f"agencia do corpo ({sub['agencia']}) diferente da rota ({ag})")
    cen = carregar(DADOS, ag)
    erros = validar.validar(sub, cen)
    if erros:
        print("Submissão inválida (nada foi enviado):")
        for e in erros:
            print(f"  - {e}")
        raise SystemExit(1)
    return sub, validar.normalizar(sub, cen)


def salvar(ag: str, acao: str, detalhe: str, k: str, sub: dict, resp) -> Path:
    pasta = RESPOSTAS / ag
    pasta.mkdir(parents=True, exist_ok=True)
    base = f"{datetime.now():%H%M%S}_{acao}_{detalhe or 'x'}_{k}"
    (pasta / f"{base}.sub.json").write_text(json.dumps(sub, ensure_ascii=False, indent=1), encoding="utf-8")
    arq = pasta / f"{base}.json"
    arq.write_text(json.dumps(resp, ensure_ascii=False, indent=1), encoding="utf-8")
    return arq


def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(RAIZ))
    except ValueError:
        return str(p)


def chamar(acao: str, ag: str, detalhe: str, k: str, f):
    respeitar_rate_limit()
    try:
        r = f()
    except ErroApi as e:
        anotar(acao=acao, agencia=ag, detalhe=detalhe, chave=k, nota=f"ERRO {e.status} {e.codigo}")
        extra = e.corpo if isinstance(e.corpo, dict) else {}
        if extra.get("retry_em"):
            print(f"tente de novo em: {extra['retry_em']}")
        if extra.get("erros") or extra.get("violacoes"):
            print(json.dumps({x: extra.get(x) for x in ("erros", "violacoes")}, ensure_ascii=False, indent=1))
        raise SystemExit(f"erro da API: {e}")
    return r


# ---------- comandos ----------

def cmd_status(c: Cliente, _a) -> None:
    r = chamar("status", "", "", "", c.status)
    anotar(acao="status", saldo=r.get("saldo", ""))
    STATUS.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    etapa = r.get("etapa") or {}
    print(f"fase: {r.get('fase')} · etapa: {etapa.get('rotulo', etapa)} · agora: {r.get('agora')} · saldo: {r.get('saldo')}")
    for ag in r.get("agencias", []):
        print(f"  agência: {json.dumps(ag, ensure_ascii=False)}")
    for carta in r.get("cartas", []):
        print(f"  carta: {json.dumps(carta, ensure_ascii=False)}")
    ev = r.get("eventos_ativos", [])
    print(f"  eventos_ativos: {len(ev)} (salvos em {rel(STATUS)}; use com simular.py --eventos)")
    for nome in liberadas_sem_kit(r):
        print(f"  ! {nome} liberada e sem kit local: py operacao/juiz.py kit {nome}")


def liberadas_sem_kit(status: dict) -> list:
    nomes = []
    for ag in status.get("agencias", []):
        nome = ag.get("id") or ag.get("agencia") or ag.get("nome") if isinstance(ag, dict) else ag
        if isinstance(nome, str) and not (DADOS / nome).is_dir():
            nomes.append(nome)
    return nomes


def baixar_kit(c: Cliente, ag: str) -> Path:
    """Como Cliente.baixar_kit, mas aceita o zip em base64 (o API Gateway devolve assim)."""
    import base64
    import io
    import zipfile
    bruto = c._req("GET", f"/agencias/{ag}/kit")
    if not bruto.startswith(b"PK"):
        bruto = base64.b64decode(bruto)
    DADOS.mkdir(parents=True, exist_ok=True)
    raiz = DADOS.resolve()
    with zipfile.ZipFile(io.BytesIO(bruto)) as z:
        for n in z.namelist():
            if not (raiz / n).resolve().is_relative_to(raiz):
                raise SystemExit(f"caminho suspeito no zip: {n}")
        z.extractall(DADOS)
    return DADOS / ag


def cmd_kit(c: Cliente, a) -> None:
    pasta = chamar("kit", a.agencia, "", "", lambda: baixar_kit(c, a.agencia))
    anotar(acao="kit", agencia=a.agencia, arquivo=rel(pasta))
    print(f"kit extraído em {rel(pasta)}")


def cmd_catalogo(c: Cliente, _a) -> None:
    cat = chamar("catalogo", "", "", "", c.catalogo)
    destino = DADOS / "catalogo.json"
    destino.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    anotar(acao="catalogo", arquivo=rel(destino))
    com_custo = all("custo" in x for x in cat.get("carregadores", []) + cat.get("entradas", []))
    print(f"catálogo salvo em {rel(destino)} · custos: {'sim' if com_custo else 'ainda não (pré-H4)'}"
          f" · pesos: {sorted(cat.get('pesos', {}))}")


def cmd_instrucoes(c: Cliente, _a) -> None:
    r = chamar("instrucoes", "", "", "", lambda: c._json("GET", "/instrucoes"))
    docs = RAIZ / "docs"
    docs.mkdir(exist_ok=True)
    for campo, nome in (("regulamento", "regulamento.md"), ("anexo_h4", "anexo_h4.md")):
        if r.get(campo):
            (docs / nome).write_text(r[campo], encoding="utf-8")
            print(f"{campo} salvo em docs/{nome}")
        else:
            print(f"{campo}: ainda não publicado")
    anotar(acao="instrucoes")


def cmd_teste(c: Cliente, a) -> None:
    ag, detalhe = a.agencia, "completo" if a.completo else "placar"
    sub, norm = preparar(ag, a.sub)
    k = chave(norm)
    feitos = [r for r in ler_log() if r["acao"] == "teste" and r["agencia"] == ag and r["chave"] == k
              and not r["nota"].startswith("ERRO")]
    serve = ("placar", "completo") if detalhe == "placar" else ("completo",)
    mesmo = [r for r in feitos if r["detalhe"] in serve]
    if mesmo and not a.forcar:
        arq = RAIZ / mesmo[-1]["arquivo"]
        print(f"teste idêntico já feito às {mesmo[-1]['hora']} (sem requisição): {rel(arq)}")
        print(arq.read_text(encoding="utf-8"))
        print("Se houve evento novo nesta agência, use --forcar.")
        return

    placar_pago = any(r["detalhe"] == "placar" for r in feitos)
    if ag == TUTORIAL:
        custo = 0
    elif detalhe == "completo":
        custo = PRECO["completo_pos_placar"] if placar_pago else PRECO["completo"]
    else:
        custo = PRECO["placar"]

    ampliacao = detalhe == "completo" and placar_pago
    if not ampliacao:
        cd = COOLDOWN_TESTE_MIN["tutorial" if ag == TUTORIAL else "pago"]
        ultimos = [r for r in ler_log() if r["acao"] == "teste" and r["agencia"] == ag
                   and not r["nota"].startswith("ERRO") and (ag == TUTORIAL or (r["taxa"] or "0") != "0")]
        if ultimos and minutos_desde(ultimos[-1]["hora"]) < cd:
            falta = cd - minutos_desde(ultimos[-1]["hora"])
            raise SystemExit(f"cooldown de {ag}: faltam {falta:.1f} min")

    if custo and not a.sim:
        print(f"Este teste ({detalhe}) em {ag} custa {custo} m7Coins. Confirme rodando de novo com --sim.")
        return

    r = chamar("teste", ag, detalhe, k, lambda: c.teste(ag, sub, detalhe))
    arq = salvar(ag, "teste", detalhe, k, sub, r)
    anotar(acao="teste", agencia=ag, detalhe=detalhe, chave=k, taxa=r.get("taxa", ""),
           saldo=r.get("saldo", ""), nota=r.get("nota", ""), arquivo=rel(arq))
    m = r.get("metricas", {})
    print(f"nota: {r.get('nota')} · taxa: {r.get('taxa')} · saldo: {r.get('saldo')} · válido: {r.get('valido')}")
    print(f"métricas: {json.dumps(m, ensure_ascii=False)}")
    if r.get("violacoes"):
        print(f"VIOLAÇÕES: {r['violacoes']}")
    print(f"resposta: {rel(arq)}")
    if detalhe == "completo":
        print(f"comparar: cd kit_kickoff/kit_kickoff && py comparar.py {arq.with_suffix('').with_suffix('.sub.json')} {arq}")


def cmd_final(c: Cliente, a) -> None:
    ag = a.agencia
    if ag == TUTORIAL:
        raise SystemExit("Bangkok não aceita envio final (não pontua)")
    sub, norm = preparar(ag, a.sub)
    k = chave(norm)
    finais = [r for r in ler_log() if r["acao"] == "final" and r["agencia"] == ag and not r["nota"].startswith("ERRO")]
    if finais and finais[-1]["chave"] == k:
        raise SystemExit("idêntico ao envio final vigente: o juiz recusaria (409)")
    if finais and minutos_desde(finais[-1]["hora"]) < COOLDOWN_FINAL_MIN:
        raise SystemExit(f"cooldown de envio final em {ag}: faltam "
                         f"{COOLDOWN_FINAL_MIN - minutos_desde(finais[-1]['hora']):.1f} min")
    custo = 0 if not finais else REENVIO_BASE * 2 ** (len(finais) - 1)
    if not a.sim:
        print(f"Envio final nº {len(finais) + 1} em {ag}: {custo} m7Coins. Substitui o vigente. "
              f"Confirme rodando de novo com --sim.")
        return
    r = chamar("final", ag, "", k, lambda: c._json("POST", f"/final/{ag}", sub))
    arq = salvar(ag, "final", "", k, sub, r)
    anotar(acao="final", agencia=ag, chave=k, taxa=r.get("taxa", ""), saldo=r.get("saldo", ""),
           nota=f"aceito={r.get('aceito')} n={r.get('n')}", arquivo=rel(arq))
    print(json.dumps(r, ensure_ascii=False, indent=1))


def cmd_gastos(_c, _a) -> None:
    log = ler_log()
    total, por_ag, finais = 0, {}, {}
    for r in log:
        t = float(r["taxa"] or 0)
        total += t
        if r["agencia"]:
            por_ag[r["agencia"]] = por_ag.get(r["agencia"], 0) + t
        if r["acao"] == "final" and not r["nota"].startswith("ERRO"):
            finais[r["agencia"]] = finais.get(r["agencia"], 0) + 1
    saldos = [r["saldo"] for r in log if r["saldo"]]
    print(f"gasto total: {total:.0f} m7Coins · último saldo informado: {saldos[-1] if saldos else '?'}")
    for ag in sorted(por_ag):
        print(f"  {ag:12s} gasto {por_ag[ag]:6.0f} · envios finais: {finais.get(ag, 0)}")
    print(f"chamadas registradas: {len(log)}")


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="py operacao/juiz.py")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status")
    sp.add_parser("catalogo")
    sp.add_parser("instrucoes")
    sp.add_parser("gastos")
    p = sp.add_parser("kit")
    p.add_argument("agencia")
    p = sp.add_parser("teste")
    p.add_argument("agencia")
    p.add_argument("sub")
    p.add_argument("--completo", action="store_true")
    p.add_argument("--sim", action="store_true", help="confirma o gasto de m7Coins")
    p.add_argument("--forcar", action="store_true", help="refaz teste idêntico (após evento)")
    p = sp.add_parser("final")
    p.add_argument("agencia")
    p.add_argument("sub")
    p.add_argument("--sim", action="store_true", help="confirma o envio")
    a = ap.parse_args(argv)

    if a.cmd == "gastos":
        return cmd_gastos(None, a)
    if a.cmd == "final" and a.agencia == TUTORIAL:
        raise SystemExit("Bangkok não aceita envio final (não pontua)")
    if a.cmd in ("teste", "final"):
        preparar(a.agencia, a.sub)  # inválida para aqui, mesmo sem credenciais
    carregar_env()
    c = Cliente()
    {"status": cmd_status, "kit": cmd_kit, "catalogo": cmd_catalogo, "instrucoes": cmd_instrucoes,
     "teste": cmd_teste, "final": cmd_final}[a.cmd](c, a)


if __name__ == "__main__":
    main()
