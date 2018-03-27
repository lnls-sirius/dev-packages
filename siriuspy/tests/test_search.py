#!/usr/bin/env python-sirius

"""Unittest module for search.py."""

import unittest
from unittest import mock

from siriuspy import util
from siriuspy import search
from siriuspy.search import PSSearch
from siriuspy.search import MASearch
from siriuspy.magnet.excdata import ExcitationData

mock_flag = True

public_interface = (
    'PSSearch',
    'MASearch',
)


def read_test_file(path):
    """Read a file."""
    with open('test_data/servweb/' + path, "r") as fd:
        return fd.read()


def read_test_ps_pstypes(path):
    """Read a file."""
    with open('test_data/servweb/pwrsupply/pstypes-data/' + path, "r") as fd:
        return fd.read()


def read_test_ma_excdata(path):
    """Read a file."""
    with open('test_data/servweb/magnet/excitation-data/' + path, "r") as fd:
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
        'get_pstype_names',
        'get_bbbnames',
        'get_splims',
        'get_pstype_dict',
        'get_bbbname_dict',
        'get_polarities',
        'conv_psname_2_pstype',
        'conv_pstype_2_polarity',
        'conv_pstype_2_magfunc',
        'conv_pstype_2_splims',
        'conv_psname_2_excdata',
        'check_psname_ispulsed',
        'conv_psname_2_psmodel',
        'check_pstype_ispulsed',
        'conv_psname_2_bbbname',
        'conv_bbbname_2_psnames',
        'get_pstype_2_psnames_dict',
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

    sample_bbb = {
        'BO-Glob:CO-BBB-1': None,
        'BO-Glob:CO-BBB-2': None,
        'BO-01:CO-BBB-1': None,
        'BO-01:CO-BBB-2': None,
        'SI-01:CO-BBB-1': None,
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

    def setUp(self):
        """Common setup for all tests."""
        if mock_flag:
            # Create Mocks
            web_patcher = mock.patch('siriuspy.search._web', autospec=True)
            excdata_patcher = mock.patch(
                'siriuspy.search._ExcitationData', autospec=True)
            self.addCleanup(web_patcher.stop)
            self.addCleanup(excdata_patcher.stop)
            self.mock_web = web_patcher.start()
            self.mock_excdata = excdata_patcher.start()
            # Set mocked functions behaviour
            self.mock_web.server_online.return_value = True
            self.mock_web.ps_pstypes_names_read.return_value = \
                read_test_file('pwrsupply/pstypes-names.txt')
            self.mock_web.ps_pstype_data_read.side_effect = \
                read_test_ps_pstypes
            self.mock_web.ps_pstype_setpoint_limits.return_value = \
                read_test_file('pwrsupply/pstypes-setpoint-limits.txt')
            self.mock_web.pu_pstype_setpoint_limits.return_value = \
                read_test_file('pwrsupply/putypes-setpoint-limits.txt')
            self.mock_web.ps_psmodels_read.return_value = \
                read_test_file('pwrsupply/psmodels.txt')
            self.mock_web.pu_psmodels_read.return_value = \
                read_test_file('pwrsupply/pumodels.txt')
            self.mock_web.beaglebone_power_supplies_mapping.return_value = \
                read_test_file(
                    'pwrsupply/beaglebone-mapping.txt')

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
        psnames = PSSearch.get_psnames({'dis': 'PU'})
        self.assertEqual(len(psnames), 12)
        for name in psnames:
            self.assertIn('PU', name)
        psnames = PSSearch.get_psnames({'sub': '0.M1'})
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

    def test_get_bbbnames(self):
        """Test get_bbbnames."""
        # without filters
        bbbnames = PSSearch.get_bbbnames()
        self.assertIsInstance(bbbnames, (list, tuple))
        for bbbname in TestPSSearch.sample_bbb:
            self.assertIn(bbbname, bbbnames)
        # check sorted
        sorted_bbbnames = sorted(bbbnames)
        self.assertEqual(bbbnames, sorted_bbbnames)
        # with filters
        bbbnames = PSSearch.get_bbbnames({'dis': 'CO'})
        self.assertEqual(len(bbbnames), 277)
        for name in bbbnames:
            self.assertIn('CO', name)
        bbbnames = PSSearch.get_bbbnames({'sub': 'Glob'})
        self.assertEqual(len(bbbnames), 29)
        # exceptions
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=23)
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=23.4)
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=[0, ])
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=(0.0, ))

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

    def test_get_bbbname_dict(self):
        """Test get_bbbname_dict."""
        d = PSSearch.get_bbbname_dict()
        self.assertIsInstance(d, dict)
        for bbbname in TestPSSearch.sample_bbb:
            self.assertTrue(bbbname in d)

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
        # Non existent pstype raises KeyError
        self.assertRaises(KeyError,
                          PSSearch.conv_pstype_2_polarity, pstype='dummy')

    def test_conv_pstype_2_magfunc(self):
        """Test conv_pstype_2_polarity."""
        for pstype, magfunc in TestPSSearch.pstype2magfunc.items():
            self.assertEqual(
                PSSearch.conv_pstype_2_magfunc(pstype), magfunc)
        # Non existent pstype raises KeyError
        self.assertRaises(KeyError,
                          PSSearch.conv_pstype_2_magfunc, pstype='dummy')

    def test_conv_pstype_2_splims(self):
        """Test conv_pstype_2_polarity."""
        pstypes = tuple(TestPSSearch.pstype2polarity.keys())
        for pstype in pstypes:
            splims = PSSearch.conv_pstype_2_splims(pstype)
            self.assertIsInstance(splims, dict)
        # Non existent pstype return None
        self.assertRaises(
            KeyError, PSSearch.conv_pstype_2_splims, pstype='dummy')

    def _test_conv_psname_2_excdata(self):
        """Test conv_psname_2_excdata."""
        calls = []
        for ps, pstype in TestPSSearch.sample.items():
            if pstype in PSSearch._pstype_2_excdat_dict:
                calls.append(mock.call(filename_web=pstype + '.txt'))
            excdata = PSSearch.conv_psname_2_excdata(ps)
            self.assertIsInstance(excdata, ExcitationData)
        if mock_flag:
            self.mock_excdata.assert_called()
            self.mock_excdata.assert_has_calls(calls)

    def test_check_psname_ispulsed(self):
        """Test check_psname_ispulsed."""
        for psname in TestPSSearch.sample:
            if ":PU" in psname:
                self.assertTrue(PSSearch.check_psname_ispulsed(psname))
            elif ":PS" in psname:
                self.assertFalse(PSSearch.check_psname_ispulsed(psname))
        self.assertRaises(KeyError,
                          PSSearch.check_psname_ispulsed, psname='A-B:C-D:E')

    def test_conv_psname_2_psmodel(self):
        """Test conv_psname_2_psmodel."""
        for ps, pstype in TestPSSearch.sample.items():
            model = PSSearch.conv_psname_2_psmodel(psname=ps)
            self.assertIsInstance(model, str)

    def test_check_pstype_ispulsed(self):
        """Test check_pstype_isplused."""
        pstypes = PSSearch.get_pstype_names()
        for pstype in pstypes:
            if ":PU" in pstype:
                self.assertTrue(PSSearch.check_pstype_ispulsed(pstype))
            elif ":PS" in pstype:
                self.assertFalse(PSSearch.check_pstype_ispulsed(pstype))
        self.assertRaises(KeyError,
                          PSSearch.check_pstype_ispulsed, pstype='dummy')

    def test_conv_bbbname_2_psnames(self):
        """Test conv_bbbname_2_psnames."""
        self.assertRaises(TypeError, PSSearch.conv_bbbname_2_psnames)
        self.assertRaises(KeyError, PSSearch.conv_bbbname_2_psnames, '')
        psnames = PSSearch.conv_bbbname_2_psnames(bbbname='SI-Glob:CO-BBB-1')
        self.assertIsInstance(psnames, list)
        self.assertGreater(len(psnames), 0)
        self.assertIsInstance(psnames[0], str)

    def test_get_pstype_2_psnames_dict(self):
        """Test get_pstype_2_psnames_dict."""
        typ2name = PSSearch.get_pstype_2_psnames_dict()
        self.assertIsInstance(typ2name, dict)
        for pstype, psnames in typ2name.items():
            self.assertIsInstance(pstype, str)
            self.assertIsInstance(psnames, (tuple, list))
            self.assertTrue(len(psnames) > 0)

    def test_get_psname_2_splims_dict(self):
        """Test conv psname_2_splims_dict."""
        limlabels = ('DRVL', 'LOLO', 'LOW', 'LOPR',
                     'HOPR', 'HIGH', 'HIHI', 'DRVH')
        splims_dict = PSSearch.get_pstype_2_splims_dict()
        self.assertIsInstance(splims_dict, dict)
        for pstype, splims in splims_dict.items():
            self.assertIsInstance(pstype, str)
            self.assertIsInstance(splims, dict)
            for limlabel in limlabels:
                self.assertIn(limlabel, splims)
            self.assertTrue(splims['LOLO'] <= splims['LOW'])
            self.assertTrue(splims['LOW'] < splims['HIGH'])
            self.assertTrue(splims['HIGH'] <= splims['HIHI'])

    def test_get_splims_unit(self):
        """Test get_splims_unit."""
        self.assertEqual(PSSearch.get_splims_unit(True), ['V', 'Voltage'])
        self.assertEqual(PSSearch.get_splims_unit(False), ['A', 'Ampere'])
        self.assertRaises(ValueError, PSSearch.get_splims_unit, ispulsed='')

    def test_get_splims_labels(self):
        """Test get_splims_labels."""
        self.assertEqual(PSSearch.get_splims_labels(),
                         ['DRVL', 'LOLO', 'LOW', 'LOPR',
                          'HOPR', 'HIGH', 'HIHI', 'DRVH'])


