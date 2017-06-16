#!/usr/bin/env python3

import unittest
import time
import siriuspy.pwrsupply
from siriuspy.pwrsupply import PowerSupply
from siriuspy.csdevice.enumtypes import EnumTypes as _et

class TestControllerSim(unittest.TestCase):

    def setUp(self):
        self.curr_min = 0; self.curr_max = 10.0; self.curr_std = 0.1
        self.psname = 'SI-Fam:PS-QDA'
        self.c = siriuspy.pwrsupply.ControllerSim(psname=self.psname,
                                                  current_min=self.curr_min,
                                                  current_max=self.curr_max,
                                                  current_std=self.curr_std,
                                                  random_seed=131071)

    def test_constructor(self):
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.pwrstate, _et.idx.Off)
        self.assertEqual(self.c.reset_counter, 0)
        self.assertEqual(self.c.abort_counter, 0)
        self.assertEqual(self.c.intlk, 0)
        self.assertEqual(self.c.current_min, self.curr_min)
        self.assertEqual(self.c.current_max, self.curr_max)
        self.assertEqual(self.c.current_sp, 0.0)
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load, -0.01262415230153511)
        c1 = self.c.current_load; c2 = self.c.current_load; self.assertEqual(c1, c2)
        self.assertEqual(self.c.trigger_timed_out, False)
        self.assertEqual(self.c.connected, True)
        self.assertEqual(self.c.psname, self.psname)

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

    def test_slowrefsync(self):
        self.c.pwrstate = _et.idx.On
        self.c.opmode = _et.idx.SlowRefSync
        self.c.current_sp = 5.0
        self.assertEqual(self.c.current_sp, 5.0)
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load, 0.16835556870840707)
        self.c.trigger_signal()
        self.assertEqual(self.c.current_ref, 5.0)
        self.assertEqual(self.c.current_load, 4.92736857786351)
        self.c.pwrstate = _et.idx.Off
        self.assertEqual(self.c.current_ref, 0.0)
        self.assertEqual(self.c.current_load, 0.051885885594204234)

    def test_fastref(self):
        self.c.pwrstate = _et.idx.On
        self.c.current_sp = 6.0
        self.c.opmode = _et.idx.FastRef
        self.c.fofb_signal(current=2.3)
        self.assertEqual(self.c.current_sp, 6.0)
        self.assertEqual(self.c.current_ref, 2.3)
        self.assertEqual(self.c.current_load, 2.468355568708407)
        self.c.opmode = _et.idx.SlowRef
        self.assertEqual(self.c.current_sp, 2.3)
        self.assertEqual(self.c.current_ref, 2.3)
        self.assertEqual(self.c.current_load, 2.2273685778635097)

    def test_abort(self):
        # slowref
        self.c.pwrstate = _et.idx.On
        self.c.current_sp = 5.0;
        self.c.abort()
        self.assertEqual(self.c.abort_counter, 1)
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.current_ref, 5.0)
        self.assertEqual(self.c.current_load, 5.168355568708407)
        self.c.abort()
        self.assertEqual(self.c.abort_counter, 2)
        # slowrefsync
        self.c.opmode = _et.idx.SlowRefSync
        self.c.current_sp = 6.0;
        self.assertEqual(self.c.current_ref, 5.0)
        self.c.abort()
        self.assertEqual(self.c.abort_counter, 3)
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.current_ref, 5.0)
        self.assertEqual(self.c.current_load, 4.9961906072664135)
        # FastRef
        self.c.opmode = _et.idx.FastRef
        self.c.fofb_signal(current=2.3)
        self.assertEqual(self.c.current_sp, 5.0)
        self.assertEqual(self.c.current_ref, 2.3)
        self.assertEqual(self.c.current_load, 2.480846501874249)
        self.c.current_sp = 6.0;
        self.assertEqual(self.c.current_sp, 6.0)
        self.assertEqual(self.c.current_ref, 2.3)
        self.assertEqual(self.c.current_load, 2.480846501874249)
        self.c.abort()
        self.assertEqual(self.c.abort_counter, 4)
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.current_sp, 2.3)
        self.assertEqual(self.c.current_ref, 2.3)
        self.assertEqual(self.c.current_load, 2.3202635989599303)
        # RmpWfm
        self.c.trigger_timeout = 10000
        self.assertEqual(self.c.trigger_timeout, 10000)
        self.c.opmode = _et.idx.RmpWfm
        self.c.wfmdata = [3.0 for _ in self.c.wfmdata]
        self.assertEqual(self.c.wfmindex, 0)
        self.c.trigger_signal()
        self.assertEqual(self.c.current_sp, 2.3)
        self.assertEqual(self.c.current_ref, 3.0)
        self.assertEqual(self.c.current_load, 2.9610465471411977)
        self.assertEqual(self.c.wfmindex, 1)
        self.c.abort()
        self.assertEqual(self.c.abort_counter, 5)
        self.assertEqual(self.c.opmode, _et.idx.RmpWfm)
        self.assertEqual(self.c.current_sp, 2.3)
        self.assertEqual(self.c.current_ref, 3.0)
        self.assertEqual(self.c.current_load, 3.0318294687025196)
        for _ in range(2000): self.c.trigger_signal()
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.current_sp, 3.0)
        self.assertEqual(self.c.current_ref, 3.0)
        self.assertEqual(self.c.current_load, 2.9474178499604298)
        # MigWfm
        self.c.current_sp = 6.0;
        self.c.trigger_timeout = 0.002
        self.assertEqual(self.c.trigger_timeout, 0.002)
        self.c.opmode = _et.idx.MigWfm
        self.c.wfmdata = [3.0 for _ in self.c.wfmdata]
        self.assertEqual(self.c.wfmindex, 0)
        self.assertEqual(self.c.current_sp, 6.0)
        self.assertEqual(self.c.current_ref, 6.0)
        self.assertEqual(self.c.current_load, 6.071851076253223)
        self.c.abort()
        self.assertEqual(self.c.abort_counter, 6)
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.current_sp, 6.0)
        self.assertEqual(self.c.current_ref, 6.0)
        self.assertEqual(self.c.current_load, 6.036233653133654)
        self.c.opmode = _et.idx.MigWfm
        self.c.trigger_signal(nrpts=2000)
        self.assertEqual(self.c.wfmindex, 0)
        self.assertEqual(self.c.opmode, _et.idx.SlowRef)
        self.assertEqual(self.c.current_sp, 3.0)
        self.assertEqual(self.c.current_ref, 3.0)
        self.assertEqual(self.c.current_load, 2.8706911712729086)



if __name__ == '__main__':
    unittest.main()
