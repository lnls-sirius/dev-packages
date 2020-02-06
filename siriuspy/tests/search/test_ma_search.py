"""Unittest module for ma_search.py."""

from unittest import TestCase

from siriuspy import util
from siriuspy.search import ma_search
from siriuspy.search import MASearch


class TestModule(TestCase):
    """Test Search module."""

    public_interface = (
        'MASearch',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                                ma_search, TestModule.public_interface)
        self.assertTrue(valid)


class TestMASearch(TestCase):
    """Test MASearch."""

    public_interface = (
        'get_manames',
        'get_pwrsupply_manames',
        'get_mapositions',
        'get_manicknames',
        'conv_maname_2_trims',
        'conv_maname_2_magfunc',
        'conv_maname_2_psnames',
        'conv_psmaname_2_psnames',
        'conv_bbbname_2_psmanames',
        'conv_psname_2_psmaname',
    )

    maname2trims = {
        "SI-Fam:MA-B1B2": None,
        "SI-Fam:MA-QDA": ('SI-01M1:PS-QDA', 'SI-01M2:PS-QDA', 'SI-05M1:PS-QDA',
                          'SI-05M2:PS-QDA', 'SI-09M1:PS-QDA', 'SI-09M2:PS-QDA',
                          'SI-13M1:PS-QDA', 'SI-13M2:PS-QDA', 'SI-17M1:PS-QDA',
                          'SI-17M2:PS-QDA'),
        "SI-14M2:MA-QDB1": None,
        "SI-09M2:MA-SDA0": None,
        "SI-07C4:MA-CH": None,
        "BO-15U:MA-CV": None,
        "TB-03:MA-QF3": None,
        "TS-01:MA-CV-2": None,
        "BO-01D:PM-InjKckr": None,
        "TB-04:PM-InjSept": None,
        "SI-01SA:PM-InjNLKckr": None,
    }

    maname2magfuncs = {
        'SI-Fam:MA-B1B2': {'SI-Fam:PS-B1B2-1': 'dipole',
                           'SI-Fam:PS-B1B2-2': 'dipole'},
        'SI-Fam:MA-QDA': {'SI-Fam:PS-QDA': 'quadrupole'},
        'SI-14M2:MA-QDB1': {'SI-14M2:PS-QDB1': 'quadrupole',
                            'SI-Fam:PS-QDB1': 'quadrupole'},
        'SI-09M2:MA-SDA0': {'SI-09M2:PS-CH': 'corrector-horizontal',
                            'SI-09M2:PS-CV': 'corrector-vertical',
                            'SI-Fam:PS-SDA0': 'sextupole'},
        'SI-07C4:MA-CH': {'SI-07C4:PS-CH': 'corrector-horizontal'},
        'BO-15U:MA-CV': {'BO-15U:PS-CV': 'corrector-vertical'},
        'TB-03:MA-QF3': {'TB-03:PS-QF3': 'quadrupole'},
        'TS-01:MA-CV-2': {'TS-01:PS-CV-2': 'corrector-vertical'},
        'BO-01D:PM-InjKckr': {'BO-01D:PU-InjKckr': 'corrector-horizontal'},
        'TB-04:PM-InjSept': {'TB-04:PU-InjSept': 'corrector-horizontal'},
        'SI-01SA:PM-InjNLKckr':
            {'SI-01SA:PU-InjNLKckr': 'corrector-horizontal'},
    }

    maname2psnames = {
        'SI-Fam:MA-B1B2': ('SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2'),
        'SI-Fam:MA-QDA': ('SI-Fam:PS-QDA',),
        'SI-14M2:MA-QDB1': ('SI-Fam:PS-QDB1', 'SI-14M2:PS-QDB1'),
        'SI-09M2:MA-SDA0': ('SI-Fam:PS-SDA0', 'SI-09M2:PS-CH',
                            'SI-09M2:PS-CV'),
        'SI-07C4:MA-CH': ('SI-07C4:PS-CH',),
        'BO-15U:MA-CV': ('BO-15U:PS-CV',),
        'TB-03:MA-QF3': ('TB-03:PS-QF3',),
        'TS-01:MA-CV-2': ('TS-01:PS-CV-2',),
        'BO-01D:PM-InjKckr': ('BO-01D:PU-InjKckr',),
        'TB-04:PM-InjSept': ('TB-04:PU-InjSept',),
        'SI-01SA:PM-InjNLKckr': ('SI-01SA:PU-InjNLKckr',),
    }

    psname2maname = {
        'SI-Fam:PS-B1B2-1': 'SI-Fam:MA-B1B2',
        'SI-Fam:PS-B1B2-2': 'SI-Fam:MA-B1B2',
        'BO-Fam:PS-B-1': 'BO-Fam:MA-B',
        'BO-Fam:PS-B-2': 'BO-Fam:MA-B',
        'SI-01M1:PS-CH': 'SI-01M1:MA-SDA0',
    }

    psname2psmaname = {
        'SI-Fam:PS-B1B2-1': 'SI-Fam:MA-B1B2',
        'SI-Fam:PS-B1B2-2': 'SI-Fam:MA-B1B2',
        'BO-Fam:PS-B-1': 'BO-Fam:MA-B',
        'BO-Fam:PS-B-1': 'BO-Fam:MA-B',
        'SI-Fam:PS-QDA': 'SI-Fam:MA-QDA',
        'SI-Fam:PS-SDA0': 'SI-Fam:MA-SDA0',
        'SI-01M1:PS-QDA': 'SI-01M1:MA-QDA',
        'SI-01M2:PS-CH': 'SI-01M2:MA-CH',
    }

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            MASearch, TestMASearch.public_interface)
        self.assertTrue(valid)

    def test_get_manames(self):
        """Test get_manames."""
        manames = MASearch.get_manames()
        self.assertIsInstance(manames, (list, tuple))
        for maname in TestMASearch.maname2trims:
            self.assertIn(maname, manames)
        # check sorted
        # sorted_manames = sorted(manames)
        # self.assertEqual(manames, sorted_manames)
        # with filters
        manames = MASearch.get_manames({'dis': 'PM'})
        self.assertEqual(len(manames), 12)
        for name in manames:
            self.assertIn('PM', name)
        manames = MASearch.get_manames({'sub': '0.M1'})
        self.assertEqual(len(manames), 84)

    def test_conv_maname_2_trims(self):
        """Test conv_maname_2_trims."""
        for ma, trims in TestMASearch.maname2trims.items():
            self.assertEqual(MASearch.conv_maname_2_trims(ma), trims)

    def test_conv_maname_2_magfunc(self):
        """Test conv_maname_2_magfunc."""
        for ma, magfuncs in TestMASearch.maname2magfuncs.items():
            self.assertEqual(MASearch.conv_maname_2_magfunc(ma), magfuncs)

    def test_conv_maname_2_psnames(self):
        """Test conv_maname_2_psnames."""
        for ma, psnames in TestMASearch.maname2psnames.items():
            self.assertEqual(MASearch.conv_maname_2_psnames(ma), psnames)

    # def test_psname_2_maname(self):
    #     """Test psname_2_maname."""
    #     for psname, maname in TestMASearch.psname2maname.items():
    #         self.assertEqual(MASearch.conv_psname_2_maname(psname), maname)

    def test_conv_psname_2_psmaname(self):
        """Test conv_psname_2_psmaname."""
        self.assertIs(MASearch.conv_psname_2_psmaname('INV'), None)
        for psname, maname in TestMASearch.psname2psmaname.items():
            self.assertEqual(MASearch.conv_psname_2_psmaname(psname),
                             maname)

    def test_conv_bbbname_2_psmanames(self):
        """Test conv_bbbname_2_psmanames."""
        self.assertRaises(KeyError, MASearch.conv_bbbname_2_psmanames, '')
