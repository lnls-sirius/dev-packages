#!/usr/bin/env python-sirius

"""Unittest module for enumtypes.py."""

from unittest import mock, TestCase
import siriuspy.pwrsupply.csdev as csdev
import siriuspy.util as util


_MOCK_FLAG = True


PUB_INTERFACE = (
    'MAX_WFMSIZE_FBP',
    'DEF_WFMSIZE_FBP',
    'DEFAULT_WFM_FBP',
    'MAX_WFMSIZE_OTHERS',
    'DEF_WFMSIZE_OTHERS',
    'DEFAULT_WFM_OTHERS',
    'DEFAULT_WFM',
    'PSSOFB_MAX_NR_UDC',
    'DEFAULT_SIGGEN_CONFIG',
    'PS_CURRENT_PRECISION',
    'PU_VOLTAGE_PRECISION',
    'PS_CURRENT_UNIT',
    'PU_VOLTAGE_UNIT',
    'PS_LI_INTLK_THRS',
    'ETypes',
    'Const',
    'get_ps_propty_database',
    'get_conv_propty_database',
    'get_ps_interlocks',
    'get_ps_modules',
)


class TestPwrSupplyCSDev(TestCase):
    """Test pwrsupply csdev module."""

    ps_alarm = ('Current-SP', 'Current-RB',
                'CurrentRef-Mon', 'Current-Mon', )
    pu_alarm = ('Voltage-SP', 'Voltage-RB',
                'Voltage-Mon', )
    pstypes = [
        'si-dipole-b1b2-fam',
        'si-quadrupole-q14-fam',
        'si-sextupole-s15-sd-fam',
        'si-sextupole-s15-ch',
        'si-sextupole-s15-cv',
        'si-sextupole-s15-qs',
        'si-corrector-fcv',
        'bo-ejekicker',
        'si-hping',
        'si-injdpk',
        'si-injnlk',
        'si-vping',
        'tb-injseptum',
        'ts-ejeseptum-thin',
        'ts-ejeseptum-thick',
        'ts-injseptum-thin',
        'ts-injseptum-thick',
    ]
    sample = {
        'SI-Fam:MA-B1B2': 'Energy-SP',
        'SI-Fam:MA-QDA': 'KL-SP',
        'SI-Fam:MA-SDB2': 'SL-SP',
        'SI-01C1:MA-CH': 'Kick-SP',
        'SI-02C3:MA-CV-2': 'Kick-SP',
        'SI-03M1:MA-QS': 'KL-SP',
        'SI-02M1:MA-FCV': 'Kick-SP',
        'BO-48D:PM-EjeKckr': 'Kick-SP',
        'SI-01SA:PM-PingH': 'Kick-SP',
        'SI-01SA:PM-InjDpKckr': 'Kick-SP',
        'SI-01SA:PM-InjNLKckr': 'Kick-SP',
        'SI-19C4:PM-PingV': 'Kick-SP',
        'TB-04:PM-InjSept': 'Kick-SP',
        'TS-01:PM-EjeSeptF': 'Kick-SP',
        'TS-01:PM-EjeSeptG': 'Kick-SP',
        'TS-04:PM-InjSeptF': 'Kick-SP',
        'TS-04:PM-InjSeptG-1': 'Kick-SP',
        'TS-04:PM-InjSeptG-2': 'Kick-SP',
    }

    def setUp(self):
        """Define setup method."""
        def get_splims(pstype, alarm):
            dbase = {'lolo': 0.0, 'low': 1.0, 'lolim': 2.0, 'hilim': 3.0,
                     'high': 4.0, 'hihi': 5.0}
            return dbase[alarm]

        def get_splims_unit(psmodel):
            if psmodel in ('FBP', 'FAC', 'FAP', 'FAC_2S', 'FAC_2P4S'):
                return ['A', 'Ampere']
            return ['V', 'Voltage']

        if _MOCK_FLAG:
            _pssearch_patcher = mock.patch(
                'siriuspy.pwrsupply.csdev._PSSearch', autospec=True)
            self.addCleanup(_pssearch_patcher.stop)
            self.m_pssearch = _pssearch_patcher.start()
            self.m_pssearch.get_splims_unit.side_effect = get_splims_unit
            self.m_pssearch.get_pstype_names.return_value = \
                TestPwrSupplyCSDev.pstypes
            self.m_pssearch.get_splims.side_effect = get_splims
            self.m_pssearch.conv_psname_2_psmodel.return_value = 'FBP'
            self.m_pssearch.conv_pstype_2_magfunc.return_value = 'quadrupole'

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(csdev, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_MAX_WFMSIZE_FBP(self):
        """Test MAX_WFMSIZE_FBP."""
        self.assertIsInstance(csdev.MAX_WFMSIZE_FBP, int)
        self.assertTrue(csdev.MAX_WFMSIZE_FBP > 0)

    def test_DEF_WFMSIZE_FBP(self):
        """Test DEF_WFMSIZE_FBP."""
        self.assertIsInstance(csdev.DEF_WFMSIZE_FBP, int)
        self.assertTrue(csdev.DEF_WFMSIZE_FBP > 0)
        self.assertTrue(csdev.DEF_WFMSIZE_FBP <= csdev.MAX_WFMSIZE_FBP)

    def test_MAX_WFMSIZE_OTHERS(self):
        """Test MAX_WFMSIZE_OTHERS."""
        self.assertIsInstance(csdev.MAX_WFMSIZE_OTHERS, int)
        self.assertTrue(csdev.MAX_WFMSIZE_OTHERS > 0)

    def test_DEF_WFMSIZE_OTHERS(self):
        """Test DEF_WFMSIZE_OTHERS."""
        self.assertIsInstance(csdev.DEF_WFMSIZE_OTHERS, int)
        self.assertTrue(csdev.DEF_WFMSIZE_OTHERS > 0)
        self.assertTrue(
            csdev.DEF_WFMSIZE_OTHERS <= csdev.MAX_WFMSIZE_OTHERS)

    def test_DEFAULT_SIGGEN_CONFIG(self):
        """Test DEFAULT_SIGGEN_CONFIG."""
        self.assertIsInstance(csdev.DEFAULT_SIGGEN_CONFIG, tuple)
        self.assertTrue(len(csdev.DEFAULT_SIGGEN_CONFIG), 9)

    def test_ps_propty_database(self):
        """Test ps_propty_database."""
        current_pvs = TestPwrSupplyCSDev.ps_alarm
        for pstype in TestPwrSupplyCSDev.pstypes:
            dbase = csdev.get_ps_propty_database('FBP', pstype)
            unit = dbase['Current-SP']['unit']
            for propty, dbi in dbase.items():
                # set setpoint limits in database
                if propty in TestPwrSupplyCSDev.ps_alarm:
                    self.assertLessEqual(dbi['lolo'], dbi['low'])
                    self.assertLessEqual(dbi['low'], dbi['lolim'])
                    self.assertLessEqual(dbi['lolim'], dbi['hilim'])
                    self.assertLessEqual(dbi['hilim'], dbi['high'])
                    self.assertLessEqual(dbi['high'], dbi['hihi'])
                if propty in current_pvs:
                    self.assertEqual(dbi['unit'], unit)

    def test_ps_FBP_propty_database(self):
        """Test ps_FBP_propty_database."""
        dbase = csdev.get_ps_propty_database('FBP', 'si-quadrupole-q14-fam')
        self.assertIsInstance(dbase, dict)
        for prop in dbase:
            self.assertIsInstance(dbase[prop], dict)
        # test precision consistency
        proptys = TestPwrSupplyCSDev.ps_alarm
        for propty in proptys:
            self.assertIn(propty, dbase)

    def test_ps_basic_propty_database(self):
        """Test ps_basic_propty_database."""
        dbase = csdev._get_ps_basic_propty_database()
        self.assertIsInstance(dbase, dict)
        for prop in dbase:
            self.assertIsInstance(dbase[prop], dict)

    def test_ps_common_propty_database(self):
        """Test ps_common_propty_database."""
        dbase = csdev._get_ps_common_propty_database()
        self.assertIsInstance(dbase, dict)
        for prop in dbase:
            self.assertIsInstance(dbase[prop], dict)
