"""Etapa 4: limite da agência e `divisao` em duas camadas (5.3, 6.3.5, 6.3.7)."""
import unittest

from apoio import CENARIO, carro, novo_motor, simular_bangkok


@unittest.skipIf(CENARIO is None, "sem dados/Bangkok")
class Etapa4(unittest.TestCase):
    def _cenario_635(self, entrada, demanda=None, divisao="igual"):
        m = novo_motor({"dc_60x2": 2}, entrada=entrada, prioridade="menor_soc", divisao=divisao)
        if demanda is not None:
            m.limite_kw = m.limite_base_kw = demanda
        p1, p2 = m.pontos
        m.plugar(carro(m, "geely", "geely", 30.0), p1)
        m.plugar(carro(m, "dolphin", "dolphin", 50.0), p1)
        m.plugar(carro(m, "kwid", "kwid", 40.0), p2)
        m.plugar(carro(m, "jac", "jac", 75.0), p2)
        m.recalcular_potencias(m.t)
        return {v: m.veiculos[v].potencia_kw for v in ("geely", "dolphin", "kwid", "jac")}

    def test_635_igual_limite_40_5(self):
        kw = self._cenario_635("b3_45")
        for v in kw.values():
            self.assertAlmostEqual(v, 10.125, places=3)

    def test_635_prioridade_limite_40_5(self):
        kw = self._cenario_635("b3_45", divisao="prioridade")
        self.assertAlmostEqual(kw["kwid"], 26.6, places=3)
        self.assertAlmostEqual(kw["geely"], 13.9, places=3)
        self.assertEqual(kw["jac"], 0)
        self.assertEqual(kw["dolphin"], 0)

    def test_635_igual_limite_80(self):
        kw = self._cenario_635("a4_150", demanda=80)
        self.assertAlmostEqual(kw["jac"], 16.45, places=3)
        for v in ("geely", "dolphin", "kwid"):
            self.assertAlmostEqual(kw[v], 21.18333, places=3)

    def test_635_prioridade_limite_80(self):
        kw = self._cenario_635("a4_150", demanda=80, divisao="prioridade")
        self.assertAlmostEqual(kw["kwid"], 26.6, places=3)
        self.assertAlmostEqual(kw["geely"], 53.4, places=3)
        self.assertEqual(kw["dolphin"], 0)  # pegou 0 na camada 1 (Geely levou os 60 kW do carregador)
        self.assertEqual(kw["jac"], 0)

    def test_637_demanda_contratada_e_o_limite(self):
        m = novo_motor({"dc_60x2": 1}, entrada="a4_150")
        self.assertEqual(m.limite_kw, 130)  # omitida = teto da entrada
        from kickoff import validar
        sub = validar.normalizar({"agencia": "Bangkok", "carregadores": {"dc_60x2": 1}, "entrada": "a4_150",
                                  "demanda_contratada_kw": 84}, CENARIO)
        self.assertEqual(sub["demanda_contratada_kw"], 80)

    def test_pico_nunca_passa_do_limite_em_bangkok(self):
        for divisao in ("igual", "prioridade"):
            res, met = simular_bangkok({"carregadores": {"dc_60x2": 1, "ac_11": 2}, "entrada": "b3_45",
                                        "politica": {"divisao": divisao}})
            self.assertEqual(res.violacoes, [])
            self.assertLessEqual(met["pico_kw"], 40.5 + 1e-6)


if __name__ == "__main__":
    unittest.main()
