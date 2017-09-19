#!/usr/bin/env python3.6

"""Module to calculate the theoretical posang correction response matrices."""
import pyaccel as _pyaccel
import pymodels as _pymodels
import numpy as np
from math import sqrt, cos, sin


def get_respmat(self, orb):
    """Calculate and check posang correction response matrices."""
    ts, twiss_in = _pymodels.ts.create_accelerator()
    ts_m44, ts_cumul_trans_matrices = _pyaccel.tracking.find_m44(ts)

    ts_twiss, _ = _pyaccel.optics.calc_twiss(accelerator=ts,
                                             init_twiss=twiss_in)
    betax1 = ts_twiss[161].betax
    alphax1 = ts_twiss[161].alphax
    mux1 = ts_twiss[161].mux
    betay1 = ts_twiss[161].betay
    alphay1 = ts_twiss[161].alphay
    muy1 = ts_twiss[161].muy

    if orb == 'x':
        # element that corresponds to the end of 04:CH
        m_ch1 = ts_cumul_trans_matrices[128]
        m_ch12end = np.dot(ts_m44, np.linalg.inv(m_ch1))
        # element that corresponds to the end of 04:InjSF
        m_ch2 = ts_cumul_trans_matrices[158]
        m_ch22end = np.dot(ts_m44, np.linalg.inv(m_ch2))

        mat_transf_x = [0, 0, 0, 0]

        betax0 = ts_twiss[128].betax
        mux0 = ts_twiss[128].mux

        mat_transf_x[0] = m_ch12end[0, 1]
        print(mat_transf_x[0])
        print(sqrt(betax1*betax0)*sin(mux1-mux0))
        if mat_transf_x[0] == sqrt(betax1*betax0)*sin(mux1-mux0):
            print('ok element 0 matrix x')

        mat_transf_x[2] = m_ch12end[1, 1]
        print(mat_transf_x[2])
        print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))
        if mat_transf_x[2] == sqrt(betax0/betax1)*(
           cos(mux1-mux0)-alphax1*sin(mux1-mux0)):
            print('ok element 2 matrix x')

        betax0 = ts_twiss[158].betax
        mux0 = ts_twiss[158].mux

        mat_transf_x[1] = m_ch22end[0, 1]
        print(mat_transf_x[1])
        print(sqrt(betax1*betax0)*sin(mux1-mux0))
        if mat_transf_x[1] == sqrt(betax1*betax0)*sin(mux1-mux0):
            print('ok element 1 matrix x')

        mat_transf_x[3] = m_ch22end[1, 1]
        print(mat_transf_x[3])
        print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))
        if mat_transf_x[3] == sqrt(betax0/betax1)*(
           cos(mux1-mux0)-alphax1*sin(mux1-mux0)):
            print('ok element 3 matrix x')

        print(mat_transf_x)
        return mat_transf_x

    elif orb == 'y':
        # element that corresponds to the end of 04:CV-1
        m_cv1 = ts_cumul_trans_matrices[126]
        m_cv12end = np.dot(ts_m44, np.linalg.inv(m_cv1))
        # element that corresponds to the end of 04:CV-2
        m_cv2 = ts_cumul_trans_matrices[141]
        m_cv22end = np.dot(ts_m44, np.linalg.inv(m_cv2))

        mat_transf_y = [0, 0, 0, 0]

        betay0 = ts_twiss[126].betay
        muy0 = ts_twiss[126].muy

        mat_transf_y[0] = m_cv12end[2, 3]
        print(mat_transf_y[0])
        print(sqrt(betay1*betay0)*sin(muy1-muy0))
        if mat_transf_y[0] == sqrt(betay1*betay0)*sin(muy1-muy0):
            print('ok element 0 matrix y')

        mat_transf_y[2] = m_cv12end[3, 3]
        print(mat_transf_y[2])
        print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))
        if mat_transf_y[2] == sqrt(betay0/betay1)*(
           cos(muy1-muy0)-alphay1*sin(muy1-muy0)):
            print('ok element 2 matrix y')

        betay0 = ts_twiss[141].betay
        muy0 = ts_twiss[141].muy

        mat_transf_y[1] = m_cv22end[2, 3]
        print(mat_transf_y[1])
        print(sqrt(betay1*betay0)*sin(muy1-muy0))
        if mat_transf_y[1] == sqrt(betay1*betay0)*sin(muy1-muy0):
            print('ok element 1 matrix y')

        mat_transf_y[3] = m_cv22end[3, 3]
        print(mat_transf_y[3])
        print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))
        if mat_transf_y[3] == sqrt(betay0/betay1)*(
           cos(muy1-muy0)-alphay1*sin(muy1-muy0)):
            print('ok element 3 matrix y')

        print(mat_transf_y)
        return mat_transf_y


if __name__ == '__main__':
    respmatx = get_respmat('x')
    respmaty = get_respmat('y')
