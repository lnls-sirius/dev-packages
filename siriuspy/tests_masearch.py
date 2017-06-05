#!/usr/local/bin/python3.6
import unittest
from siriuspy.search import MASearch

class TestMASearcg(unittest.TestCase):
    def test_getsplim(self):
        lolo = MASearch.get_splim('SI-Fam:MA-QDA', 'lolo')
        high = MASearch.get_splim('SI-Fam:MA-QDA', 'HIGH')
        hihi = MASearch.get_splim('SI-Fam:MA-QDA', 'HIHI')

        self.assertEqual(lolo, 0.0)
        self.assertEqual(high, 125.0)
        self.assertEqual(hihi, 125.0)


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

if __name__ == "__main__":
    unittest.main()
