#!/usr/local/bin/python3.6
import unittest
from siriuspy.search import MASearch

class TestMASearch(unittest.TestCase):
    def test_getsplim(self):
        lolo = MASearch.get_splim('SI-Fam:MA-QDA', 'lolo')
        high = MASearch.get_splim('SI-Fam:MA-QDA', 'HIGH')
        hihi = MASearch.get_splim('SI-Fam:MA-QDA', 'HIHI')

        self.assertEqual(lolo, 0.0)
        self.assertEqual(high, 125.0)
        self.assertEqual(hihi, 125.0)

class TestMASearchMagFunc(unittest.TestCase):
    def setUp(self):
        self.magnets = [
            dict(
                input='SI-Fam:MA-B1B2',
                output= {
                    'SI-Fam:PS-B1B2-1': 'dipole',
                    'SI-Fam:PS-B1B2-2': 'dipole'
                }
            ),
            dict(
                input='SI-Fam:MA-Q1',
                output= {
                    'SI-Fam:PS-Q1':'quadrupole',
                }
            ),
            dict(
                input='SI-09M1:MA-QFA',
                output= {
                    'SI-Fam:PS-QFA': 'quadrupole',
                    'SI-09M1:PS-QFA': 'quadrupole'
                }
            ),
            dict(
                input='SI-01M2:MA-SDA0',
                output= {
                    'SI-Fam:PS-SDA0': 'sextupole',
                    'SI-01M2:PS-CH': 'corrector',
                    'SI-01M2:PS-CV': 'corrector'
                }
            ),
            dict(
                input='SI-01C2:MA-FC',
                output= {
                    'SI-01C2:PS-FCH': 'corrector',
                    'SI-01C2:PS-FCV': 'corrector',
                    'SI-01C2:PS-QS': 'quadrupole-skew'
                }
            )
        ]

    def test_conv_name_2_func(self):
        for magnet in self.magnets:
            for ps in magnet['output']:
                result = MASearch.conv_maname_2_magfunc(magnet['input'])
                self.assertEqual(magnet['output'], result)

class TestMASearchLimitLabels(unittest.TestCase):
    def setUp(self):
        MASearch.reload_maname_2_splims_dict()

    def test_ma_limit_labels(self):
        for maname, ma_labels in MASearch._maname_2_splims_dict.items():
            for label in MASearch._splims_labels:
                self.assertEqual(label in ma_labels, True)

class TestMASearchLoading(unittest.TestCase):
    def test_masearch_load_from_get_splim(self):
        sp_lim = MASearch.get_splim('SI-Fam:MA-QDA', 'lolo')
        self.assertEqual(MASearch._maname_2_splims_dict is not None, True)

    def test_masearch_load_from_get_splims_unit(self):
        MASearch.get_splims_unit()
        self.assertEqual(MASearch._splims_unit is not None, True)

    def test_masearch_load_from_conv_maname_2_magfunc(self):
        mag_func = MASearch.conv_maname_2_magfunc('SI-Fam:MA-QDA')
        self.assertEqual(MASearch._maname_2_psnames_dict is not None, True)


if __name__ == "__main__":
    unittest.main()
