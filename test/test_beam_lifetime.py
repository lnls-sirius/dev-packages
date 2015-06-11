
import unittest
import mathphys.beam_lifetime as beam_lifetime


class TestLossRates(unittest.TestCase):

    def test_calc_quantum_loss_rates(self):
        expected_results = (
            0.163746150615596,
            0.239642114195851,
            0.147082817097433
        )
        results = beam_lifetime.calc_quantum_loss_rates(
            natural_emittance=1.5,
            coupling=0.2,
            energy_spread=1.0,
            transverse_acceptances=[0.5, 0.4],
            energy_acceptance=0.5,
            radiation_damping_times=[2.0, 3.0, 1.5]
        )
        self.assertEqual(len(results), 3)
        for i in range(len(expected_results)):
            self.assertAlmostEqual(results[i], expected_results[i], 15)

    def test_calc_quantum_loss_rates_transverse(self):
        alpha_x, alpha_y = beam_lifetime.calc_quantum_loss_rates_transverse(
            natural_emittance=1.5,
            coupling=0.2,
            acceptances=[0.5, 0.4],
            radiation_damping_times=[2.0, 3.0]
        )
        self.assertAlmostEqual(alpha_x, 0.163746150615596, 15)
        self.assertAlmostEqual(alpha_y, 0.239642114195851, 15)

    def test_calc_quantum_loss_rate_longitudinal(self):
        alpha_s = beam_lifetime.calc_quantum_loss_rate_longitudinal(
            energy_spread=1.0,
            energy_acceptance=0.5,
            radiation_damping_time=1.5
        )
        self.assertAlmostEqual(alpha_s, 0.147082817097433, 15)


def loss_rates_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLossRates)
    return suite


def get_suite():
    suite_list = []
    suite_list.append(loss_rates_suite())
    return unittest.TestSuite(suite_list)
