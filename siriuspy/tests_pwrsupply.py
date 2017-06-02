#!/usr/bin/env python3

import unittest
from siriuspy.pwrsupply import PowerSupply

class PowerSupplyTest(unittest.TestCase):

    def setUp(self):
        self.ps = PowerSupply(psname='SI-Fam:PS-QDA')
        self.ps_enum = PowerSupply(psname='SI-Fam:PS-QDA', enum_keys=True)

        self.default_labels = self.ps.wfmlabels_mon
        self.default_labels_e = self.ps.wfmlabels_mon

    def test_initialization(self):
        self.assertEqual(self.ps.psname, 'SI-Fam:PS-QDA')
        self.assertEqual(self.ps._enum_keys, False)
        self.assertEqual(self.ps.callback, None)

    def test_initial_ctrlmode(self):
        self.assertEqual(self.ps.ctrlmode_mon, 0)
        self.assertEqual(self.ps_enum.ctrlmode_mon, 'Remote')

    def test_initial_opmode(self):
        self.assertEqual(self.ps.opmode_sel, 0)
        self.assertEqual(self.ps.opmode_sts, 0)

        self.assertEqual(self.ps_enum.opmode_sel, 'SlowRef')
        self.assertEqual(self.ps_enum.opmode_sts, 'SlowRef')

    def test_set_opmode_with_int(self):
        self.ps.opmode_sel = 1
        self.ps_enum.opmode_sel = 1

        self.assertEqual(self.ps.opmode_sel, 1)
        self.assertEqual(self.ps.opmode_sts, 1)

        self.assertEqual(self.ps_enum.opmode_sel, 'SlowRefSync')
        self.assertEqual(self.ps_enum.opmode_sts, 'SlowRefSync')

    def test_set_opmode_with_str(self):
        self.ps.opmode_sel = 'FastRef'
        self.ps_enum.opmode_sel = 'FastRef'

        self.assertEqual(self.ps.opmode_sel, 2)
        self.assertEqual(self.ps.opmode_sts, 2)

        self.assertEqual(self.ps_enum.opmode_sel, 'FastRef')
        self.assertEqual(self.ps_enum.opmode_sts, 'FastRef')

    def test_set_opmode_on_local(self):
        self.ps._ctrlmode_mon = 1 #Local mode
        self.ps.opmode_sel = 2
        self.assertEqual(self.ps.opmode_sel, 0)

    def test_reset_counter(self):
        self.assertEqual(self.ps.reset, 0)
        self.ps.reset = 2
        self.assertEqual(self.ps.reset, 1)

    def test_abort_counter(self):
        self.assertEqual(self.ps.abort, 0)
        self.ps.abort = 2
        self.assertEqual(self.ps.abort, 1)

    def test_initial_label(self):
        self.assertEqual(self.ps.wfmlabel_rb, self.default_labels[0])
        self.assertEqual(self.ps.wfmlabel_sp, self.default_labels[0])

        self.assertEqual(self.ps_enum.wfmlabel_rb, self.default_labels_e[0])
        self.assertEqual(self.ps_enum.wfmlabel_sp, self.default_labels_e[0])

    def test_set_wfmlabel(self):
        self.ps.wfmlabel_sp = 'MinhaWfm'
        self.assertEqual(self.ps.wfmlabel_rb, 'MinhaWfm')
        self.assertEqual(self.ps.wfmlabel_sp, 'MinhaWfm')
        self.ps_enum.wfmlabel_sp = 'MinhaWfm'
        self.assertEqual(self.ps_enum.wfmlabel_rb, 'MinhaWfm')
        self.assertEqual(self.ps_enum.wfmlabel_sp, 'MinhaWfm')

    def test_set_wfmlabel_on_local(self):
        self.ps._ctrlmode_mon = 1 #Local mode
        self.ps.wfmlabel_sp = 'MinhaWfm'
        self.assertEqual(self.ps.wfmlabel_rb, self.default_labels[0])
        self.assertEqual(self.ps.wfmlabel_sp, self.default_labels[0])
        self.ps_enum._ctrlmode_mon = 1 #Local mode
        self.ps_enum.wfmlabel_sp = 'MinhaWfm'
        self.assertEqual(self.ps_enum.wfmlabel_rb, self.default_labels_e[0])
        self.assertEqual(self.ps_enum.wfmlabel_sp, self.default_labels_e[0])

    def test_initial_wfmload(self):
        self.assertEqual(self.ps.wfmload_sts, 0)
        self.assertEqual(self.ps.wfmload_sel, 0)
        self.assertEqual(self.ps_enum.wfmload_sts, self.default_labels_e[0])
        self.assertEqual(self.ps_enum.wfmload_sel, self.default_labels_e[0])

    def test_set_wfmload(self):
        self.ps.wfmload_sel = 2
        self.assertEqual(self.ps.wfmload_sts, 2)
        self.assertEqual(self.ps.wfmload_sel, 2)
        self.assertEqual(self.ps.wfmlabel_rb, self.default_labels[2])
        self.ps.wfmload_sel = 0
        self.assertEqual(self.ps.wfmload_sts, 0)
        self.assertEqual(self.ps.wfmload_sel, 0)
        target_label = self.default_labels_e[5]
        self.ps_enum.wfmload_sel = target_label
        self.assertEqual(self.ps_enum.wfmload_sts, target_label)
        self.assertEqual(self.ps_enum.wfmload_sel, target_label)
        self.assertEqual(self.ps_enum.wfmlabel_rb, target_label)

    def test_set_wfmload_notint_error(self):
        ''' Test if a ValueError exception is risen when enum_keys=False and
            trying to set index without an int
        '''
        with self.assertRaises(ValueError):
            self.ps.wfmload_sel = self.default_labels_e[4]

    def test_set_wfmload_notstr_error(self):
        ''' Test if a ValueError exception is risen when enum_keys=True and
            trying to set index without a string
        '''
        with self.assertRaises(ValueError):
            self.ps_enum.wfmload_sel = 4

    def test_set_wfmload_label_not_found_error(self):
        ''' Test if a KeyError exception is risen when enum_keys=True and
            trying to set index with a waveform that is not defined
        '''
        with self.assertRaises(KeyError):
            self.ps_enum.wfmload_sel = 'randomstring'

    def test_wfmsave_counter(self):
        self.assertEqual(self.ps.wfmsave_cmd, 0)
        self.ps.wfmsave_cmd = 5
        self.assertEqual(self.ps.wfmsave_cmd, 1)

    def test_set_wfmdata(self):
        self.ps.wfmdata_sp = list(range(2000))

        for i, value in enumerate(self.ps.wfmdata_rb):
            self.assertEqual(i, value)

    def test_wfmsave_label(self):
        idx_changed = 2
        old_label_name = self.default_labels[2]
        new_label_name = 'TestWfm'

        self.ps.wfmload_sel = idx_changed
        self.ps.wfmlabel_sp = new_label_name
        self.ps.wfmsave_cmd = 1
        del self.ps
        self.ps = PowerSupply(psname='SI-Fam:PS-QDA')

        labels = self.ps.wfmlabels_mon
        self.assertEqual(labels[idx_changed], new_label_name)

        self.ps.wfmload_sel = idx_changed
        self.ps.wfmlabel_sp = old_label_name
        self.ps.wfmsave_cmd = 1
        del self.ps
        self.ps = PowerSupply(psname='SI-Fam:PS-QDA')

        self.assertEqual(self.default_labels[idx_changed], old_label_name)

    '''def test_wfmsave_label(self):
        idx_changed = 2
        self.ps.wfmload_sel = idx_changed
        old_data = self.ps.wfmdata_rb
        new_data = list(range(2000))

        self.ps.wfmdata_sp = new_data
        self.ps.wfmsave_cmd
        del self.ps
        self.ps = PowerSupply(psname='SI-Fam:PS-QDA')

        self.ps.wfmload_sel = idx_changed
        self.assertEqual(True, (self.ps.wfmdata_rb == new_data).all())

        self.ps.wfmdata_sp = old_data
        self.ps.wfmsave_cmd
        del self.ps
        self.ps = PowerSupply(psname='SI-Fam:PS-QDA')

        self.ps.wfmload_sel = idx_changed
        self.assertEqual(True, (self.ps.wfmdata_rb == old_data).all())'''




    def test_initial_label_wfmindex(self):
        self.assertEqual(self.ps.wfmindex_mon, 0)
        self.assertEqual(self.ps_enum.wfmindex_mon, 0)
if __name__ == '__main__':
    unittest.main()
