import unittest
from siriuspy.magnet.model import PowerSupplyMA

''' VACA and si-fam-ma must be running '''

class PowerSupplyMATest(unittest.TestCase):

    def setUp(self):

        self.ma_set = [
            dict(
                input='SI-Fam:MA-B1B2', #ma name
                output= {
                    'magfunc':'dipole',
                    'strth_class':'StrthMADip',
                    'controller':['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
                }
            ),
            dict(
                input='SI-Fam:MA-QDA', #ma name
                output= {
                    'magfunc':'quadrupole',
                    'strth_class':'_StrthMAFam',
                    'controller':['SI-Fam:PS-QDA']
                }
            ),
            dict(
                input='SI-Fam:MA-SDB0', #ma name
                output= {
                    'magfunc':'sextupole',
                    'strth_class':'_StrthMAFam',
                    'controller':['SI-Fam:PS-SDB0']
                }
            ),
            dict(
                input='SI-01M2:MA-QFA',
                output= {
                    'magfunc':'quadrupole',
                    'strth_class':'_StrthMATrim',
                    'controller':['SI-01M2:PS-QFA']
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
            dict(
                input='SI-01C2:MA-CV-2',
                output= {
                    'magfunc':'corrector-vertical',
                    'strth_class':'_StrthMA',
                    'controller':['SI-01C2:PS-CV-2']
                }
            )
        ]'''

        self.ioc_list = list()
        for ma in self.ma_set:
            self.ioc_list.append(PowerSupplyMA(ma['input'], True, 'VAG-'))

    def test_strth_class(self):
        for i, ma in enumerate(self.ma_set):
            classname = self.ioc_list[i]._strobj.__class__.__name__
            self.assertEqual(classname, ma['output']['strth_class'])

    def test_controller(self):
        for i, ma in enumerate(self.ma_set):
            self.assertEqual(self.ioc_list[i]._psname, ma['output']['controller'])

    def test_magfunc(self):
        for i, ma in enumerate(self.ma_set):
            self.assertEqual(self.ioc_list[i].magfunc, ma['output']['magfunc'])

    def test_get_strength_sp(self):
        for i, ma in enumerate(self.ma_set):
            self.assertEqual(type(self.ioc_list[i].strength_sp), float)

    def test_set_strength_sp(self):
        for i, ma in enumerate(self.ma_set):
            init_strth = self.ioc_list[i].strength_sp
            self.ioc_list[i].strength_sp = init_strth + 1.0
            self.assertEqual(self.ioc_list[i].strength_sp, (init_strth + 1.0))

    def test_read_strength(self):
        for i, ma in enumerate(self.ma_set):
            init_strth = self.ioc_list[i].strength_sp
            self.ioc_list[i].strength_sp = init_strth + 1.0
            self.assertEqual(self.ioc_list[i].strength_rb, (init_strth + 1.0))
            self.assertEqual(self.ioc_list[i].strengthref_mon, (init_strth + 1.0))
            self.assertEqual(self.ioc_list[i].strength_mon, (init_strth + 1.0))
