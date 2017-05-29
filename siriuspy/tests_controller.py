#!/usr/bin/env python3

import unittest
import siriuspy.pwrsupply
from siriuspy.csdevice.enumtypes import EnumTypes as _et

class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.curr_min = 0; self.curr_max = 10.0; self.curr_std = 0.1
        self.c = siriuspy.pwrsupply.ControllerSim(current_min=self.curr_min,
                                                  current_max=self.curr_max,
                                                  current_std=self.curr_std,
                                                  random_seed=131071)

    def test_constructor(self):
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.pwrstate, _et.idx.Off)
        self.assertEqual(self.c.reset_counter, 0)
        self.assertEqual(self.c.current_min, self.curr_min)
        self.assertEqual(self.c.current_max, self.curr_max)
        self.assertEqual(self.c.current_sp, 0.0)
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load, -0.01262415230153511)
        c1 = self.c.current_load; c2 = self.c.current_load; self.assertEqual(c1, c2)
        self.assertEqual(self.c.trigger_timed_out, False)

    def test_pwrstate_off(self):
        self.c.current_sp = 10.0
        self.assertEqual(self.c.current_sp, 10.0)
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load, -0.05711411364691349)

    def test_pwrstate_on(self):
        self.c.current_sp = 10.0
        self.c.pwrstate = 1
        self.assertEqual(self.c.current_sp, 10.0)
        self.assertEqual(self.c.current_ref, 10.0)
        self.assertEqual(self.c.current_load,10.039223131824139)
        self.c.pwrstate = 0
        self.assertEqual(self.c.current_sp, 10.0)
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load,0.16835556870840707)

    def test_current_limits(self):
        self.c.pwrstate = _et.idx.On
        self.c.current_sp = 20.0
        self.assertEqual(self.c.current_sp, 20.0)
        self.assertEqual(self.c.current_ref, self.curr_max)
        self.assertEqual(self.c.current_load, 10.039223131824139)

    def test_sp_change2slowref(self):
        self.c.wfmdata = [5.0 for _ in range(len(self.c.wfmdata))]
        self.c.opmode = _et.idx.RmpWfm
        self.c.trigger_signal()
        self.c.trigger_signal()
        self.c.trigger_signal()
        self.assertEqual(self.c.wfmindex, 3)
        self.assertEqual(self.c.current_sp, 0.0)
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load,0.051885885594204234)
        self.c._set_wfmindex(10)
        self.c.pwrstate = _et.idx.On
        self.assertEqual(self.c.current_sp, 0.0)
        self.assertEqual(self.c.current_ref, 5.0)
        self.assertEqual(self.c.current_load, 5.052973467000613)
        self.c.opmode = _et.idx.SlowRef
        self.assertEqual(self.c.current_sp, 5.0)



if __name__ == '__main__':
    unittest.main()
