#!/usr/bin/env python-sirius

"""Unittest module for search.py."""

import unittest
from unittest import mock

from siriuspy import util
from siriuspy import search
from siriuspy.search import PSSearch
from siriuspy.search import MASearch
from siriuspy.magnet.excdata import ExcitationData


public_interface = (
    'PSSearch',
    'MASearch',
)


def read_test_file(path):
    """Read a file."""
    with open('test_data/' + path, "r") as fd:
        return fd.read()


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

    pstype2polarity = {
        'si-dipole-b1b2-fam': 'monopolar',
        'si-quadrupole-q14-fam': 'monopolar',
        'si-sextupole-s15-sd-fam': 'monopolar',
        'si-sextupole-s15-ch': 'bipolar',
        'si-sextupole-s15-cv': 'bipolar',
        'si-sextupole-s15-qs': 'bipolar',
        'si-corrector-fcv': 'bipolar',
        'bo-ejekicker': 'monopolar',
        'si-hping': 'bipolar',
        'si-injdpk': 'monopolar',
        'si-injnlk': 'monopolar',
        'si-vping': 'bipolar',
        'tb-injseptum': 'monopolar',
        'ts-ejeseptum-thin': 'monopolar',
        'ts-ejeseptum-thick': 'monopolar',
        'ts-injseptum-thin': 'monopolar',
        'ts-injseptum-thick': 'monopolar',
    }

    pstype2magfunc = {
        'si-dipole-b1b2-fam': 'dipole',
        'si-quadrupole-q14-fam': 'quadrupole',
        'si-sextupole-s15-sd-fam': 'sextupole',
        'si-sextupole-s15-ch': 'corrector-horizontal',
        'si-sextupole-s15-cv': 'corrector-vertical',
        'si-sextupole-s15-qs': 'quadrupole-skew',
        'si-corrector-fcv': 'corrector-vertical',
        'bo-ejekicker': 'corrector-horizontal',
        'si-hping': 'corrector-horizontal',
        'si-injdpk': 'corrector-horizontal',
        'si-injnlk': 'corrector-horizontal',
        'si-vping': 'corrector-vertical',
        'tb-injseptum': 'corrector-horizontal',
        'ts-ejeseptum-thin': 'corrector-horizontal',
        'ts-ejeseptum-thick': 'corrector-horizontal',
        'ts-injseptum-thin': 'corrector-horizontal',
        'ts-injseptum-thick': 'corrector-horizontal',
    }

    pstype2splims = {
        'si-dipole-b1b2-fam':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 410.0, 'HIGH': 450.0, 'HIHI': 450.0, 'DRVH': 450.0},
        'si-quadrupole-q14-fam':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 160.0, 'HIGH': 165.0, 'HIHI': 165.0, 'DRVH': 165.0},
        'si-sextupole-s15-sd-fam':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 160.0, 'HIGH': 165.0, 'HIHI': 165.0, 'DRVH': 165.0},
        'si-sextupole-s15-ch':
            {'DRVL': -10.0, 'LOLO': -10.0, 'LOW': -10.0, 'LOPR': -9.9,
             'HOPR': 9.9, 'HIGH': 10.0, 'HIHI': 10.0, 'DRVH': 10.0},
        'si-sextupole-s15-cv':
            {'DRVL': -10.0, 'LOLO': -10.0, 'LOW': -10.0, 'LOPR': -9.9,
             'HOPR': 9.9, 'HIGH': 10.0, 'HIHI': 10.0, 'DRVH': 10.0},
        'si-sextupole-s15-qs':
            {'DRVL': -10.0, 'LOLO': -10.0, 'LOW': -10.0, 'LOPR': -9.9,
             'HOPR': 9.9, 'HIGH': 10.0, 'HIHI': 10.0, 'DRVH': 10.0},
        'si-corrector-fcv':
            {'DRVL': -9.0, 'LOLO': -9.0, 'LOW': -9.0, 'LOPR': -8.9,
             'HOPR': 8.9, 'HIGH': 9.0, 'HIHI': 9.0, 'DRVH': 9.0},
        'bo-ejekicker':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'si-hping':
            {'DRVL': -10.0, 'LOLO': -10.0, 'LOW': -10.0, 'LOPR': -9.9,
             'HOPR': 9.9, 'HIGH': 10.0, 'HIHI': 10.0, 'DRVH': 10.0},
        'si-injdpk':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'si-injnlk':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'si-vping':
            {'DRVL': -10.0, 'LOLO': -10.0, 'LOW': -10.0, 'LOPR': -9.9,
             'HOPR': 9.9, 'HIGH': 10.0, 'HIHI': 10.0, 'DRVH': 10.0},
        'tb-injseptum':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'ts-ejeseptum-thin':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'ts-ejeseptum-thick':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'ts-injseptum-thin':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
        'ts-injseptum-thick':
            {'DRVL': 0.0, 'LOLO': 0.0, 'LOW': 0.0, 'LOPR': 0.0,
             'HOPR': 995.0, 'HIGH': 1000.0, 'HIHI': 1000.0, 'DRVH': 1000.0},
    }

    @mock.patch('siriuspy.search._ExcitationData', autospec=True)
    @mock.patch('siriuspy.search._web', autospec=True)
    def setUp(self, mock_web, mock_excdata):
        """Common setup for all tests."""
        self.mock_excdata = mock_excdata
        self.mock_web = mock_web

        mock_web.server_online.return_value = True
        mock_web.power_supplies_pstypes_names_read.return_value = \
            read_test_file('pstypes-names.txt')
        mock_web.power_supplies_pstype_data_read.side_effect = \
            read_test_file
        mock_web.power_supplies_pstype_setpoint_limits.return_value = \
            read_test_file('pstypes-setpoint-limits.txt')
        mock_web.pulsed_power_supplies_pstype_setpoint_limits.return_value = \
            read_test_file('putypes-setpoint-limits.txt')

        # self.psnames = PSSearch.get_psnames()
        # self.pstypes = PSSearch.get_pstype_names()

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            PSSearch, TestPSSearch.public_interface)
        self.assertTrue(valid)

    # get_pstype_names
    def test_get_pstype_names(self):
        """Test get_pstype_names."""
        pstypes = PSSearch.get_pstype_names()
        self.assertIsInstance(pstypes, list)
        for pstype in pstypes:
            self.assertIsInstance(pstype, str)

    # get_psnames
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

    # get_splims
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

    def test_conv_psname_2_pstypes(self):
        """Test conv_psname_2_pstype."""
        for psname, pstype in TestPSSearch.sample.items():
            self.assertEqual(PSSearch.conv_psname_2_pstype(psname), pstype)
        # exceptions
        self.assertRaises(
            KeyError, PSSearch.conv_psname_2_pstype, psname='dummy')

    def test_conv_pstype_2_polarity(self):
        """Test conv_pstype_2_polarity."""
        for pstype, polarity in TestPSSearch.pstype2polarity.items():
            self.assertEqual(
                PSSearch.conv_pstype_2_polarity(pstype), polarity)
        # Non existent pstype return None
        self.assertIsNone(PSSearch.conv_pstype_2_polarity('dummy'))

    def test_conv_pstype_2_magfunc(self):
        """Test conv_pstype_2_polarity."""
        for pstype, magfunc in TestPSSearch.pstype2magfunc.items():
            self.assertEqual(
                PSSearch.conv_pstype_2_magfunc(pstype), magfunc)
        # Non existent pstype return None
        self.assertIsNone(PSSearch.conv_pstype_2_magfunc('dummy'))

    def test_conv_pstype_2_splims(self):
        """Test conv_pstype_2_polarity."""
        for pstype, splims in TestPSSearch.pstype2splims.items():
            self.assertEqual(
                PSSearch.conv_pstype_2_splims(pstype), splims)
        # Non existent pstype return None
        self.assertRaises(
            KeyError, PSSearch.conv_pstype_2_splims, pstype='dummy')

    def _test_conv_psname_2_excdata(self):
        """Test conv_psname_2_excdata."""
        PSSearch.conv_psname_2_excdata("SI-Fam:PS-QDA")
        self.mock_excdata.assert_called()
        pass

    def test_conv_psname_2_ispulsed(self):
        """Test conv_psname_2_ispulsed."""
        for psname in TestPSSearch.sample:
            if "PU" in psname:
                self.assertTrue(PSSearch.conv_psname_2_ispulsed(psname))
            elif "PS" in psname:
                self.assertFalse(PSSearch.conv_psname_2_ispulsed(psname))
            else:
                self.assertRaises(
                    ValueError, PSSearch.conv_psname_2_ispulsed, psname=psname)

    def test_conv_psname_2_splims_dict(self):
        """Test conv psname_2_splims_dict."""
        splims_dict = PSSearch.get_pstype_2_splims_dict()
        for pstype, splims in TestPSSearch.pstype2splims.items():
            self.assertIn(pstype, splims_dict)
            self.assertEqual(splims, splims_dict[pstype])

    def test_get_splims_unit(self):
        """Test get_splims_unit."""
        self.assertEqual(PSSearch.get_splims_unit(True), ['V', 'Voltage'])
        self.assertEqual(PSSearch.get_splims_unit(False), ['A', 'Ampere'])

    def test_get_splims_labels(self):
        """Test get_splims_labels."""
        self.assertEqual(PSSearch.get_splims_labels(),
                         ['DRVL', 'LOLO', 'LOW', 'LOPR',
                          'HOPR', 'HIGH', 'HIHI', 'DRVH'])


