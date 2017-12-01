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

    sample = {
        'SI-Fam:PS-B1B2-1': 'si-dipole-b1b2-fam',
        'SI-Fam:PS-QDA': 'si-quadrupole-q14-fam',
        'SI-Fam:PS-SDB2': 'si-sextupole-s15-sd-fam',
        'SI-01C1:PS-CH': 'si-sextupole-s15-ch',
        'SI-02C3:PS-CV-2': 'si-sextupole-s15-cv',
        'SI-03M1:PS-QS': 'si-sextupole-s15-qs',
        'SI-02M1:PS-FCV': 'si-corrector-fcv',
        'BO-48D:PU-EjeK': 'bo-ejekicker',
        'SI-01SA:PU-HPing': 'si-hping',
        'SI-01SA:PU-InjDpK': 'si-injdpk',
        'SI-01SA:PU-InjNLK': 'si-injnlk',
        'SI-19C4:PU-VPing': 'si-vping',
        'TB-04:PU-InjS': 'tb-injseptum',
        'TS-01:PU-EjeSF': 'ts-ejeseptum-thin',
        'TS-01:PU-EjeSG': 'ts-ejeseptum-thick',
        'TS-04:PU-InjSF': 'ts-injseptum-thin',
        'TS-04:PU-InjSG-1': 'ts-injseptum-thick',
        'TS-04:PU-InjSG-2': 'ts-injseptum-thick',
    }

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            PSSearch, TestPSSearch.public_interface)
        self.assertTrue(valid)

    def test_get_psnames(self):
        """Test get_psnames."""
        # without filters
        psnames = PSSearch.get_psnames()
        self.assertIsInstance(psnames, (list, tuple))
        for psname in TestPSSearch.sample:
            self.assertIn(psname, psnames)
        # check sorted
        sorted_psnames = sorted(psnames)
        self.assertEqual(psnames, sorted_psnames)
        # with filters
        psnames = PSSearch.get_psnames({'discipline': 'PU'})
        self.assertEqual(len(psnames), 12)
        for name in psnames:
            self.assertIn('PU', name)
        psnames = PSSearch.get_psnames({'sub_section': '0.M1'})
        self.assertEqual(len(psnames), 69)
        # exceptions
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=23)
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=23.4)
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=[0, ])
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=(0.0, ))

    def test_get_pstype_names(self):
        """Test get_pstype_names."""
        pstypes = PSSearch.get_pstype_names()
        self.assertIsInstance(pstypes, list)
        for pstype in pstypes:
            self.assertIsInstance(pstype, str)

    def test_get_splims(self):
        """Test get_splims."""
        l1 = PSSearch.get_splims(
             pstype='si-quadrupole-q30-trim', label='lolo')
        l2 = PSSearch.get_splims(
             pstype='si-quadrupole-q30-trim', label='hihi')
        self.assertGreater(l2, l1)
        # exceptions
        self.assertRaises(
            KeyError, PSSearch.get_splims,
            pstype='dummy', label='low')
        self.assertRaises(
            KeyError, PSSearch.get_splims,
            pstype='bo-corrector-ch', label='dummy')

    def test_get_pstype_dict(self):
        """Test get_pstype_dict."""
        d = PSSearch.get_pstype_dict()
        self.assertIsInstance(d, dict)
        pstypes_d = sorted(list(d.keys()))
        pstypes = sorted(PSSearch.get_pstype_names())
        self.assertEqual(pstypes_d, pstypes)

    def test_get_polarities(self):
        """Test get_polarities."""
        polarities = PSSearch.get_polarities()
        self.assertIsInstance(polarities, list)
        for p in polarities:
            self.assertIsInstance(p, str)
        self.assertIn('bipolar', polarities)
        self.assertIn('monopolar', polarities)

    def test_conv_psname_2_pstype(self):
        """Test conv_psname_2_pstype."""
        for psname, pstype in TestPSSearch.sample.items():
            self.assertEqual(PSSearch.conv_psname_2_pstype(psname), pstype)
        # exceptions
        self.assertRaises(
            KeyError, PSSearch.conv_psname_2_pstype, psname='dummy')


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

    def test_manames_get_splims(self):
        """Test get_pwrsupply_manames and get_splims."""
        manames = MASearch.get_pwrsupply_manames()
        for maname in manames:
            lolo = MASearch.get_splims(maname, 'lolo')
            low = MASearch.get_splims(maname, 'low')
            high = MASearch.get_splims(maname, 'HIGH')
            hihi = MASearch.get_splims(maname, 'HIHI')

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

    def test_masearch_load_from_get_splims(self):
        """Test _maname_2_splims_dict."""
        MASearch.get_splims('SI-Fam:MA-QDA', 'lolo')
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
