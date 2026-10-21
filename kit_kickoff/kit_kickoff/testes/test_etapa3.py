"""Etapa 3: fila, plug, curva em degraus e fim de recarga (5.2, 5.3, 6.3.2, 6.3.4)."""
import unittest

from apoio import CENARIO, SEG, ate_alvo, carro, novo_motor, processar, simular_bangkok


@unittest.skipIf(CENARIO is None, "sem dados/Bangkok")
class Etapa3(unittest.TestCase):
    def test_632_dolphin_gs_20_a_80_no_dc60_em_36_7_min(self):
        m = novo_motor({"dc_60x2": 1})
        v = carro(m, "V1", "dolphin", 20.0)
        m.entrar_patio(v, m.t)
        self.assertTrue(v.plugado)
        t = ate_alvo(m, v)
        self.assertAlmostEqual(t - (SEG + 600), 36.7, delta=0.05)
        self.assertFalse(v.plugado)  # aberta: desplugado ao chegar a 80%
        self.assertAlmostEqual(v.soc, 80.0)

    def test_634_escolhe_o_dc60(self):
        m = novo_motor({"ac_22x2": 1, "dc_60x2": 1})
        dc = next(p for p in m.pontos if p.modelo.id == "dc_60x2")
        ac = next(p for p in m.pontos if p.modelo.id == "ac_22x2")
        m.plugar(carro(m, "geely", "geely", 30.0), dc)
        self.assertIs(m.escolher_ponto(carro(m, "dolphin", "dolphin", 20.0)), dc)  # 30 kW contra 7
        m.plugar(m.veiculos["dolphin"], dc)
        self.assertIs(m.escolher_ponto(carro(m, "outro", "dolphin", 20.0)), ac)  # DC-60 cheio

    def test_plugados_nunca_passam_das_saidas(self):
        m = novo_motor({"ac_7": 1, "dc_30": 1})
        for i in range(4):
            m.entrar_patio(carro(m, f"V{i}", "kwid", 10.0 + i), m.t)
        self.assertEqual(sum(len(p.conectados) for p in m.pontos), 2)
        self.assertEqual(len(m.fila), 2)

    def test_fila_anda_quando_termina_a_recarga(self):
        m = novo_motor({"dc_30": 1})
        a, b = carro(m, "A", "kwid", 70.0), carro(m, "B", "kwid", 50.0)
        m.entrar_patio(a, m.t)
        m.entrar_patio(b, m.t)
        self.assertTrue(a.plugado and b.na_fila)
        processar(m, ate=m.t + 10)
        self.assertTrue(b.plugado)
        self.assertFalse(a.plugado)

    def test_fechada_nao_pluga(self):
        m = novo_motor({"dc_30": 1}, aberta=False)
        v = carro(m, "V1", "kwid", 20.0)
        m.entrar_patio(v, m.t)
        self.assertTrue(v.na_fila and not v.plugado)

    def test_bangkok_exemplo_sem_violacoes(self):
        res, met = simular_bangkok({"carregadores": {"ac_7": 2, "dc_30": 1}, "entrada": "b3_45"})
        self.assertEqual(res.violacoes, [])
        self.assertGreater(met["certos"] + met["upgrades"], 22)
        self.assertLessEqual(max(x[1] for x in res.trace), 3)
        for r in res.retiradas:
            self.assertGreaterEqual(r.soc, 80 - 1e-6)


if __name__ == "__main__":
    unittest.main()