class TestMASearch(unittest.TestCase):
    """Test MASearch."""

    public_interface = (
        None,
    )

    maname2trims = {
        "SI-Fam:MA-B1B2": ("SI-Fam:PS-B1B2-1", "SI-Fam:PS-B1B2-2"),
        "SI-Fam:MA-QDA": ("SI-Fam:PS-QDA", ),
        "SI-14M2:MA-QDB1": ("SI-Fam:PS-QDB1", "SI-14M2:PS-QDB1"),
        "SI-09M2:MA-SDA0":
            ("SI-Fam:PS-SDA0", "SI-09M2:PS-CH", "SI-09M2:PS-CV"),
        "SI-07C4:MA-CH": ("SI-07C4:PS-CH",),
        "BO-15U:MA-CV": ("BO-15U:PS-CV",),
        "TB-03:MA-QF3": ("TB-03:PS-QF3",),
        "TS-01:MA-CV-2": ("TS-01:PS-CV-2",),
        "BO-01D:PM-InjK": ("BO-01D:PU-InjK",),
        "TB-04:PM-InjS": ("TB-04:PU-InjS",),
        "SI-01SA:PM-InjNLK": ("SI-01SA:PU-InjNLK",),
    }

    @mock.patch('siriuspy.search._web', autospec=True)
    def setUp(self, mock_web):
        """Common setup for all tests."""
        self.mock_web = mock_web

        mock_web.server_online.return_value = True
        mock_web.magnets_excitation_ps_read.return_value = \
            read_test_file('magnet-excitation-ps.txt')
        mock_web.magnets_setpoint_limits.return_value = \
            read_test_file('magnet-setpoint-limits.txt')
        mock_web.pulsed_magnets_setpoint_limits.return_value = \
            read_test_file('pulsed-magnet-setpoint-limits.txt')

    def _test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            search, TestMASearch.public_interface)
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
        manames = MASearch.get_manames({'discipline': 'PM'})
        self.assertEqual(len(manames), 12)
        for name in manames:
            self.assertIn('PM', name)
        manames = MASearch.get_manames({'sub_section': '0.M1'})
        self.assertEqual(len(manames), 84)

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

    def test_get_splims_unit(self):
        """Test get_splims_unit."""
        self.assertEqual(MASearch.get_splims_unit(True), ['V', 'Voltage'])
        self.assertEqual(MASearch.get_splims_unit(False), ['A', 'Ampere'])


