"""Apoio aos testes das etapas: monta um Motor sobre os dados de Bangkok e roda só os eventos agendados no teste."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kickoff import motor, tempo, validar  # noqa: E402
from kickoff.dados import carregar  # noqa: E402
from kickoff.modelo import Contrato  # noqa: E402

DADOS = RAIZ / "dados"
SEG = tempo.DIA  # segunda 18/10 00:00
CENARIO = carregar(DADOS, "Bangkok") if (DADOS / "Bangkok").is_dir() else None

MODELO = {
    "kwid": "Renault Kwid E-Tech", "jac": "JAC E-JS1", "geely": "Geely EX2 Pro", "mini": "BYD Dolphin Mini GS",
    "mg4": "MG4 Urban Comfort", "dolphin": "BYD Dolphin GS", "plus": "BYD Dolphin Plus", "leap": "Leapmotor B10 BEV",
}


def novo_motor(carregadores: dict, entrada="se_2000", t=SEG + 600, aberta=True, **politica) -> motor.Motor:
    """Motor sem agenda inicial (o teste agenda o que precisa). Padrão: sem limite prático (SE 2 MVA)."""
    sub = {"agencia": "Bangkok", "carregadores": carregadores, "entrada": entrada}
    if politica:
        sub["politica"] = politica
    m = motor.Motor(CENARIO, validar.normalizar(sub, CENARIO))
    m.t, m.aberta = t, aberta
    return m


def carro(m: motor.Motor, vid: str, apelido: str, soc: float) -> motor.Veiculo:
    mod = CENARIO.modelos[MODELO[apelido]]
    v = motor.Veiculo(vid, mod, mod.rank, soc)
    m.veiculos[vid] = v
    return v


def contrato(cid: str, categoria: str, retirada_t: int, km=None) -> Contrato:
    return Contrato(cid, categoria, CENARIO.categorias[categoria], retirada_t, None, 0.0, km)


def processar(m: motor.Motor, ate=float("inf"), ao_evento=None) -> None:
    """Roda os eventos da agenda até `ate` (mesmo despacho de Motor.rodar)."""
    import heapq
    while m.heap and m.heap[0][0] <= ate:
        t, _, _, tipo, p = heapq.heappop(m.heap)
        m.avancar(t)
        {"devolucao": lambda: m.on_devolucao(p[0], p[1], t),
         "abertura": lambda: m.on_abertura(t),
         "fechamento": lambda: m.on_fechamento(t),
         "ponta": lambda: m.on_ponta(p[0], t),
         "evento": lambda: m.on_evento(t, *p),
         "fim_recarga": lambda: m.on_fim_recarga(p[0], p[1], t),
         "retirada": lambda: m.on_retirada(p[0], t)}[tipo]()
        if ao_evento:
            ao_evento(t, tipo)


def ate_alvo(m: motor.Motor, v: motor.Veiculo):
    """Instante em que v chega ao alvo (80%), rodando a agenda."""
    chegou = []
    processar(m, ao_evento=lambda t, tipo: chegou.append(t) if not chegou and v.soc >= v.alvo - 1e-6 else None)
    return chegou[0] if chegou else None


def simular_bangkok(sub: dict):
    from kickoff import medicao
    s = validar.normalizar({"agencia": "Bangkok", **sub}, CENARIO)
    res = motor.simular(CENARIO, s)
    ini, fim = tempo.JANELA_PUBLICA
    return res, medicao.metricas(res.retiradas, res.nao_atendidos, res.bins, ini, fim)
