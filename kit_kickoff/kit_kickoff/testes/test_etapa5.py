"""Etapa 5: horário de funcionamento e `evitar_ponta` (5.2, 5.3, 6.3.6)."""
import unittest

from apoio import CENARIO, SEG, ate_alvo, carro, motor, novo_motor, processar, simular_bangkok

H = 60


@unittest.skipIf(CENARIO is None, "sem dados/Bangkok")
class Etapa5(unittest.TestCase):
    def _mg4_636(self, evitar):
        """MG4 (43 kWh) pluga segunda 17:00 num AC-22, de 29% a 80%. Bangkok fecha às 18:00."""
        m = novo_motor({"ac_22x2": 1}, t=SEG + 17 * H, evitar_ponta=evitar)
        m.agendar(SEG + 18 * H, motor.PRIO_FECHAMENTO, "fechamento")
        m.agendar(SEG + 24 * H + 8 * H, motor.PRIO_ABERTURA, "abertura")
        if evitar:
            m.agendar(SEG + 18 * H, motor.PRIO_ABERTURA, "ponta", True)
            m.agendar(SEG + 21 * H, motor.PRIO_ABERTURA, "ponta", False)
        v = carro(m, "mg4", "mg4", 29.0)
        m.entrar_patio(v, m.t)
        self.assertAlmostEqual(v.potencia_kw, 11.0)
        return m, v

    def test_636_sem_evitar_ponta_termina_19h(self):
        m, v = self._mg4_636(False)
        self.assertAlmostEqual(ate_alvo(m, v), SEG + 19 * H, delta=1)

    def test_636_com_evitar_ponta_termina_22h(self):
        m, v = self._mg4_636(True)
        processar(m, ate=SEG + 20 * H)
        self.assertTrue(v.plugado)  # parado na ponta, mas plugado
        self.assertEqual(v.potencia_kw, 0)
        self.assertAlmostEqual(ate_alvo(m, v), SEG + 22 * H, delta=1)

    def test_fechada_segura_a_saida_ate_abrir(self):
        m, v = self._mg4_636(False)
        processar(m, ate=SEG + 23 * H)
        self.assertTrue(v.plugado)  # chegou a 80% com a agência fechada
        self.assertGreaterEqual(v.soc, 80 - 1e-6)
        processar(m)  # abertura de terça 08:00
        self.assertFalse(v.plugado)

    def test_bangkok_evitar_ponta_zera_energia_na_ponta(self):
        sub = {"carregadores": {"ac_7": 2, "dc_30": 1}, "entrada": "b3_45"}
        _, sem = simular_bangkok(sub)
        res, com = simular_bangkok({**sub, "politica": {"evitar_ponta": True}})
        self.assertGreater(sem["energia_ponta_kwh"], 0)
        self.assertAlmostEqual(com["energia_ponta_kwh"], 0, places=6)
        self.assertEqual(res.violacoes, [])


if __name__ == "__main__":
    unittest.main()
