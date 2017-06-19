import unittest
import time
import math
from siriuspy.magnet.model import PowerSupplyMA

''' VACA and si-fam-ma must be running '''

class PowerSupplyMATest(unittest.TestCase):

    def setUp(self):
        time.sleep(1)
        self.strengths = [1.5, -0.6, -1.2, 0.06, -0.0005]

        self.ma_set = [
            dict(
                input='SI-Fam:MA-B1B2', #ma name
                output= {
                    'magfunc':'dipole',
                    'strth_class':'MAStrengthDip',
                    'controller':['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
                }
            ),
            dict(
                input='SI-Fam:MA-QDA', #ma name
                output= {
                    'magfunc':'quadrupole',
                    'strth_class':'MAStrength',
                    'controller':['SI-Fam:PS-QDA']
                }
            ),
            dict(
                input='SI-Fam:MA-SDB0', #ma name
                output= {
                    'magfunc':'sextupole',
                    'strth_class':'MAStrength',
                    'controller':['SI-Fam:PS-SDB0']
                }
            ),
            dict(
                input='SI-01M2:MA-QFA',
                output= {
                    'magfunc':'quadrupole',
                    'strth_class':'MAStrengthTrim',
                    'controller':['SI-01M2:PS-QFA']
                }
            ),
            dict(
                input='SI-01C2:MA-CV-2',
                output= {
                    'magfunc':'corrector-vertical',
                    'strth_class':'MAStrength',
                    'controller':['SI-01C2:PS-CV-2']
                }
            )
        ]
        '''dict(
                input='SI-16C2:MA-QS',
                output= {
                    'magfunc':'quadrupole-skew',
                    'strth_class':'_StrthMA',
                    'controller':['SI-16C2:PS-QS']
                }
            ),
        ]'''

        self.ioc_list = list()
        for ma in self.ma_set:
            self.ioc_list.append(PowerSupplyMA(ma['input'], True))
            self.ioc_list[-1].pwrstate_sel = 1

    def test_strth_class(self):
        for i, ma in enumerate(self.ma_set):
            classname = self.ioc_list[i]._strobj.__class__.__name__
            self.assertEqual(classname, ma['output']['strth_class'])

    def test_controller(self):
        for i, ma in enumerate(self.ma_set):
            self.assertEqual(self.ioc_list[i]._psnames, ma['output']['controller'])

    def test_magfunc(self):
        for i, ma in enumerate(self.ma_set):
            self.assertEqual(self.ioc_list[i].magfunc, ma['output']['magfunc'])

    def test_get_strength_sp(self):
        time.sleep(1)
        for i, ma in enumerate(self.ma_set):
            self.assertEqual(type(self.ioc_list[i].strength_sp), float)

    def test_set_strength_sp(self):
        strengths = self.strengths
        for i, ma in enumerate(self.ma_set):
            init_strth = self.ioc_list[i].strength_sp
            self.ioc_list[i].strength_sp = strengths[i]
            #self.assertEqual(math.fabs(self.ioc_list[0].strength_sp - init_strth - 0.1), 0.1)
            self.assertEqual(math.fabs(self.ioc_list[i].strength_sp - strengths[i]) < 0.000001, True)

    def test_read_strength(self):
        strengths = self.strengths
        for i, ma in enumerate(self.ma_set):
            self.ioc_list[i].strength_sp = strengths[i]
            time.sleep(1)
            self.assertEqual(math.fabs(self.ioc_list[i].strength_rb - strengths[i]) < 0.000001, True)
            self.assertEqual(math.fabs(self.ioc_list[i].strengthref_mon - strengths[i]) < 0.000001, True)
            self.assertEqual(math.fabs(self.ioc_list[i].strength_mon - strengths[i]) < 0.000001, True)


if __name__ == "__main__":
    unittest.main()
