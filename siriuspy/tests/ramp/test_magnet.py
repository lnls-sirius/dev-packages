#!/usr/bin/env python-sirius
"""Magnet class test module."""

import unittest
from siriuspy import util
from siriuspy.ramp import magnet
import siriuspy.search as _search


public_interface = (
    'Magnet',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                magnet,
                public_interface)
        self.assertTrue(valid)


class TestMagnet(unittest.TestCase):
    """TestMagnet."""

    class Modules:
        """Modules class."""

        pass

    ps_manames = _search.MASearch.get_pwrsupply_manames()
    conv_maname_2_splims = _search.MASearch.conv_maname_2_splims

    manames = (
        'SI-Fam:MA-B1B2',
        'SI-Fam:MA-QDA',
        'SI-Fam:MA-QDB1',
        'SI-Fam:MA-QDB2',
        'SI-Fam:MA-QDP1',
        'SI-Fam:MA-QDP2',
        'SI-Fam:MA-QFA',
        'SI-Fam:MA-Q1',
        'SI-Fam:MA-Q2',
        'SI-Fam:MA-Q3',
        'SI-Fam:MA-Q4',
        'SI-Fam:MA-QFB',
        'SI-Fam:MA-QFP',
        'SI-Fam:MA-SFA0',
        'SI-Fam:MA-SFA1',
        'SI-Fam:MA-SFA2',
        'SI-Fam:MA-SFB0',
        'SI-Fam:MA-SFB1',
        'SI-Fam:MA-SFB2',
        'SI-Fam:MA-SFP0',
        'SI-Fam:MA-SFP1',
        'SI-Fam:MA-SFP2',
        'SI-Fam:MA-SDA0',
        'SI-Fam:MA-SDA1',
        'SI-Fam:MA-SDA2',
        'SI-Fam:MA-SDA3',
        'SI-Fam:MA-SDB0',
        'SI-Fam:MA-SDB1',
        'SI-Fam:MA-SDB2',
        'SI-Fam:MA-SDB3',
        'SI-Fam:MA-SDP0',
        'SI-Fam:MA-SDP1',
        'SI-Fam:MA-SDP2',
        'SI-Fam:MA-SDP3',
        'TS-Fam:MA-B',
        'BO-Fam:MA-B',
        'BO-Fam:MA-QD',
        'BO-Fam:MA-QF',
        'BO-Fam:MA-SD',
        'BO-Fam:MA-SF',
        'TB-Fam:MA-B',
        'SI-01M1:MA-QDA',
        'SI-02M1:MA-QDB1',
        'SI-02M1:MA-QDB2',
        'SI-03M1:MA-QDP1',
        'SI-03M1:MA-QDP2',
        'SI-19M2:MA-QDP2',
        'SI-09M2:MA-QFA',
        'SI-18C1:MA-Q1',
        'SI-17C1:MA-Q2',
        'SI-08C3:MA-Q3',
        'SI-11C2:MA-Q4',
        'SI-06M2:MA-QFB',
        'SI-07M2:MA-QFP',
        'SI-07C2:MA-CH',
        'SI-01C1:MA-CV',
        'SI-01C2:MA-CV-1',
        'SI-01C3:MA-CV-2',
        'SI-02C3:MA-CV-1',
        'SI-08C2:MA-CV-1',
        'SI-08C3:MA-CV-1',
        'SI-09C1:MA-CV',
        'SI-05C1:MA-QS',
        'SI-13C3:MA-QS',
        'SI-01C2:MA-CV-2',
        'SI-01M1:MA-FCH',
        'SI-09M1:MA-FCH',
        'SI-04C3:MA-FCV',
        'BO-02D:MA-QS',
        'BO-29U:MA-CH',
        'BO-07U:MA-CV',
        'TB-01:MA-QD1',
        'TB-01:MA-QF1',
        'TB-02:MA-QD2A',
        'TB-02:MA-QF2A',
        'TB-02:MA-QF2B',
        'TB-02:MA-QD2B',
        'TB-03:MA-QF3',
        'TB-03:MA-QD3',
        'TB-04:MA-QF4',
        'TB-04:MA-QD4',
        'TB-01:MA-CH-1',
        'TB-01:MA-CH-2',
        'TB-03:MA-CH',
        'TB-01:MA-CV-1',
        'TB-01:MA-CV-2',
        'TB-02:MA-CV-1',
        'TS-01:MA-QF1A',
        'TS-01:MA-QF1B',
        'TS-02:MA-QD2',
        'TS-04:MA-QD4A',
        'TS-04:MA-QD4B',
        'TS-02:MA-QF2',
        'TS-03:MA-QF3',
        'TS-04:MA-QF4',
        'TS-04:MA-CH',
        'TS-01:MA-CV-1',
        'TS-01:MA-CV-2',
        'TS-02:MA-CV',
        'TS-04:PM-InjSeptG-1',
        'TS-04:PM-InjSeptG-2',
        'TS-04:PM-InjSeptF',
        'TS-01:PM-EjeSeptG',
        'TS-01:PM-EjeSeptF',
        'BO-01D:PM-InjKckr',
        'BO-48D:PM-EjeKckr',
        'TB-04:PM-InjSept',
        'SI-01SA:PM-InjDpKckr',
        'SI-01SA:PM-InjNLKckr',
        'SI-01SA:PM-PingH',
        'SI-19C4:PM-PingV',
    )

    def setUp(self):
        """Setup method."""
        import siriuspy.ramp.magnet as _mod
        self.modules = TestMagnet.Modules()
        self.modules.magnet = _mod

    def test_constructor(self):
        """Test create magnets.

        - Create a magnet for each maname in MASearchs.get_manames().
        """
        for maname in TestMagnet.manames:
            magnet = self.modules.magnet.Magnet(maname=maname)
            splims = TestMagnet.conv_maname_2_splims(maname)
            self.assertEqual(magnet.maname, maname)
            self.assertEqual(magnet.current_max, splims['DRVH'])
            self.assertEqual(magnet.current_min, splims['DRVL'])
            self.assertIn(magnet.dipole_name, (None,
                                               'SI-Fam:MA-B1B2',
                                               'BO-Fam:MA-B',
                                               'TB-Fam:MA-B',
                                               'TS-Fam:MA-B'))

    def test_conversions(self):
        """Test conversion current 2 strength."""
        for maname in TestMagnet.manames:
            if 'PM-' in maname:
                print('test_conversions: skipping {} ...'.format(maname))
                continue
            magnet = self.modules.magnet.Magnet(maname=maname)
            splims = TestMagnet.conv_maname_2_splims(maname)
            currents1 = list(splims.values())
            strengths = magnet.conv_current_2_strength(
                currents1,
                strengths_dipole=3.0,
                strengths_family=1.0)
            currents2 = magnet.conv_strength_2_current(
                strengths,
                strengths_dipole=3.0,
                strengths_family=1.0)
            for i in range(len(currents1)):
                self.assertAlmostEqual(currents1[i], currents2[i])


if __name__ == "__main__":
    unittest.main()