class TestMASearch(unittest.TestCase):
    """Test MASearch."""

    public_interface = (
        'get_manames',
        'get_pwrsupply_manames',
        'get_splims_unit',
        'get_splims',
        'conv_maname_2_trims',
        'conv_maname_2_magfunc',
        'conv_maname_2_splims',
        'conv_maname_2_psnames',
        'conv_psname_2_maname',
        'get_maname_2_splims_dict',
        'check_maname_ispulsed'
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
        "BO-01D:PM-InjK": None,
        "TB-04:PM-InjS": None,
        "SI-01SA:PM-InjNLK": None,
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
        'BO-01D:PM-InjK': {'BO-01D:PU-InjK': 'corrector-horizontal'},
        'TB-04:PM-InjS': {'TB-04:PU-InjS': 'corrector-horizontal'},
        'SI-01SA:PM-InjNLK': {'SI-01SA:PU-InjNLK': 'corrector-horizontal'},
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
        'BO-01D:PM-InjK': ('BO-01D:PU-InjK',),
        'TB-04:PM-InjS': ('TB-04:PU-InjS',),
        'SI-01SA:PM-InjNLK': ('SI-01SA:PU-InjNLK',),
    }

    psname2maname = {
        'SI-Fam:PS-B1B2-1': 'SI-Fam:MA-B1B2',
        'SI-Fam:PS-B1B2-2': 'SI-Fam:MA-B1B2',
        'BO-Fam:PS-B-1': 'BO-Fam:MA-B',
        'BO-Fam:PS-B-2': 'BO-Fam:MA-B',
        'SI-01M1:PS-CH': 'SI-01M1:MA-SDA0',
    }

    def setUp(self):
        """Common setup for all tests."""
        if mock_flag:
            # Create Mocks
            web_patcher = mock.patch('siriuspy.search._web')
            self.addCleanup(web_patcher.stop)
            self.mock_web = web_patcher.start()
            # MASearch funcs
            self.mock_web.server_online.return_value = True
            self.mock_web.magnets_excitation_ps_read.return_value = \
                read_test_file('magnet/magnet-excitation-ps.txt')
            self.mock_web.magnets_setpoint_limits.return_value = \
                read_test_file('magnet/magnet-setpoint-limits.txt')
            self.mock_web.pulsed_magnets_setpoint_limits.return_value = \
                read_test_file('magnet/pulsed-magnet-setpoint-limits.txt')
            # PSSearch funcs
            self.mock_web.ps_pstypes_names_read.return_value = \
                read_test_file('pwrsupply/pstypes-names.txt')
            self.mock_web.ps_pstype_data_read.side_effect = \
                read_test_ps_pstypes
            self.mock_web.ps_pstype_setpoint_limits.return_value = \
                read_test_file('pwrsupply/pstypes-setpoint-limits.txt')
            self.mock_web.pu_pstype_setpoint_limits.return_value = \
                read_test_file('pwrsupply/putypes-setpoint-limits.txt')

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            search.MASearch, TestMASearch.public_interface)
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

    def test_get_pwrsupply_manames(self):
        """Test get_pwrsupply_manames."""
        ps_manames = MASearch.get_pwrsupply_manames()
        self.assertIsInstance(ps_manames, (list, tuple))
        manames = tuple(MASearch.get_maname_2_splims_dict().keys())
        for ps_maname in ps_manames:
            self.assertIn(ps_maname, manames)

    def test_get_splims_unit(self):
        """Test get_splims_unit."""
        self.assertEqual(MASearch.get_splims_unit(True), ['V', 'Voltage'])
        self.assertEqual(MASearch.get_splims_unit(False), ['A', 'Ampere'])

    def test_get_splims(self):
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

    def test_conv_maname_2_trims(self):
        """Test conv_maname_2_trims."""
        for ma, trims in TestMASearch.maname2trims.items():
            self.assertEqual(MASearch.conv_maname_2_trims(ma), trims)

    def test_conv_maname_2_magfunc(self):
        """Test conv_maname_2_magfunc."""
        for ma, magfuncs in TestMASearch.maname2magfuncs.items():
            self.assertEqual(MASearch.conv_maname_2_magfunc(ma), magfuncs)

    def test_conv_maname_2_splims(self):
        """Test conv_maname_2_splims."""
        limlabels = ('DRVL', 'LOLO', 'LOW', 'LOPR',
                     'HOPR', 'HIGH', 'HIHI', 'DRVH')
        splims_dict = MASearch.get_maname_2_splims_dict()
        self.assertIsInstance(splims_dict, dict)
        for pstype, splims in splims_dict.items():
            self.assertIsInstance(pstype, str)
            self.assertIsInstance(splims, dict)
            for limlabel in limlabels:
                self.assertIn(limlabel, splims)
            self.assertTrue(splims['LOLO'] <= splims['LOW'])
            self.assertTrue(splims['LOW'] < splims['HIGH'])
            self.assertTrue(splims['HIGH'] <= splims['HIHI'])

    def test_conv_maname_2_psnames(self):
        """Test conv_maname_2_psnames."""
        for ma, psnames in TestMASearch.maname2psnames.items():
            self.assertEqual(MASearch.conv_maname_2_psnames(ma), psnames)

    def test_psname_2_maname(self):
        """Test psname_2_maname."""
        for psname, maname in TestMASearch.psname2maname.items():
            self.assertEqual(MASearch.conv_psname_2_maname(psname), maname)

    def test_check_maname_ispulsed(self):
        """Test check_maname_ispulsed."""
        for maname in TestMASearch.maname2trims:
            if ":PM" in maname:
                self.assertTrue(MASearch.check_maname_ispulsed(maname))
            elif ":MA" in maname:
                self.assertFalse(MASearch.check_maname_ispulsed(maname))
        self.assertRaises(KeyError,
                          MASearch.check_maname_ispulsed, maname='A-B:C-D:E')

    def test_get_maname_2_splims_dict(self):
        """Test get_maname_2_splims_dict."""
        limlabels = ('DRVL', 'LOLO', 'LOW', 'LOPR',
                     'HOPR', 'HIGH', 'HIHI', 'DRVH')
        splims_dict = MASearch.get_maname_2_splims_dict()
        self.assertIsInstance(splims_dict, dict)
        for pstype, splims in splims_dict.items():
            self.assertIsInstance(pstype, str)
            self.assertIsInstance(splims, dict)
            for limlabel in limlabels:
                self.assertIn(limlabel, splims)
            self.assertTrue(splims['LOLO'] <= splims['LOW'])
            self.assertTrue(splims['LOW'] < splims['HIGH'])
            self.assertTrue(splims['HIGH'] <= splims['HIHI'])


if __name__ == "__main__":
    unittest.main()
