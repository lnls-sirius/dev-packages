#!/usr/bin/env python-sirius
"""Magnet class test module."""

from unittest import TestCase
from siriuspy import util
from siriuspy.ramp import magnet


public_interface = (
    'get_magnet',
    'Magnet',
)


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                magnet,
                public_interface)
        self.assertTrue(valid)


class TestMagnet(TestCase):
    """TestMagnet."""

    class Modules:
        """Modules class."""

        pass

    # ps_manames = _search.MASearch.get_pwrsupply_manames()
    # conv_maname_2_splims = _search.MASearch.conv_maname_2_splims

    data = {
        'SI-Fam:MA-B1B2':
            {'DRVH': 405.0,
             'DRVL': 0.0,
             'HIGH': 405.0,
             'HIHI': 405.0,
             'HOPR': 400.0,
             'LOLO': 0.0,
             'LOPR': 0.0,
             'LOW': 0.0,
             'TSTR': 0.5,
             'TSTV': 394.0},
        'SI-Fam:MA-QDA': {},
        'SI-Fam:MA-QDB1': {},
        'SI-Fam:MA-QFA': {},
        'SI-Fam:MA-Q1': {},
        'SI-Fam:MA-QFB': {},
        'SI-Fam:MA-QFP': {},
        'SI-Fam:MA-SFA0': {},
        'SI-Fam:MA-SFP1': {},
        'SI-Fam:MA-SDA0': {},
        'SI-Fam:MA-SDP0': {},
        'TS-Fam:MA-B': {},
        'BO-Fam:MA-B': {},
        'BO-Fam:MA-QD': {},
        'BO-Fam:MA-QF': {},
        'BO-Fam:MA-SD': {},
        'BO-Fam:MA-SF': {},
        'TB-Fam:MA-B': {},
        'SI-01M1:MA-QDA': {},
        'SI-17C1:MA-Q2': {},
        'SI-07C2:MA-CH': {},
        'SI-01C1:MA-CV': {},
        'SI-01C2:MA-CV-1': {},
        'SI-05C1:MA-QS': {},
        'SI-09M1:MA-FCH': {},
        'SI-04C3:MA-FCV': {},
        'BO-02D:MA-QS': {},
        'BO-29U:MA-CH': {},
        'BO-07U:MA-CV': {},
        'TB-01:MA-QD1': {},
        'TB-02:MA-QD2A': {},
        'TB-01:MA-CH-1': {},
        'TB-03:MA-CH': {},
        'TB-01:MA-CV-1': {},
        'TS-01:MA-QF1A': {},
        'TS-02:MA-QD2': {},
        'TS-02:MA-QF2': {},
        'TS-04:MA-CH': {},
        'TS-01:MA-CV-1': {},
        'TS-04:PM-InjSeptG-1': {},
        'TS-04:PM-InjSeptG-2': {},
        'TS-04:PM-InjSeptF': {},
        'TS-01:PM-EjeSeptG': {},
        'TS-01:PM-EjeSeptF': {},
        'BO-01D:PM-InjKckr': {},
        'BO-48D:PM-EjeKckr': {},
        'TB-04:PM-InjSept': {},
        'SI-01SA:PM-InjDpKckr': {},
        'SI-01SA:PM-InjNLKckr': {},
        'SI-01SA:PM-PingH': {},
        'SI-19C4:PM-PingV': {},
    }

    def setUp(self):
        """Setup method."""
        import siriuspy.ramp.magnet as _mod
        self.modules = TestMagnet.Modules()
        self.modules.magnet = _mod

        # search_patcher = mock.patch(
        #     'siriuspy.ramp.magnet._MAData', autospec=True)
        # self.addCleanup(search_patcher.stop)
        # self.mock = search_patcher.start()
        # self.mock.return_value.magfunc.return_value = 'dipole'
        # self.mock.conv_maname_2_splims.return_value = \
        #     {'DRVH': 405.0,
        #      'DRVL': 0.0,
        #      'HIGH': 405.0,
        #      'HIHI': 405.0,
        #      'HOPR': 400.0,
        #      'LOLO': 0.0,
        #      'LOPR': 0.0,
        #      'LOW': 0.0,
        #      'TSTR': 0.5,
        #      'TSTV': 394.0}
        # self.mock.get_splims_unit.return_value = ['A', 'Ampere']

    public_interface = (
        'maname',
        'section',
        'dipole_name',
        'family_name',
        'magfunc',
        'strength_label',
        'strength_units',
        'current_min',
        'current_max',
        'splims',
        'conv_current_2_strength',
        'conv_strength_2_current'
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                magnet.Magnet,
                TestMagnet.public_interface)
        self.assertTrue(valid)

    def _test_constructor(self):
        """Test create magnets.

        - Create a magnet for each maname in MASearchs.get_manames().
        """
        # TODO: use mocking!!!
        for maname, data in TestMagnet.data.items():
            magnet = self.modules.magnet.Magnet(maname=maname)
            self.assertEqual(magnet.maname, maname)
            self.assertIn(magnet.dipole_name, (None,
                                               'SI-Fam:MA-B1B2',
                                               'BO-Fam:MA-B',
                                               'TB-Fam:MA-B',
                                               'TS-Fam:MA-B'))
            # if data:
            #     splims = data
            #     self.assertEqual(magnet.current_max, splims['DRVH'])
            #     self.assertEqual(magnet.current_min, splims['DRVL'])

    def _test_conversions(self):
        """Test conversion current 2 strength."""
        # TODO: use mocking!!!
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
