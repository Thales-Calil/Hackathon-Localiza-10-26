"""Etapa 6: as três `prioridade` (6.3.3)."""
import unittest

from apoio import CENARIO, SEG, carro, contrato, novo_motor, simular_bangkok

H = 60


@unittest.skipIf(CENARIO is None, "sem dados/Bangkok")
class Etapa6(unittest.TestCase):
    def _fila_633(self, prioridade):
        m = novo_motor({"ac_7": 1}, t=SEG + 11 * H, prioridade=prioridade)
        m.contratos = {c.id: c for c in (contrato("ouro", "Ouro", SEG + 12 * H + 30),
                                         contrato("prata", "Prata", SEG + 13 * H + 15),
                                         contrato("bronze", "Bronze", SEG + 14 * H))}
        for vid, ap, soc, entrou in (("A", "kwid", 30.0, 10 * H), ("B", "mini", 20.0, 10 * H + 20),
                                     ("C", "mg4", 55.0, 10 * H + 40), ("D", "leap", 40.0, 10 * H + 55)):
            v = carro(m, vid, ap, soc)
            v.na_fila, v.entrou_fila_t = True, SEG + entrou
            m.fila.append(v)
        m.fila.reverse()
        m.ordenar_fila(m.t)
        return [v.id for v in m.fila]

    def test_633_menor_soc_em_km(self):
        self.assertEqual(self._fila_633("menor_soc"), ["A", "B", "D", "C"])

    def test_633_chegada(self):
        self.assertEqual(self._fila_633("chegada"), ["A", "B", "C", "D"])

    def test_633_proxima_retirada(self):
        self.assertEqual(self._fila_633("proxima_retirada"), ["C", "D", "B", "A"])

    def test_bangkok_tres_prioridades_sem_violacoes(self):
        for p in ("menor_soc", "chegada", "proxima_retirada"):
            res, _ = simular_bangkok({"carregadores": {"ac_7": 2, "dc_30": 1}, "entrada": "b3_45",
                                      "politica": {"prioridade": p, "divisao": "prioridade"}})
            self.assertEqual(res.violacoes, [], p)


if __name__ == "__main__":
    unittest.main()
