#!/usr/bin/env python3.6

"""Module to calculate the theoretical posang correction response matrices."""
import pyaccel as _pyaccel
import pymodels as _pymodels
import numpy as np
# from math import sqrt, cos, sin, isclose


def get_respmat(tl, orb):
    """Calculate and check posang correction response matrices."""
    if tl == 'tb':
        tl, twiss_in = _pymodels.tb.create_accelerator()
        ch1_idx = 110
        ch2_idx = 135
        cv1_idx = 115
        cv2_idx = 131
        # end_index = 136

    elif tl == 'ts':
        tl, twiss_in = _pymodels.ts.create_accelerator()
        ch1_idx = 128
        ch2_idx = 158
        cv1_idx = 126
        cv2_idx = 141
        # end_index = 161

    tl_m44, tl_cumul_trans_matrices = _pyaccel.tracking.find_m44(tl)
    tl_twiss, _ = _pyaccel.optics.calc_twiss(accelerator=tl,
                                             init_twiss=twiss_in)
    # betax1 = tl_twiss[end_index].betax
    # alphax1 = tl_twiss[end_index].alphax
    # mux1 = tl_twiss[end_index].mux
    # betay1 = tl_twiss[end_index].betay
    # alphay1 = tl_twiss[end_index].alphay
    # muy1 = tl_twiss[end_index].muy

    if orb == 'x':
        m_ch1 = tl_cumul_trans_matrices[ch1_idx]
        m_ch12end = np.dot(tl_m44, np.linalg.inv(m_ch1))
        m_ch2 = tl_cumul_trans_matrices[ch2_idx]
        m_ch22end = np.dot(tl_m44, np.linalg.inv(m_ch2))

        mat_transf_x = [0, 0, 0, 0]

        # betax0 = tl_twiss[ch1_idx].betax
        # mux0 = tl_twiss[ch1_idx].mux
        # if isclose(m_ch12end[0, 1], sqrt(betax1*betax0)*sin(mux1-mux0)):
        #     print('OK')
        #     mat_transf_x[0] = m_ch12end[0, 1]
        # if isclose(
        #         m_ch12end[1, 1],
        #         sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0))):
        #     print('OK')
        #     mat_transf_x[2] = m_ch12end[1, 1]
        mat_transf_x[0] = m_ch12end[0, 1]
        mat_transf_x[2] = m_ch12end[1, 1]

        # betax0 = tl_twiss[ch2_idx].betax
        # mux0 = tl_twiss[ch2_idx].mux
        # if isclose(m_ch22end[0, 1], sqrt(betax1*betax0)*sin(mux1-mux0)):
        #     print('OK')
        #     mat_transf_x[1] = m_ch22end[0, 1]
        # if isclose(
        #         m_ch22end[1, 1],
        #         sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0))):
        #     print('OK')
        #     mat_transf_x[3] = m_ch22end[1, 1]
        mat_transf_x[1] = m_ch22end[0, 1]
        mat_transf_x[3] = m_ch22end[1, 1]

        return mat_transf_x

    elif orb == 'y':
        m_cv1 = tl_cumul_trans_matrices[cv1_idx]
        m_cv12end = np.dot(tl_m44, np.linalg.inv(m_cv1))
        m_cv2 = tl_cumul_trans_matrices[cv2_idx]
        m_cv22end = np.dot(tl_m44, np.linalg.inv(m_cv2))

        mat_transf_y = [0, 0, 0, 0]

        # betay0 = tl_twiss[cv1_idx].betay
        # muy0 = tl_twiss[cv1_idx].muy
        # if isclose(m_cv12end[2, 3], sqrt(betay1*betay0)*sin(muy1-muy0)):
        #     print('OK')
        #     mat_transf_y[0] = m_cv12end[2, 3]
        # if isclose(
        #         m_cv12end[3, 3],
        #         sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0))):
        #     print('OK')
        #     mat_transf_y[2] = m_cv12end[3, 3]
        mat_transf_y[0] = m_cv12end[2, 3]
        mat_transf_y[2] = m_cv12end[3, 3]

        # betay0 = tl_twiss[cv2_idx].betay
        # muy0 = tl_twiss[cv2_idx].muy
        # if isclose(m_cv22end[2, 3], sqrt(betay1*betay0)*sin(muy1-muy0)):
        #     print('OK')
        #     mat_transf_y[1] = m_cv22end[2, 3]
        # if isclose(
        #         m_cv22end[3, 3],
        #         sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0))):
        #     print('OK')
        #     mat_transf_y[3] = m_cv22end[3, 3]
        mat_transf_y[1] = m_cv22end[2, 3]
        mat_transf_y[3] = m_cv22end[3, 3]

        return mat_transf_y


if __name__ == '__main__':
    tb_respmatx = get_respmat('tb', 'x')
    print('TB horizontal correction matrix: ', tb_respmatx)
    tb_respmaty = get_respmat('tb', 'y')
    print('TB vertical correction matrix:   ', tb_respmaty)
    ts_respmatx = get_respmat('ts', 'x')
    print('TS horizontal correction matrix: ', ts_respmatx)
    ts_respmaty = get_respmat('ts', 'y')
    print('TS vertical correction matrix:   ', ts_respmaty)
