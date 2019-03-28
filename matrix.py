"""Class of the Response Matrix."""

import os as _os
import logging as _log
import numpy as _np
from functools import partial as _part
from .base_class import BaseClass as _BaseClass


class BaseMatrix(_BaseClass):
    pass


class EpicsMatrix(BaseMatrix):
    """Class of the Response Matrix."""

    def get_database(self):
        """Get the database of the class."""
        db = self._csorb.get_respmat_database()
        prop = 'fun_set_pv'
        db['RespMat-SP'][prop] = self.set_respmat
        db['CHEnblList-SP'][prop] = _part(self.set_enbl_list, 'ch')
        db['CVEnblList-SP'][prop] = _part(self.set_enbl_list, 'cv')
        db['BPMXEnblList-SP'][prop] = _part(self.set_enbl_list, 'bpmx')
        db['BPMYEnblList-SP'][prop] = _part(self.set_enbl_list, 'bpmy')
        db['NrSingValues-SP'][prop] = self.set_num_sing_values
        if self.isring:
            db['RFEnbl-Sel'][prop] = _part(self.set_enbl_list, 'rf')
        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self.select_items = {
            'bpmx': _np.ones(self._csorb.NR_BPMS, dtype=bool),
            'bpmy': _np.ones(self._csorb.NR_BPMS, dtype=bool),
            'ch': _np.ones(self._csorb.NR_CH, dtype=bool),
            'cv': _np.ones(self._csorb.NR_CV, dtype=bool),
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
        self.num_sing_values = self._csorb.NR_SING_VALS
        self.sing_values = _np.zeros(self._csorb.NR_CORRS, dtype=float)
        self.respmat = _np.zeros([2*self._csorb.NR_BPMS, self._csorb.NR_CORRS])
        self.inv_respmat = self.respmat.copy().T
        self._load_respmat()

    def set_respmat(self, mat):
        """Set the response matrix in memory and save it in file."""
        msg = 'Setting New RespMat.'
        self._update_log(msg)
        _log.info(msg)
        mat = _np.array(mat, dtype=float)
        if mat.size % self._csorb.MTX_SZ:
            msg = 'ERR: Wrong RespMat Size.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        mat = _np.reshape(mat, [-1, self._csorb.NR_CORRS])
        old_ = self.respmat.copy()
        self.respmat = mat
        if not self._calc_matrices():
            self.respmat = old_
            return False
        self._save_respmat(mat)
        self.run_callbacks('RespMat-RB', list(self.respmat.flatten()))
        return True

    def calc_kicks(self, orbit):
        """Calculate the kick from the orbit distortion given."""
        if len(orbit) != self.inv_respmat.shape[0]:
            msg = 'ERR: Orbit and matrix size not compatible.'
            self._update_log(msg)
            _log.error(msg[5:])
            return
        kicks = _np.dot(-self.inv_respmat, orbit)
        nr_ch = self._csorb.NR_CH
        nr_chcv = self._csorb.NR_CHCV
        self.run_callbacks('DeltaKickCH-Mon', list(kicks[:nr_ch]))
        self.run_callbacks('DeltaKickCV-Mon', list(kicks[nr_ch:nr_chcv]))
        if self.isring:
            self.run_callbacks('DeltaKickRF-Mon', kicks[-1])
        return kicks

    def set_enbl_list(self, key, val):
        msg = 'Setting {0:s} Enable List'.format(key.upper())
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
        if not self._calc_matrices():
            self.select_items[key] = bkup
            return False
        self.run_callbacks(self.selection_pv_names[key], val)
        return True

    def set_num_sing_values(self, num):
        bkup = self.num_sing_values
        self.num_sing_values = num
        if not self._calc_matrices():
            self.num_sing_values = bkup
            return False
        self.run_callbacks('NrSingValues-RB', self.num_sing_values)
        return True

    def _calc_matrices(self):
        msg = 'Calculating Inverse Matrix.'
        self._update_log(msg)
        _log.info(msg)
        sel_ = self.select_items
        selecbpm = _np.hstack([sel_['bpmx'], sel_['bpmy']])
        seleccor = _np.hstack([sel_['ch'], sel_['cv']])
        if self.isring:
            seleccor = _np.hstack([seleccor, sel_['rf']])
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
        mat = self.respmat[sel_mat]
        mat = _np.reshape(mat, [sum(selecbpm), sum(seleccor)])
        try:
            U, s, V = _np.linalg.svd(mat, full_matrices=False)
        except _np.linalg.LinAlgError():
            msg = 'ERR: Could not calculate SVD'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        inv_s = 1/s
        nsv = _np.isfinite(inv_s).sum()
        if not nsv:
            msg = 'ERR: All Singular Values are zero.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        elif nsv < self.num_sing_values:
            self.num_sing_values = nsv
            self.run_callbacks('NrSingValues-SP', nsv)
            self.run_callbacks('NrSingValues-RB', nsv)
            msg = 'WARN: NrSingValues had to be set to {0:d}.'.format(nsv)
            self._update_log(msg)
            _log.warning(msg[6:])
        inv_s[self.num_sing_values:] = 0
        Inv_S = _np.diag(inv_s)
        inv_mat = _np.dot(_np.dot(V.T, Inv_S), U.T)
        is_nan = _np.any(_np.isnan(inv_mat))
        is_inf = _np.any(_np.isinf(inv_mat))
        if is_nan or is_inf:
            msg = 'ERR: Inverse contains nan or inf.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False

        self.sing_values[:] = 0
        self.sing_values[:len(s)] = s
        self.run_callbacks('SingValues-Mon', list(self.sing_values))
        self.inv_respmat = _np.zeros(
                        [2*self._csorb.NR_BPMS, self._csorb.NR_CORRS]).T
        self.inv_respmat[sel_mat.T] = inv_mat.flatten()
        self.run_callbacks(
                'InvRespMat-Mon', list(self.inv_respmat.flatten()))
        return True

    def _load_respmat(self):
        filename = self._csorb.RESPMAT_FILENAME
        if _os.path.isfile(filename):
            bkup = self.respmat.copy()
            self.respmat = _np.loadtxt(filename)
            if not self._calc_matrices():
                self.respmat = bkup
                return
            msg = 'Loading RespMat from file.'
            self._update_log(msg)
            _log.info(msg)
            self.run_callbacks('RespMat-RB', list(self.respmat.flatten()))

    def _save_respmat(self, mat):
        msg = 'Saving RespMat to file'
        self._update_log(msg)
        _log.info(msg)
        path = _os.path.split(self._csorb.RESPMAT_FILENAME)[0]
        if not _os.path.isdir(path):
            _os.mkdir(path)
        _np.savetxt(self._csorb.RESPMAT_FILENAME, mat)
