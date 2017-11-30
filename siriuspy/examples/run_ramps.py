#!/usr/bin/env python-sirius

from siriuspy.ramp.waveform import Waveform
import numpy as np
import matplotlib.pyplot as plt
import numpy as np



def test1():
    w = Waveform()
    w0 = [0*0.1 + v for v in w.waveform]
    print('w0: ', w.i07)
    # w.change_plateau(w.v34+0.1)
    # w.change_ramp_up(i1=w.i1, i2=w.i2-500, v1=w.v1, v2=w.v2)
    w.change_ramp_down(i6=w.i6-100)
    w1 = [0*0.2 + v for v in w.waveform]

    # w = Waveform()
    # w.change_ramp_down(i6=w.i6-100)
    # w2 = [0*0.3 + v for v in w.waveform]
    print('w1: ', w.i07)

    plt.plot(w0, '.')
    plt.plot(w1, '.')
    # plt.plot(w2)
    plt.show()


test1()