#
#
# class TestMASearchMagFunc(unittest.TestCase):
#     """MASearch class."""
#
#     def setUp(self):
#         """Setup method."""
#         self.magnets = [
#             dict(
#                 input='SI-Fam:MA-B1B2',
#                 output={
#                     'SI-Fam:PS-B1B2-1': 'dipole',
#                     'SI-Fam:PS-B1B2-2': 'dipole'
#                 }
#             ),
#             dict(
#                 input='SI-Fam:MA-Q1',
#                 output={
#                     'SI-Fam:PS-Q1': 'quadrupole',
#                 }
#             ),
#             dict(
#                 input='SI-09M1:MA-QFA',
#                 output={
#                     'SI-Fam:PS-QFA': 'quadrupole',
#                     'SI-09M1:PS-QFA': 'quadrupole'
#                 }
#             ),
#             dict(
#                 input='SI-01M2:MA-SDA0',
#                 output={
#                     'SI-Fam:PS-SDA0': 'sextupole',
#                     'SI-01M2:PS-CH': 'corrector-horizontal',
#                     'SI-01M2:PS-CV': 'corrector-vertical'
#                 }
#             ),
#             dict(
#                 input='SI-01C2:MA-FC',
#                 output={
#                     'SI-01C2:PS-FCH': 'corrector-horizontal',
#                     'SI-01C2:PS-FCV': 'corrector-vertical',
#                     'SI-01C2:PS-QS': 'quadrupole-skew'
#                 }
#             )
#         ]
#
#     def test_conv_name_2_func(self):
#         """Test conv_name_2_func."""
#         for magnet in self.magnets:
#             for ps in magnet['output']:
#                 result = MASearch.conv_maname_2_magfunc(magnet['input'])
#                 self.assertEqual(magnet['output'], result)
#
#
# class TestMASearchLimitLabels(unittest.TestCase):
#     """TestMASearchLimitLabels class."""
#
#     def test_ma_limit_labels(self):
#         """Test limits and labels."""
#         for maname, ma_labels in MASearch._maname_2_splims_dict.items():
#             for label in MASearch._splims_labels:
#                 self.assertEqual(label in ma_labels, True)
#
#
# class TestMASearchLoading(unittest.TestCase):
    # """Test Loading methods."""
    #
    # def test_masearch_load_from_get_splims(self):
    #     """Test _maname_2_splims_dict."""
    #     MASearch.get_splims('SI-Fam:MA-QDA', 'lolo')
    #     self.assertEqual(MASearch._maname_2_splims_dict is not None, True)
    #
    # def test_masearch_load_from_get_splims_unit(self):
    #     """Test _splims_unit."""
    #     MASearch.get_splims_unit()
    #     self.assertEqual(MASearch._splims_unit is not None, True)
    #
    # def test_masearch_load_from_conv_maname_2_magfunc(self):
    #     """Test _maname_2_psnames_dict."""
    #     MASearch.conv_maname_2_magfunc('SI-Fam:MA-QDA')
    #     self.assertEqual(MASearch._maname_2_psnames_dict is not None, True)


if __name__ == "__main__":
    unittest.main()
