"""Unittest module for ps_search.py."""

from unittest import TestCase

from siriuspy import util
from siriuspy.search import ps_search
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.siggen import Signal
from siriuspy.magnet.excdata import ExcitationData


class TestModule(TestCase):
    """Test Search module."""

    public_interface = (
        'PSSearch',
    )

    def _test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            ps_search, TestModule.public_interface)
        self.assertTrue(valid)


class TestPSSearch(TestCase):
    """Test PSSearch."""

    public_interface = (
        'get_psnames',
        'get_psnicknames',
        'get_pstype_names',
        'get_psmodel_names',
        'get_bbbnames',
        'get_splims',
        'get_pstype_dict',
        'get_bbbname_dict',
        'get_udc_dict',
        'get_polarities',
        'conv_psname_2_pstype',
        'conv_psname_2_splims',
        'conv_pstype_2_polarity',
        'conv_pstype_2_magfunc',
        'conv_pstype_2_splims',
        'conv_psname_2_magfunc',
        'conv_psname_2_excdata',
        'conv_psname_2_psmodel',
        'conv_psmodel_2_psname',
        'conv_psname_2_siggenconf',
        'conv_psname_2_bbbname',
        'conv_bbbname_2_psnames',
        'conv_bbbname_2_bsmps',
        'conv_bbbname_2_freq',
        'conv_bbbname_2_udc',
        'conv_udc_2_bbbname',
        'conv_udc_2_bsmps',
        'conv_psname_2_udc',
        'conv_psname_2_dclink',
        'conv_dclink_2_psname',
        'get_linac_ps_sinap2sirius_dict',
        'get_linac_ps_sirius2sinap_dict',
        'get_pstype_2_psnames_dict',
        'get_pstype_2_splims_dict',
        'get_splims_unit',
        'get_splims_labels',
        'get_psname_2_dclink_dict',
        'get_dclink_2_psname_dict',
    )

    sample = {
        'SI-Fam:PS-B1B2-1': 'si-dipole-b1b2-fam',
        'SI-Fam:PS-QDA': 'si-quadrupole-q14-fam',
        'SI-Fam:PS-SDB2': 'si-sextupole-s15-sd-fam',
        'SI-01C1:PS-CH': 'si-sextupole-s15-ch',
        'SI-02C3:PS-CV-2': 'si-sextupole-s15-cv',
        'SI-03M1:PS-QS': 'si-sextupole-s15-qs',
        'SI-02M1:PS-FCV': 'si-corrector-fcv',
        'BO-48D:PU-EjeKckr': 'bo-ejekicker',
        'SI-01SA:PU-PingH': 'si-hping',
        'SI-01SA:PU-InjDpKckr': 'si-injdpk',
        'SI-01SA:PU-InjNLKckr': 'si-injnlk',
        'SI-19C4:PU-PingV': 'si-vping',
        'TB-04:PU-InjSept': 'tb-injseptum',
        'TS-01:PU-EjeSeptF': 'ts-ejeseptum-thin',
        'TS-01:PU-EjeSeptG': 'ts-ejeseptum-thick',
        'TS-04:PU-InjSeptF': 'ts-injseptum-thin',
        'TS-04:PU-InjSeptG-1': 'ts-injseptum-thick',
        'TS-04:PU-InjSeptG-2': 'ts-injseptum-thick',
    }

    sample_bbb = {
        'PA-RaPSC03:CO-PSCtrl-BO4': None,
        'PA-RaPSC03:CO-PSCtrl-BO3': None,
        'PA-RaPSC03:CO-PSCtrl-BO2': None,
        'PA-RaPSE05:CO-PSCtrl-BO': None,
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
        # # with filters
        # bbbnames = PSSearch.get_bbbnames({'dis': 'CO'})
        # self.assertEqual(len(bbbnames), 289)
        # for name in bbbnames:
        #     self.assertIn('CO', name)
        # bbbnames = PSSearch.get_bbbnames({'sub': 'Glob'})
        # self.assertEqual(len(bbbnames), 29)
        # exceptions
        self.assertRaises(TypeError, PSSearch.get_bbbnames, filters=23)
        self.assertRaises(TypeError, PSSearch.get_bbbnames, filters=23.4)
        self.assertRaises(TypeError, PSSearch.get_bbbnames, filters=[0, ])
        self.assertRaises(TypeError, PSSearch.get_bbbnames, filters=(0.0, ))

    def test_get_splims(self):
        """Test get_splims."""
        lim1 = PSSearch.get_splims(
            pstype='si-quadrupole-q30-trim', label='lolo')
        lim2 = PSSearch.get_splims(
            pstype='si-quadrupole-q30-trim', label='hihi')
        self.assertGreater(lim2, lim1)
        # exceptions
        self.assertRaises(
            KeyError, PSSearch.get_splims,
            pstype='dummy', label='low')
        self.assertRaises(
            KeyError, PSSearch.get_splims,
            pstype='bo-corrector-ch', label='dummy')

    def test_get_pstype_dict(self):
        """Test get_pstype_dict."""
        dict_ = PSSearch.get_pstype_dict()
        self.assertIsInstance(dict_, dict)
        pstypes_d = sorted(list(dict_.keys()))
        pstypes = sorted(PSSearch.get_pstype_names())
        self.assertEqual(pstypes_d, pstypes)

    def test_get_bbbname_dict(self):
        """Test get_bbbname_dict."""
        dict_ = PSSearch.get_bbbname_dict()
        self.assertIsInstance(dict_, dict)
        for bbbname in TestPSSearch.sample_bbb:
            self.assertTrue(bbbname in dict_)

    def test_get_polarities(self):
        """Test get_polarities."""
        polarities = PSSearch.get_polarities()
        self.assertIsInstance(polarities, list)
        for pol in polarities:
            self.assertIsInstance(pol, str)
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

    def test_conv_psname_2_excdata(self):
        """Test conv_psname_2_excdata."""
        self.assertRaises(KeyError, PSSearch.conv_psname_2_excdata, '')
        excdata = PSSearch.conv_psname_2_excdata('SI-Fam:PS-B1B2-1')
        self.assertIsInstance(excdata, ExcitationData)

    def test_conv_psname_2_psmodel(self):
        """Test conv_psname_2_psmodel."""
        for psn in TestPSSearch.sample:
            model = PSSearch.conv_psname_2_psmodel(psname=psn)
            self.assertIsInstance(model, str)

    def test_conv_psname_2_siggenconf(self):
        """Test conv_psname_2_siggenconf."""
        for psn in TestPSSearch.sample:
            siggenconf = PSSearch.conv_psname_2_siggenconf(psname=psn)
            self.assertIsInstance(siggenconf, Signal)

    def test_conv_bbbname_2_psnames(self):
        """Test conv_bbbname_2_psnames."""
        self.assertRaises(TypeError, PSSearch.conv_bbbname_2_psnames)
        self.assertRaises(KeyError, PSSearch.conv_bbbname_2_psnames, '')
        bsmps = PSSearch.conv_bbbname_2_psnames(
            bbbname='PA-RaPSF05:CO-PSCtrl-BO')
        self.assertIsInstance(bsmps, list)
        self.assertGreater(len(bsmps), 0)
        self.assertIsInstance(bsmps[0], tuple)
        self.assertIsInstance(bsmps[0][0], str)
        self.assertIsInstance(bsmps[0][1], int)

    def test_conv_bbbname_2_freq(self):
        """Test conv_bbbname_2_freqs."""
        self.assertRaises(TypeError, PSSearch.conv_bbbname_2_freq)
        self.assertRaises(KeyError, PSSearch.conv_bbbname_2_psnames, '')
        freq = PSSearch.conv_bbbname_2_freq(
            bbbname='LA-RaCtrl:CO-PSCtrl-TB1')
        self.assertIsInstance(freq, float)

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
        self.assertRaises(TypeError, PSSearch.get_splims_unit)
        self.assertRaises(ValueError, PSSearch.get_splims_unit, '')
        self.assertRaises(TypeError, PSSearch.get_splims_unit)
        self.assertEqual(PSSearch.get_splims_unit('FBP'), ['A', 'Ampere'])

    def test_get_splims_labels(self):
        """Test get_splims_labels."""
        self.assertEqual(PSSearch.get_splims_labels(),
                         ['DRVL', 'LOLO', 'LOW', 'LOPR',
                          'HOPR', 'HIGH', 'HIHI', 'DRVH',
                          'DTOL_CUR', 'DTOL_WFM', 'TSTV', 'TSTR'])
