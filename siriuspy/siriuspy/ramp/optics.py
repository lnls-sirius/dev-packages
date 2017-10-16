"""Optics module.

This module implements routines that calculate new strenght values for
magnets, given desired tunes and chromaticities. These routines use epics
soft IOCs in order to accomplish its tasks.
"""

import numpy as _np

# All beam optics data in this module is taken from running
# AT script 'sirius_integrated_strength.m'.
#
# Lattice Models:
#                SI.V22.02_S05.01
#                BO.V04.01.M0

_nominal_tunes_si = [49.09624237, 14.15190288]
_nominal_chrom_si = [02.57562434, 02.50328132]
_nominal_tunes_bo = [19.20433000, 07.31417006]
_nominal_chrom_bo = [00.49987001, 00.49998761]

_nominal_intkl = {

    'SI-Fam:MA-QFA': +00.7146305692912001,
    'SI-Fam:MA-QDA': -00.2270152048045000,
    'SI-Fam:MA-QFB': +01.2344424683922000,
    'SI-Fam:MA-QDB2': -00.4782973132726601,
    'SI-Fam:MA-QDB1': -00.2808906119138000,
    'SI-Fam:MA-QFP': +01.2344424683922000,
    'SI-Fam:MA-QDP2': -00.4782973132726601,
    'SI-Fam:MA-QDP1': -00.2808906119138000,
    'SI-Fam:MA-Q1': +00.5631612043340000,
    'SI-Fam:MA-Q2': +00.8684629376249999,
    'SI-Fam:MA-Q3': +00.6471254242426001,
    'SI-Fam:MA-Q4': +00.7867827142062001,
    'SI-Fam:MA-SDA0': -12.1250549999999979,
    'SI-Fam:MA-SDB0': -09.7413299999999996,
    'SI-Fam:MA-SDP0': -09.7413299999999996,
    'SI-Fam:MA-SDA1': -24.4479749999999996,
    'SI-Fam:MA-SDB1': -21.2453849999999989,
    'SI-Fam:MA-SDP1': -21.3459000000000003,
    'SI-Fam:MA-SDA2': -13.3280999999999992,
    'SI-Fam:MA-SDB2': -18.3342150000000004,
    'SI-Fam:MA-SDP2': -18.3421500000000002,
    'SI-Fam:MA-SDA3': -20.9911199999999987,
    'SI-Fam:MA-SDB3': -26.0718599999999974,
    'SI-Fam:MA-SDP3': -26.1236099999999993,
    'SI-Fam:MA-SFA0': +07.8854400000000000,
    'SI-Fam:MA-SFB0': +11.0610149999999994,
    'SI-Fam:MA-SFP0': +11.0610149999999994,
    'SI-Fam:MA-SFA1': +28.7742599999999982,
    'SI-Fam:MA-SFB1': +34.1821950000000001,
    'SI-Fam:MA-SFP1': +34.3873949999999979,
    'SI-Fam:MA-SFA2': +22.6153800000000018,
    'SI-Fam:MA-SFB2': +29.6730900000000020,
    'SI-Fam:MA-SFP2': +29.7755099999999970,
    'BO-Fam:MA-QD': +00.0011197961538728,
    'BO-Fam:MA-QF': +00.3770999232791374,
    'BO-Fam:MA-SD': +00.5258382119529604,
    'BO-Fam:MA-SF': +01.1898514030258744,
}


def get_nominal_integrated_strengths(magnet):
    """Return nominal integrated strength of a given magnet."""
    return _nominal_intkl[magnet]


def calc_dkl_correct_tune(wfmset, dtunex, dtuney):
    """Calculate dKL of quadrupoles that implements a given tune shift."""
    # PVs that will be used (examples):
    # 'CalcDeltaKL-Cmd'
    # 'LastCalcdSFSL-Mon'
    # 'LastCalcdSD'
    # 'LastCalcdSL-Mon'
    _respm_tune_bo = _np.array(
        [[+92.66995777,  +4.12350708],
         [-21.10665142, -38.74671566]])

    dtune = _np.array([dtunex, dtuney])
    dkl = {}
    if wfmset.section == 'BO':
        r = _np.linalg.solve(_respm_tune_bo, dtune)
        dkl['BO-Fam:MA-QF'] = r[0]
        dkl['BO-Fam:MA-QD'] = r[1]
    elif wfmset.section == 'SI':
        dkl['SI-Fam:MA-QFA'] = 0.0
        dkl['SI-Fam:MA-QDA'] = 0.0
        dkl['SI-Fam:MA-QFB'] = 0.0
        dkl['SI-Fam:MA-QDB2'] = 0.0
        dkl['SI-Fam:MA-QDB1'] = 0.0
        dkl['SI-Fam:MA-QFP'] = 0.0
        dkl['SI-Fam:MA-QDP2'] = 0.0
        dkl['SI-Fam:MA-QDP1'] = 0.0
    return dkl
