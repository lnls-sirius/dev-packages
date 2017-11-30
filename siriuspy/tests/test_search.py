#!/usr/bin/env python-sirius

"""Unittest module for search.py."""

import unittest
from siriuspy.search import MASearch


class TestMASearch(unittest.TestCase):
    """Test MASearch."""

    def test_manames_getsplim(self):
        """Test get_pwrsupply_manames and getsplim."""
        manames = MASearch.get_pwrsupply_manames()
        for maname in manames:
            lolo = MASearch.get_splim(maname, 'lolo')
            low = MASearch.get_splim(maname, 'low')
            high = MASearch.get_splim(maname, 'HIGH')
            hihi = MASearch.get_splim(maname, 'HIHI')

            self.assertGreaterEqual(hihi, high)
            self.assertGreater(high, lolo)
            self.assertGreaterEqual(low, lolo)


class TestMASearchMagFunc(unittest.TestCase):
    """MASearch class."""

    def setUp(self):
        """Setup method."""
        self.magnets = [
            dict(
                input='SI-Fam:MA-B1B2',
                output={
                    'SI-Fam:PS-B1B2-1': 'dipole',
                    'SI-Fam:PS-B1B2-2': 'dipole'
                }
            ),
            dict(
                input='SI-Fam:MA-Q1',
                output={
                    'SI-Fam:PS-Q1': 'quadrupole',
                }
            ),
            dict(
                input='SI-09M1:MA-QFA',
                output={
                    'SI-Fam:PS-QFA': 'quadrupole',
                    'SI-09M1:PS-QFA': 'quadrupole'
                }
            ),
            dict(
                input='SI-01M2:MA-SDA0',
                output={
                    'SI-Fam:PS-SDA0': 'sextupole',
                    'SI-01M2:PS-CH': 'corrector-horizontal',
                    'SI-01M2:PS-CV': 'corrector-vertical'
                }
            ),
            dict(
                input='SI-01C2:MA-FC',
                output={
                    'SI-01C2:PS-FCH': 'corrector-horizontal',
                    'SI-01C2:PS-FCV': 'corrector-vertical',
                    'SI-01C2:PS-QS': 'quadrupole-skew'
                }
            )
        ]

    def test_conv_name_2_func(self):
        """Test conv_name_2_func."""
        for magnet in self.magnets:
            for ps in magnet['output']:
                result = MASearch.conv_maname_2_magfunc(magnet['input'])
                self.assertEqual(magnet['output'], result)


class TestMASearchLimitLabels(unittest.TestCase):
    """TestMASearchLimitLabels class."""

    def test_ma_limit_labels(self):
        """Test limits and labels."""
        for maname, ma_labels in MASearch._maname_2_splims_dict.items():
            for label in MASearch._splims_labels:
                self.assertEqual(label in ma_labels, True)


class TestMASearchLoading(unittest.TestCase):
    """Test Loading methods."""

    def test_masearch_load_from_get_splim(self):
        """Test _maname_2_splims_dict."""
        MASearch.get_splim('SI-Fam:MA-QDA', 'lolo')
        self.assertEqual(MASearch._maname_2_splims_dict is not None, True)

    def test_masearch_load_from_get_splims_unit(self):
        """Test _splims_unit."""
        MASearch.get_splims_unit()
        self.assertEqual(MASearch._splims_unit is not None, True)

    def test_masearch_load_from_conv_maname_2_magfunc(self):
        """Test _maname_2_psnames_dict."""
        MASearch.conv_maname_2_magfunc('SI-Fam:MA-QDA')
        self.assertEqual(MASearch._maname_2_psnames_dict is not None, True)


if __name__ == "__main__":
    unittest.main()
