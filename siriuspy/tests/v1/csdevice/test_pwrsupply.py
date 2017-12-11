#!/usr/bin/env python-sirius

"""Unittest module for enumtypes.py."""

import unittest
from unittest import mock
from siriuspy.search import PSSearch
import siriuspy.csdevice.pwrsupply as pwrsupply
import siriuspy.util as util


_mock_flag = True


public_interface = (
    'default_wfmsize',
    'default_wfmlabels',
    'default_intlklabels',
    'default_ps_current_precision',
    'default_pu_current_precision',
    'get_ps_current_unit',
    'get_pu_current_unit',
    'get_common_propty_database',
    'get_common_ps_propty_database',
    'get_common_pu_propty_database',
    'get_ps_propty_database',
    'get_pu_propty_database',
    'get_ma_propty_database',
    'get_pm_propty_database',
)


class TestPwrSupply(unittest.TestCase):
    """Test pwrsupply module."""

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
        'BO-48D:PM-EjeK': 'Kick-SP',
        'SI-01SA:PM-HPing': 'Kick-SP',
        'SI-01SA:PM-InjDpK': 'Kick-SP',
        'SI-01SA:PM-InjNLK': 'Kick-SP',
        'SI-19C4:PM-VPing': 'Kick-SP',
        'TB-04:PM-InjS': 'Kick-SP',
        'TS-01:PM-EjeSF': 'Kick-SP',
        'TS-01:PM-EjeSG': 'Kick-SP',
        'TS-04:PM-InjSF': 'Kick-SP',
        'TS-04:PM-InjSG-1': 'Kick-SP',
        'TS-04:PM-InjSG-2': 'Kick-SP',
    }

    def setUp(self):
        """Setup method."""
        def get_splims(pstype, alarm):
            db = {'lolo': 0.0, 'low': 1.0, 'lolim': 2.0, 'hilim': 3.0,
                  'high': 4.0, 'hihi': 5.0}
            return db[alarm]

        def get_splims_unit(ispulsed):
            if ispulsed is True:
                return ['V', 'Voltage']
            elif ispulsed is False:
                return ['A', 'Ampere']
            else:
                raise ValueError

        if _mock_flag:
            _PSSearch_patcher = mock.patch(
                'siriuspy.csdevice.pwrsupply._PSSearch', autospec=True)
            self.addCleanup(_PSSearch_patcher.stop)
            self.m_PSSearch = _PSSearch_patcher.start()
            self.m_PSSearch.get_splims_unit.side_effect = get_splims_unit
            self.m_PSSearch.get_pstype_names.return_value = \
                TestPwrSupply.pstypes
            self.m_PSSearch.get_splims.side_effect = get_splims
            _MASearch_patcher = mock.patch(
                'siriuspy.csdevice.pwrsupply._MASearch', autospec=True)
            self.addCleanup(_MASearch_patcher.stop)
            self.m_MASearch = _MASearch_patcher.start()
            self.m_MASearch.get_splims_unit.side_effect = get_splims_unit

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            pwrsupply, public_interface)
        self.assertTrue(valid)

    def test_ps_current_unit(self):
        """Test  ps_current_unit."""
        unit = pwrsupply.get_ps_current_unit()
        self.assertIsInstance(unit, (list, tuple))
        self.assertEqual(unit[0], 'A')
        self.assertEqual(unit[1], 'Ampere')

    def test_pu_current_unit(self):
        """Test  pu_current_unit."""
        unit = pwrsupply.get_pu_current_unit()
        self.assertIsInstance(unit, (list, tuple))
        self.assertEqual(unit[0], 'V')
        self.assertEqual(unit[1], 'Voltage')

    def test_common_propty_database(self):
        """Test common_propty_database."""
        db = pwrsupply.get_common_propty_database()
        self.assertIsInstance(db, dict)
        for prop in db:
            self.assertIsInstance(db[prop], dict)

    def test_common_ps_propty_database(self):
        """Test common_ps_propty_database."""
        db = pwrsupply.get_common_ps_propty_database()
        self.assertIsInstance(db, dict)
        for prop in db:
            self.assertIsInstance(db[prop], dict)
        # test precision consistency
        proptys = TestPwrSupply.ps_alarm + ('WfmData-SP', 'WfmData-RB')
        for propty in proptys:
            self.assertEqual(db[propty]['prec'],
                             pwrsupply.default_ps_current_precision)

    def test_ps_propty_database(self):
        """Test ps_propty_database."""
        current_pvs = TestPwrSupply.ps_alarm + \
            ('WfmData-SP', 'WfmData-RB')
        for pstype in TestPwrSupply.pstypes:
            db = pwrsupply.get_ps_propty_database(pstype)
            unit = db['Current-SP']['unit']
            for propty, dbi in db.items():
                # set setpoint limits in database
                if propty in TestPwrSupply.ps_alarm:
                    self.assertLessEqual(dbi['lolo'], dbi['low'])
                    self.assertLessEqual(dbi['low'], dbi['lolim'])
                    self.assertLessEqual(dbi['lolim'], dbi['hilim'])
                    self.assertLessEqual(dbi['hilim'], dbi['high'])
                    self.assertLessEqual(dbi['high'], dbi['hihi'])
                if propty in current_pvs:
                    self.assertEqual(dbi['unit'], unit)

    def test_pu_propty_database(self):
        """Test pu_propty_database."""
        current_pvs = TestPwrSupply.pu_alarm
        for pstype in TestPwrSupply.pstypes:
            db = pwrsupply.get_pu_propty_database(pstype)
            unit = db['Voltage-SP']['unit']
            for propty, dbi in db.items():
                # set setpoint limits in database
                if propty in TestPwrSupply.ps_alarm:
                    self.assertLessEqual(dbi['lolo'], dbi['low'])
                    self.assertLessEqual(dbi['low'], dbi['lolim'])
                    self.assertLessEqual(dbi['lolim'], dbi['hilim'])
                    self.assertLessEqual(dbi['hilim'], dbi['high'])
                    self.assertLessEqual(dbi['high'], dbi['hihi'])
                if propty in current_pvs:
                    self.assertEqual(dbi['unit'], unit)

    def test_ma_propty_database(self):
        """Test ma_propty_database."""
        current_pvs = TestPwrSupply.ps_alarm + \
            ('WfmData-SP', 'WfmData-RB')
        for maname, convname in TestPwrSupply.sample.items():
            if ':MA-' not in maname:
                continue
            db = pwrsupply.get_ma_propty_database(maname)
            for psname, db_ps in db.items():
                # check PS database
                unit = db_ps['Current-SP']['unit']
                for propty, dbi in db_ps.items():
                    # set setpoint limits in database
                    if propty in TestPwrSupply.ps_alarm:
                        self.assertLessEqual(dbi['lolo'], dbi['low'])
                        self.assertLessEqual(dbi['low'], dbi['lolim'])
                        self.assertLessEqual(dbi['lolim'], dbi['hilim'])
                        self.assertLessEqual(dbi['hilim'], dbi['high'])
                        self.assertLessEqual(dbi['high'], dbi['hihi'])
                    if propty in current_pvs:
                        # print(psname, propty, dbi.keys())
                        self.assertEqual(dbi['unit'], unit)
                # check MA database
                self.assertIn(convname, db_ps)
                self.assertIn(convname.replace('-SP', '-RB'), db_ps)
                self.assertIn(convname.replace('-SP', 'Ref-Mon'), db_ps)
                self.assertIn(convname.replace('-SP', '-Mon'), db_ps)
                self.assertIn('unit', db_ps[convname])
                self.assertIn('unit', db_ps[convname.replace('-SP', '-RB')])
                self.assertIn('unit',
                              db_ps[convname.replace('-SP', 'Ref-Mon')])
                self.assertIn('unit', db_ps[convname.replace('-SP', '-Mon')])

    def test_pm_propty_database(self):
        """Test pm_propty_database."""
        current_pvs = TestPwrSupply.pu_alarm
        for maname, convname in TestPwrSupply.sample.items():
            if ':PM-' not in maname:
                continue
            db = pwrsupply.get_pm_propty_database(maname)
            for psname, db_ps in db.items():
                # check PU database
                unit = db_ps['Voltage-SP']['unit']
                for propty, dbi in db_ps.items():
                    # set setpoint limits in database
                    if propty in TestPwrSupply.ps_alarm:
                        self.assertLessEqual(dbi['lolo'], dbi['low'])
                        self.assertLessEqual(dbi['low'], dbi['lolim'])
                        self.assertLessEqual(dbi['lolim'], dbi['hilim'])
                        self.assertLessEqual(dbi['hilim'], dbi['high'])
                        self.assertLessEqual(dbi['high'], dbi['hihi'])
                    if propty in current_pvs:
                        # print(psname, propty, dbi.keys())
                        self.assertEqual(dbi['unit'], unit)
                # check PM database
                self.assertIn(convname, db_ps)
                self.assertIn(convname.replace('-SP', '-RB'), db_ps)
                self.assertIn(convname.replace('-SP', '-Mon'), db_ps)
                self.assertIn('unit', db_ps[convname])
                self.assertIn('unit', db_ps[convname.replace('-SP', '-RB')])
                self.assertIn('unit', db_ps[convname.replace('-SP', '-Mon')])


if __name__ == "__main__":
    unittest.main()
