#!/usr/bin/env python3.6

"""Module to calculate the theoretical posang correction response matrices."""
import pyaccel as _pyaccel
import pymodels as _pymodels
import numpy as np
from math import sqrt, cos, sin


def get_ts_respmat(orb):
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

        mat_transf_x[2] = m_ch12end[1, 1]
        print(mat_transf_x[2])
        print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))

        betax0 = ts_twiss[158].betax
        mux0 = ts_twiss[158].mux

        mat_transf_x[1] = m_ch22end[0, 1]
        print(mat_transf_x[1])
        print(sqrt(betax1*betax0)*sin(mux1-mux0))

        mat_transf_x[3] = m_ch22end[1, 1]
        print(mat_transf_x[3])
        print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))

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

        mat_transf_y[2] = m_cv12end[3, 3]
        print(mat_transf_y[2])
        print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))

        betay0 = ts_twiss[141].betay
        muy0 = ts_twiss[141].muy

        mat_transf_y[1] = m_cv22end[2, 3]
        print(mat_transf_y[1])
        print(sqrt(betay1*betay0)*sin(muy1-muy0))

        mat_transf_y[3] = m_cv22end[3, 3]
        print(mat_transf_y[3])
        print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))

        print(mat_transf_y)
        return mat_transf_y


def get_tb_respmat(orb):
    """Calculate and check posang correction response matrices."""
    tb, twiss_in = _pymodels.tb.create_accelerator()
    tb_m44, tb_cumul_trans_matrices = _pyaccel.tracking.find_m44(tb)

    tb_twiss, _ = _pyaccel.optics.calc_twiss(accelerator=tb,
                                             init_twiss=twiss_in)
    betax1 = tb_twiss[136].betax
    alphax1 = tb_twiss[136].alphax
    mux1 = tb_twiss[136].mux
    betay1 = tb_twiss[136].betay
    alphay1 = tb_twiss[136].alphay
    muy1 = tb_twiss[136].muy

    if orb == 'x':
        # element that corresponds to the end of 04:CH
        m_ch1 = tb_cumul_trans_matrices[110]
        m_ch12end = np.dot(tb_m44, np.linalg.inv(m_ch1))
        # element that corresponds to the end of 04:InjSF
        m_ch2 = tb_cumul_trans_matrices[135]
        m_ch22end = np.dot(tb_m44, np.linalg.inv(m_ch2))

        mat_transf_x = [0, 0, 0, 0]

        betax0 = tb_twiss[110].betax
        mux0 = tb_twiss[110].mux

        mat_transf_x[0] = m_ch12end[0, 1]
        print(mat_transf_x[0])
        print(sqrt(betax1*betax0)*sin(mux1-mux0))

        mat_transf_x[2] = m_ch12end[1, 1]
        print(mat_transf_x[2])
        print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))

        betax0 = tb_twiss[135].betax
        mux0 = tb_twiss[135].mux

        mat_transf_x[1] = m_ch22end[0, 1]
        print(mat_transf_x[1])
        print(sqrt(betax1*betax0)*sin(mux1-mux0))

        mat_transf_x[3] = m_ch22end[1, 1]
        print(mat_transf_x[3])
        print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))

        print(mat_transf_x)
        return mat_transf_x

    elif orb == 'y':
        # element that corresponds to the end of 04:CV-1
        m_cv1 = tb_cumul_trans_matrices[115]
        m_cv12end = np.dot(tb_m44, np.linalg.inv(m_cv1))
        # element that corresponds to the end of 04:CV-2
        m_cv2 = tb_cumul_trans_matrices[131]
        m_cv22end = np.dot(tb_m44, np.linalg.inv(m_cv2))

        mat_transf_y = [0, 0, 0, 0]

        betay0 = tb_twiss[115].betay
        muy0 = tb_twiss[115].muy

        mat_transf_y[0] = m_cv12end[2, 3]
        print(mat_transf_y[0])
        print(sqrt(betay1*betay0)*sin(muy1-muy0))

        mat_transf_y[2] = m_cv12end[3, 3]
        print(mat_transf_y[2])
        print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))

        betay0 = tb_twiss[131].betay
        muy0 = tb_twiss[131].muy

        mat_transf_y[1] = m_cv22end[2, 3]
        print(mat_transf_y[1])
        print(sqrt(betay1*betay0)*sin(muy1-muy0))

        mat_transf_y[3] = m_cv22end[3, 3]
        print(mat_transf_y[3])
        print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))

        print(mat_transf_y)
        return mat_transf_y


if __name__ == '__main__':
    ts_respmatx = get_ts_respmat('x')
    ts_respmaty = get_ts_respmat('y')
    tb_respmatx = get_tb_respmat('x')
    tb_respmaty = get_tb_respmat('y')
