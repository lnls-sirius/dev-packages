#!/usr/bin/env python3.6
import pyaccel as _pyaccel
import pymodels as _pymodels
import numpy as np
from math import *
import sys as _sys

args = _sys.argv
v = args[1]

def get_respmat(s,orb,verify):
    if s == 'ts':
        tl, twiss_in = _pymodels.ts.create_accelerator()
        last_element = 161
        ch1 = 128
        ch2 = 158
        cv1 = 126
        cv2 = 141
    elif s == 'tb':
        tl, twiss_in = _pymodels.tb.create_accelerator()
        last_element = 137
        ch1 = 110
        ch2 = 135
        cv1 = 131
        cv2 = 135
    tl_m44, tl_cumul_trans_matrices = _pyaccel.tracking.find_m44(tl)

    tl_twiss, *_ = _pyaccel.optics.calc_twiss(accelerator=tl,init_twiss=twiss_in)
    betax1 = tl_twiss[last_element].betax
    alphax1 = tl_twiss[last_element].alphax
    mux1 = tl_twiss[last_element].mux
    betay1 = tl_twiss[last_element].betay
    alphay1 = tl_twiss[last_element].alphay
    muy1 = tl_twiss[last_element].muy

    if orb == 'x':
        m_ch1 = tl_cumul_trans_matrices[ch1] # element that corresponds to the end of ch1
        m_ch12end = np.dot(tl_m44,np.linalg.inv(m_ch1))
        m_ch2 = tl_cumul_trans_matrices[ch2] # element that corresponds to the end of ch2
        m_ch22end = np.dot(tl_m44,np.linalg.inv(m_ch2))

        mat_transf_x = [0,0,0,0]
        betax0 = tl_twiss[ch1].betax
        alphax0 = tl_twiss[ch1].alphax
        mux0 = tl_twiss[ch1].mux
        mat_transf_x[0] = m_ch12end[0,1]
        if verify:
            print(mat_transf_x[0])
            print(sqrt(betax1*betax0)*sin(mux1-mux0))
            if mat_transf_x[0] == sqrt(betax1*betax0)*sin(mux1-mux0):
                print('ok element 0 matrix x')
        mat_transf_x[2] = m_ch12end[1,1]
        if verify:
            print(mat_transf_x[2])
            print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))
            if mat_transf_x[2] == sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)):
                print('ok element 2 matrix x')

        betax0 = tl_twiss[ch2].betax
        alphax0 = tl_twiss[ch2].alphax
        mux0 = tl_twiss[ch2].mux
        mat_transf_x[1] = m_ch22end[0,1]
        if verify:
            print(mat_transf_x[1])
            print(sqrt(betax1*betax0)*sin(mux1-mux0))
            if mat_transf_x[1] == sqrt(betax1*betax0)*sin(mux1-mux0):
                print('ok element 1 matrix x')
        mat_transf_x[3] = m_ch22end[1,1]
        if verify:
            print(mat_transf_x[3])
            print(sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)))
            if mat_transf_x[3] == sqrt(betax0/betax1)*(cos(mux1-mux0)-alphax1*sin(mux1-mux0)):
                print('ok element 3 matrix x')

        print(s.upper() + ' Horizontal Orbit Response Matrix: ')
        print(mat_transf_x)
        return mat_transf_x

    if orb == 'y':
        m_cv1 = tl_cumul_trans_matrices[cv1] # element that corresponds to the end of cv1
        m_cv12end = np.dot(tl_m44,np.linalg.inv(m_cv1))
        m_cv2 = tl_cumul_trans_matrices[cv2] # element that corresponds to the end of cv2
        m_cv22end = np.dot(tl_m44,np.linalg.inv(m_cv2))

        mat_transf_y = [0,0,0,0]
        betay0 = tl_twiss[cv1].betay
        alphay0 = tl_twiss[cv1].alphay
        muy0 = tl_twiss[cv1].muy
        mat_transf_y[0] = m_cv12end[2,3]
        if verify:
            print(mat_transf_y[0])
            print(sqrt(betay1*betay0)*sin(muy1-muy0))
            if mat_transf_y[0] == sqrt(betay1*betay0)*sin(muy1-muy0):
                print('ok element 0 matrix y')
        mat_transf_y[2] = m_cv12end[3,3]
        if verify:
            print(mat_transf_y[2])
            print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))
            if mat_transf_y[2] == sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)):
                print('ok element 2 matrix y')

        betay0 = tl_twiss[cv2].betay
        alphay0 = tl_twiss[cv2].alphay
        muy0 = tl_twiss[cv2].muy
        mat_transf_y[1] = m_cv22end[2,3]
        if verify:
            print(mat_transf_y[1])
            print(sqrt(betay1*betay0)*sin(muy1-muy0))
            if mat_transf_y[1] == sqrt(betay1*betay0)*sin(muy1-muy0):
                print('ok element 1 matrix y')
        mat_transf_y[3] = m_cv22end[3,3]
        if verify:
            print(mat_transf_y[3])
            print(sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)))
            if mat_transf_y[3] == sqrt(betay0/betay1)*(cos(muy1-muy0)-alphay1*sin(muy1-muy0)):
                print('ok element 3 matrix y')

        print(s.upper() + ' Vertical Orbit Response Matrix: ')
        print(mat_transf_y)
        return mat_transf_y


if __name__ == '__main__':
    if v == 'y':
        v = True
    elif v == 'n':
        v = False

    get_respmat('ts','x',v)
    get_respmat('ts','y',v)

    get_respmat('tb','x',v)
    get_respmat('tb','y',v)
