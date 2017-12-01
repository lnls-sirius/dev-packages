#!/usr/bin/env python-sirius

"""Unittest module for search.py."""

import unittest
from siriuspy import util
from siriuspy import search
from siriuspy.search import PSSearch
from siriuspy.search import MASearch


public_interface = (
    'PSSearch',
    'MASearch',
)


class TestSearch(unittest.TestCase):
    """Test Search module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(search, public_interface)
        self.assertTrue(valid)


class TestPSSearch(unittest.TestCase):
    """Test PSSearch."""

    public_interface = (
        'get_psnames',
        'get_splims',
        'get_pstype_dict',
        'get_pstype_names',
        'get_polarities',
        'get_pstype_2_names_dict',
        'conv_psname_2_pstype',
        'conv_pstype_2_polarity',
        'conv_pstype_2_magfunc',
        'conv_pstype_2_splims',
        'conv_psname_2_excdata',
        'conv_psname_2_ispulsed',
        'get_pstype_2_splims_dict',
        'get_splims_unit',
        'get_splims_labels',
    )

    sample = (
        'SI-Fam:PS-B1B2-1', 'SI-Fam:PS-QDA', 'SI-Fam:PS-SDB2',
        'SI-01C1:PS-CH', 'SI-02C3:PS-CV-2', 'SI-03M1:PS-QS',
        'SI-02M1:PS-FCV', 'BO-48D:PU-EjeK', 'SI-01SA:PU-HPing',
        'SI-01SA:PU-InjDpK', 'SI-01SA:PU-InjNLK', 'SI-19C4:PU-VPing',
        'TB-04:PU-InjS', 'TS-01:PU-EjeSF', 'TS-01:PU-EjeSG', 'TS-04:PU-InjSF',
        'TS-04:PU-InjSG-1', 'TS-04:PU-InjSG-2',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            PSSearch, TestPSSearch.public_interface)
        self.assertTrue(valid)

    def test_get_psnames(self):
        """Test get_psnames."""
        # raw
        psnames = PSSearch.get_psnames()
        self.assertIsInstance(psnames, (list, tuple))
        for psname in TestPSSearch.sample:
            self.assertIn(psname, psnames)
        # filtering
        psnames = PSSearch.get_psnames({'discipline': 'PU'})
        print(psnames)


class TestMASearch(unittest.TestCase):
    """Test MASearch."""

    public_interface = (
        None,
    )

    def _test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            search, TestMASearch.public_interface)
        self.assertTrue(valid)

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
