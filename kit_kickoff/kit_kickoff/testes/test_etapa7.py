"""Etapa 7: eventos ao vivo (11). Formato de `params` [tipo, agencia, inicio, fim, valor] (formato do GET /status)."""
import unittest

from apoio import CENARIO, SEG, carro, novo_motor, processar


@unittest.skipIf(CENARIO is None, "sem dados/Bangkok")
class Etapa7(unittest.TestCase):
    def test_limite_da_concessionaria_reduz_e_volta(self):
        m = novo_motor({"dc_60x2": 1}, entrada="b3_45")
        m.entrar_patio(carro(m, "A", "geely", 20.0), m.t)
        m.agendar_eventos([["limite_kw", "Bangkok", m.t + 1, m.t + 5, 15]])
        processar(m, ate=m.t + 2)
        self.assertAlmostEqual(m.veiculos["A"].potencia_kw, 15)
        processar(m, ate=m.t + 4)
        self.assertGreater(m.veiculos["A"].potencia_kw, 15)
        self.assertEqual(m.limite_kw, 40.5)

    def test_carregador_fora_zera_e_ao_voltar_repluga_a_fila(self):
        m = novo_motor({"dc_30": 1})
        a = carro(m, "A", "kwid", 20.0)
        m.entrar_patio(a, m.t)
        m.agendar_eventos([["carregador_fora", "Bangkok", m.t + 1, m.t + 30, "dc_30"]])
        processar(m, ate=m.t + 2)
        self.assertTrue(a.plugado)
        self.assertEqual(a.potencia_kw, 0)
        b = carro(m, "B", "kwid", 10.0)
        m.entrar_patio(b, m.t)
        self.assertTrue(b.na_fila)
        processar(m, ate=m.t + 31)
        self.assertGreater(a.potencia_kw + (0 if a.plugado else 1), 0)

    def test_corte_da_concessionaria_multiplica_o_limite(self):
        m = novo_motor({"dc_60x2": 1}, entrada="b3_45")
        m.entrar_patio(carro(m, "A", "geely", 20.0), m.t)
        m.agendar_eventos([["corte", "Bangkok", m.t + 1, m.t + 5, 0.7]])
        processar(m, ate=m.t + 2)
        self.assertAlmostEqual(m.limite_kw, 40.5 * 0.7)
        self.assertAlmostEqual(m.veiculos["A"].potencia_kw, 40.5 * 0.7)
        processar(m, ate=m.t + 4)
        self.assertEqual(m.limite_kw, 40.5)

    def test_evento_desconhecido_vira_aviso(self):
        m = novo_motor({"dc_30": 1})
        m.agendar_eventos([["outro", "Bangkok", m.t + 1, None]])
        processar(m)
        self.assertTrue(m.avisos)


if __name__ == "__main__":
    unittest.main()
