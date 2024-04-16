
import numpy as np

from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.devices import FamFastCorrs
from siriuspy.fofb.csdev import HLFOFBConst

# create FOFB contants
fofbconst = HLFOFBConst()

# get matrix from configdb
client = ConfigDBClient()
ref = client.get_config_value(name='ref_orb', config_type='si_orbit')
respm = client.get_config_value(
    name='ref_respmat', config_type='si_fastorbcorr_respm')
respm = np.asarray(respm)

# connect to correctors and get convertion constants
corrs_dev = FamFastCorrs()

# determine enable lists
# select all
bpmxenbl = np.ones(fofbconst.nr_bpms, dtype=bool)
bpmyenbl = np.ones(fofbconst.nr_bpms, dtype=bool)
chenbl = np.ones(fofbconst.nr_ch, dtype=bool)
cvenbl = np.ones(fofbconst.nr_cv, dtype=bool)
rfenbl = np.ones(1, dtype=bool)
# select one straight section
bpmenbl = np.array(
    ['C1' not in b and 'C3-2' not in b and 'C4' not in b
     for b in fofbconst.bpm_nicknames])
bpmxenbl = bpmenbl
bpmyenbl = bpmenbl
chenbl = np.array(['01M' not in c for c in fofbconst.ch_names])
cvenbl = np.array(['01M' not in c for c in fofbconst.cv_names])
rfenbl = np.zeros(1, dtype=bool)

selbpm = np.hstack([bpmxenbl, bpmyenbl])
selcorr = np.hstack([chenbl, cvenbl, rfenbl])
selmat = selbpm[:, None] * selcorr[None, :]
if selmat.size != respm.size:
    raise ValueError(
        f'Incompatiple selection ({selmat.size}) and matrix size {respm.size}')
mat = respm.copy()
mat = mat[selmat]
mat = np.reshape(mat, [sum(selbpm), sum(selcorr)])

# calculate SVD
try:
    _uo, _so, _vo = np.linalg.svd(mat, full_matrices=False)
except np.linalg.LinAlgError():
    raise ValueError('Could not calculate SVD')

# handle singular values
# select singular values greater than minimum
idcs = _so > fofbconst.MIN_SING_VAL
_sr = _so[idcs]
nrs = np.sum(idcs)
if not nrs:
    raise ValueError('All Singular Values below minimum.')
# apply Tikhonov regularization
regc = fofbconst.TIKHONOV_REG_CONST
regc *= regc
inv_s = np.zeros(_so.size, dtype=float)
inv_s[idcs] = _sr/(_sr*_sr + regc)
# calculate processed singular values
_sp = np.zeros(_so.size, dtype=float)
_sp[idcs] = 1/inv_s[idcs]

# check if inverse matrix is valid
invmat = np.dot(_vo.T*inv_s, _uo.T)
if np.any(np.isnan(invmat)) or np.any(np.isinf(invmat)):
    raise ValueError('Inverse contains nan or inf.')

# reconstruct filtered and regularized matrix in physical units
matr = np.dot(_uo*_sp, _vo)

# convert matrix to hardware units
str2curr = np.r_[corrs_dev.strength_2_current_factor, 1.0]
currgain = np.r_[corrs_dev.curr_gain, 1.0]
# unit convertion: um/urad (1)-> nm/urad (2)-> nm/A (3)-> nm/counts
matc = matr * fofbconst.CONV_UM_2_NM
matc = matc / str2curr[selcorr]
matc = matc * currgain[selcorr]

# obtain pseudoinverse
# calculate SVD for converted matrix
_uc, _sc, _vc = np.linalg.svd(matc, full_matrices=False)
# handle singular value selection
idcsc = _sc/_sc.max() >= 1e-14
inv_sc = np.zeros(_so.size, dtype=float)
inv_sc[idcsc] = 1/_sc[idcsc]
# calculate pseudoinverse of converted matrix from SVD
invmatc = np.dot(_vc.T*inv_sc, _uc.T)

# get final matrices and singular values
sing_vals_raw = np.zeros(fofbconst.nr_svals, dtype=float)
sing_vals_raw[:_so.size] = _so

sing_vals_phy = np.zeros(fofbconst.nr_svals, dtype=float)
sing_vals_phy[:_sp.size] = _sp
nr_sing_vals = nrs

invrespmat = np.zeros(respm.shape, dtype=float).T
invrespmat[selmat.T] = invmat.ravel()

respmat_proc = np.zeros(respm.shape, dtype=float)
respmat_proc[selmat] = matr.ravel()

sing_vals_hw = np.zeros(fofbconst.nr_svals, dtype=float)
sing_vals_hw[:_sc.size] = _sc

invrespmatconv = np.zeros(respm.shape, dtype=float).T
invrespmatconv[selmat.T] = invmatc.ravel()

respmatconv_proc = np.zeros(respm.shape, dtype=float)
respmatconv_proc[selmat] = matc.ravel()
