"""Etapa 2: devolução em km (4.1), escolha do carro (5.1, 6.3.1), retirada sem recarga."""
import unittest

from apoio import CENARIO, SEG, carro, contrato, motor, novo_motor, simular_bangkok, tempo


@unittest.skipIf(CENARIO is None, "sem dados/Bangkok")
class Etapa2(unittest.TestCase):
    def test_soc_devolucao_pela_autonomia_do_modelo(self):
        m = novo_motor({"ac_7": 1})
        c = contrato("C1", "Ouro", SEG + 480, km=162.0)
        self.assertAlmostEqual(m.soc_devolucao(carro(m, "V1", "dolphin", 80.0), c), 162 / 291 * 100)
        # num Kwid 162 km seriam 87,6%: o teto é o SOC de saída
        self.assertEqual(m.soc_devolucao(carro(m, "V2", "kwid", 80.0), c), 80.0)

    def _patio_631(self, soc_geely):
        m = novo_motor({"ac_7": 1})
        for vid, ap, soc in (("geely", "geely", soc_geely), ("mini", "mini", 95.0), ("mg4", "mg4", 100.0),
                             ("jac", "jac", 100.0)):
            m.patio[vid] = carro(m, vid, ap, soc)
        m.patio["mini"].plugado = True
        return m

    def test_631_sai_o_geely(self):
        m = self._patio_631(82.0)
        self.assertEqual(m.escolher_carro(contrato("C1", "Prata", SEG + 600), SEG + 600).id, "geely")

    def test_631_geely_78_sai_o_dolphin_mini(self):
        m = self._patio_631(78.0)
        self.assertEqual(m.escolher_carro(contrato("C1", "Prata", SEG + 600), SEG + 600).id, "mini")

    def test_631_sem_prata_apto_sai_o_mg4_upgrade(self):
        m = self._patio_631(78.0)
        del m.patio["mini"]
        self.assertEqual(m.escolher_carro(contrato("C1", "Prata", SEG + 600), SEG + 600).id, "mg4")

    def test_downgrade_nunca(self):
        m = novo_motor({"ac_7": 1})
        m.patio["jac"] = carro(m, "jac", "jac", 100.0)
        self.assertIsNone(m.escolher_carro(contrato("C1", "Prata", SEG + 600), SEG + 600))

    def test_empate_em_80_vai_pelo_menor_id(self):
        m = novo_motor({"ac_7": 1})
        for vid in ("V9", "V1", "V5"):
            m.patio[vid] = carro(m, vid, "dolphin", 80.0)
        self.assertEqual(m.escolher_carro(contrato("C1", "Ouro", SEG + 600), SEG + 600).id, "V1")

    def test_devolucao_abaixo_de_80_entra_na_fila(self):
        m = novo_motor({"ac_7": 1}, aberta=False)
        v = carro(m, "V1", "kwid", 40.0)
        m.on_devolucao("V1", 40.0, SEG + 600)
        self.assertTrue(v.na_fila)
        self.assertEqual(v.entrou_fila_t, SEG + 600)

    def test_bangkok_sem_recarga_atende_so_o_estoque(self):
        """Referência: sem plugar ninguém, só os 22 carros do estoque (todos a 80%) atendem."""
        class SemRecarga(motor.Motor):
            def plugar_fila(self, t):
                pass

        original = motor.Motor
        motor.Motor = SemRecarga
        try:
            res, met = simular_bangkok({"carregadores": {"ac_7": 1}, "entrada": "b3_45"})
        finally:
            motor.Motor = original
        self.assertEqual(met["certos"] + met["upgrades"], 22)
        for r in res.retiradas:
            self.assertGreaterEqual(r.soc, 80 - 1e-6)
            self.assertGreaterEqual(r.rank_entregue, r.rank_pedido)


if __name__ == "__main__":
    unittest.main()
