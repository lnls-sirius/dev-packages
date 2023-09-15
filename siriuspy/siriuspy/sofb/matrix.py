"""Class of the Response Matrix."""

import os as _os
import logging as _log
from functools import partial as _part

import numpy as _np

from .base_class import BaseClass as _BaseClass


class BaseMatrix(_BaseClass):
    """."""


class EpicsMatrix(BaseMatrix):
    """Class of the Response Matrix."""

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._sofb = None
        self.select_items = {
            'bpmx': _np.ones(self._csorb.nr_bpms, dtype=bool),
            'bpmy': _np.ones(self._csorb.nr_bpms, dtype=bool),
            'ch': _np.ones(self._csorb.nr_ch, dtype=bool),
            'cv': _np.ones(self._csorb.nr_cv, dtype=bool),
            }
        self.selection_pv_names = {
            'ch': 'CHEnblList-RB',
            'cv': 'CVEnblList-RB',
            'bpmx': 'BPMXEnblList-RB',
            'bpmy': 'BPMYEnblList-RB',
            }
        if self.isring:
            self.select_items['rf'] = _np.zeros(1, dtype=bool)
            self.selection_pv_names['rf'] = 'RFEnbl-Sts'
        self._respmat_mode = self._csorb.RespMatMode.Full
        self.min_sing_val = self._csorb.MIN_SING_VAL
        self.tikhonov_reg_const = self._csorb.TIKHONOV_REG_CONST
        self.respmat = _np.zeros(
            [2*self._csorb.nr_bpms, self._csorb.nr_corrs], dtype=float)
        self.inv_respmat = self.respmat.copy().T
        self.respmat_processed = self.respmat.copy().T
        self._load_respmat()

    @property
    def sofb(self):
        """."""
        return self._sofb

    @sofb.setter
    def sofb(self, sofb):
        self._sofb = sofb

    @property
    def bpm_enbllist(self):
        """."""
        sel_ = self.select_items
        return _np.hstack([sel_['bpmx'], sel_['bpmy']])

    @property
    def corrs_enbllist(self):
        """."""
        sel_ = self.select_items
        seleccor = _np.hstack([sel_['ch'], sel_['cv']])
        if self.isring:
            seleccor = _np.hstack([seleccor, sel_['rf']])
        return seleccor

    def get_map2write(self):
        """Get the write methods of the class."""
        dbase = {
            'RespMat-SP': self.set_respmat,
            'RespMatMode-Sel': self.set_respmat_mode,
            'CHEnblList-SP': _part(self.set_enbllist, 'ch'),
            'CVEnblList-SP': _part(self.set_enbllist, 'cv'),
            'BPMXEnblList-SP': _part(self.set_enbllist, 'bpmx'),
            'BPMYEnblList-SP': _part(self.set_enbllist, 'bpmy'),
            'MinSingValue-SP': self.set_min_sing_value,
            'TikhonovRegConst-SP': self.set_tikhonov_reg_const,
            }
        if self.isring:
            dbase['RFEnbl-Sel'] = _part(self.set_enbllist, 'rf')
        return dbase

    def set_respmat_mode(self, mode):
        """Set the response matrix mode."""
        msg = 'Setting New RespMatMode.'
        self._update_log(msg)
        _log.info(msg)
        if mode not in self._csorb.RespMatMode:
            self.run_callbacks('RespMatMode-Sel', self._respmat_mode)
            return
        old_ = self._respmat_mode
        self._respmat_mode = mode
        if not self._calc_matrices():
            self._respmat_mode = old_
            self.run_callbacks('RespMatMode-Sel', self._respmat_mode)
            return
        self.run_callbacks('RespMatMode-Sts', self._respmat_mode)
        return True

    def set_respmat(self, mat):
        """Set the response matrix in memory and save it in file."""
        msg = 'Setting New RespMat.'
        self._update_log(msg)
        _log.info(msg)
        if mat is None:
            self.run_callbacks('RespMat-SP', list(self.respmat.ravel()))
            return False
        mat = _np.reshape(mat, [-1, self._csorb.nr_corrs])
        old_ = self.respmat.copy()
        self.respmat = mat
        if not self._calc_matrices():
            self.respmat = old_
            self.run_callbacks('RespMat-SP', list(self.respmat.ravel()))
            return False
        self._save_respmat(mat)
        self.run_callbacks('RespMat-RB', list(self.respmat.ravel()))
        return True

    def set_enbllist(self, key, val):
        """."""
        msg = 'Setting {0:s} EnblList'.format(key.upper())
        self._update_log(msg)
        _log.info(msg)

        bkup = self.select_items[key]
        new_ = _np.array(val, dtype=bool)
        if key == 'rf':
            pass
        elif new_.size >= bkup.size:
            new_ = new_[:bkup.size]
        else:
            new2_ = bkup.copy()
            new2_[:new_.size] = new_
            new_ = new2_
        self.select_items[key] = new_

        pvn = self.selection_pv_names[key]
        if not self._calc_matrices():
            self.select_items[key] = bkup
            new_ = bkup
            pvn = pvn.replace('-RB', '-SP')

        new_ = bool(new_) if new_.size == 1 else new_
        self.run_callbacks(pvn, new_)
        return True

    def calc_kicks(self, orbit):
        """Calculate the kick from the orbit distortion given."""
        if orbit.size != self.inv_respmat.shape[1]:
            msg = 'ERR: Orbit and matrix size not compatible.'
            self._update_log(msg)
            _log.error(msg[5:])
            return None
        kicks = _np.dot(self.inv_respmat, orbit)
        kicks *= -1
        self._LQTHREAD.put((self._update_dkicks, (kicks, )))
        return kicks

    def estimate_orbit_variation(self, kicks):
        """Estimate the orbit variation induced by kicks.

        Args:
            kicks (numpy.ndarray): Correctors kicks that will be used to
                estimate orbit distortion.

        Returns:
            dorb (numpy.ndarray): Estimated orbit.

        """
        if kicks.size != self.respmat.shape[1]:
            msg = 'ERR: kicks and matrix size not compatible.'
            self._update_log(msg)
            _log.error(msg[5:])
            return None
        return _np.dot(self.respmat, kicks)

    def _update_dkicks(self, kicks):
        kicks = kicks.copy()
        nr_ch = self._csorb.nr_ch
        nr_chcv = self._csorb.nr_chcv
        self.run_callbacks('DeltaKickCH-Mon', kicks[:nr_ch])
        self.run_callbacks('DeltaKickCV-Mon', kicks[nr_ch:nr_chcv])
        if self.isring:
            self.run_callbacks('DeltaKickRF-Mon', kicks[-1])

    def set_min_sing_value(self, num):
        """."""
        bkup = self.min_sing_val
        self.min_sing_val = float(num)
        if not self._calc_matrices():
            self.min_sing_val = bkup
            self.run_callbacks('MinSingValue-SP', self.min_sing_val)
            return False
        self.run_callbacks('MinSingValue-RB', self.min_sing_val)
        return True

    def set_tikhonov_reg_const(self, num):
        """."""
        bkup = self.tikhonov_reg_const
        self.tikhonov_reg_const = float(num)
        if not self._calc_matrices():
            self.tikhonov_reg_const = bkup
            self.run_callbacks('TikhonovRegConst-SP', self.tikhonov_reg_const)
            return False
        self.run_callbacks('TikhonovRegConst-RB', self.tikhonov_reg_const)
        return True

    def _calc_matrices(self):
        msg = 'Calculating Inverse Matrix.'
        self._update_log(msg)
        _log.info(msg)
        selecbpm = self.bpm_enbllist
        seleccor = self.corrs_enbllist
        if not any(selecbpm):
            msg = 'ERR: No BPM selected in EnblList'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if not any(seleccor):
            msg = 'ERR: No Corrector selected in EnblList'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        sel_mat = selecbpm[:, None] * seleccor[None, :]
        if sel_mat.size != self.respmat.size:
            return False
        mat = self.respmat.copy()
        nr_bpms = self._csorb.nr_bpms
        nr_ch = self._csorb.nr_ch
        nr_chcv = self._csorb.nr_chcv
        if self._respmat_mode != self._csorb.RespMatMode.Full:
            mat[:nr_bpms, nr_ch:nr_chcv] = 0
            mat[nr_bpms:, :nr_ch] = 0
            mat[nr_bpms:, nr_chcv:] = 0
        if self._respmat_mode == self._csorb.RespMatMode.Mxx:
            mat[nr_bpms:] = 0
        elif self._respmat_mode == self._csorb.RespMatMode.Myy:
            mat[:nr_bpms] = 0

        mat = mat[sel_mat]
        mat = _np.reshape(mat, [sum(selecbpm), sum(seleccor)])
        try:
            uuu, sing, vvv = _np.linalg.svd(mat, full_matrices=False)
        except _np.linalg.LinAlgError():
            msg = 'ERR: Could not calculate SVD'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        idcs = sing > self.min_sing_val
        singr = sing[idcs]
        nr_sv = _np.sum(idcs)
        if not nr_sv:
            msg = 'ERR: All Singular Values below minimum.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False

        # Apply Tikhonov regularization:
        regc = self.tikhonov_reg_const
        regc *= regc
        inv_s = _np.zeros(sing.size, dtype=float)
        inv_s[idcs] = singr/(singr*singr + regc)

        # calculate processed singular values
        singp = _np.zeros(sing.size, dtype=float)
        singp[idcs] = 1/inv_s[idcs]
        inv_mat = _np.dot(vvv.T*inv_s, uuu.T)
        is_nan = _np.any(_np.isnan(inv_mat))
        is_inf = _np.any(_np.isinf(inv_mat))
        if is_nan or is_inf:
            msg = 'ERR: Inverse contains nan or inf.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False

        sing_vals = _np.zeros(self._csorb.nr_svals, dtype=float)
        sing_vals[:sing.size] = sing
        self.run_callbacks('SingValuesRaw-Mon', sing_vals)
        sing_vals = _np.zeros(self._csorb.nr_svals, dtype=float)
        sing_vals[:singp.size] = singp
        self.run_callbacks('SingValues-Mon', sing_vals)
        self.run_callbacks('NrSingValues-Mon', nr_sv)
        self.inv_respmat = _np.zeros(self.respmat.shape, dtype=float).T
        self.inv_respmat[sel_mat.T] = inv_mat.ravel()
        self.run_callbacks('InvRespMat-Mon', list(self.inv_respmat.ravel()))
        self.respmat_processed = _np.zeros(self.respmat.shape, dtype=float)
        self.respmat_processed[sel_mat] = _np.dot(uuu*singp, vvv).ravel()
        self.run_callbacks('RespMat-Mon', list(self.respmat_processed.ravel()))
        msg = 'Ok!'
        self._update_log(msg)
        _log.info(msg)
        return True

    def _load_respmat(self):
        filename = self._csorb.respmat_fname
        boo = False
        if _os.path.isfile(filename):
            boo = self.set_respmat(_np.loadtxt(filename))
            if boo:
                msg = 'Loading RespMat from file.'
            else:
                msg = 'ERR: Problem loading RespMat from file.'
            self._update_log(msg)
            _log.info(msg)

    def _save_respmat(self, mat):
        path = _os.path.split(self._csorb.respmat_fname)[0]
        _os.makedirs(path, exist_ok=True)
        _np.savetxt(self._csorb.respmat_fname, mat)
