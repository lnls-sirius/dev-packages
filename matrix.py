"""Class of the Response Matrix."""

import os as _os
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
        db['RFEnbl-Sel'][prop] = _part(self.set_enbl_list, 'rf')
        db['NumSingValues-SP'][prop] = self.set_num_sing_values
        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        path_ = _os.path.abspath(_os.path.dirname(__file__))
        ext = acc.lower() + 'respmat'
        self.RESPMAT_FILENAME = _os.path.join(path_, 'data', 'respmat.'+ext)

        self.select_items = {
            'bpmx': _np.ones(self._csorb.NR_BPMS, dtype=bool),
            'bpmy': _np.ones(self._csorb.NR_BPMS, dtype=bool),
            'ch': _np.ones(self._csorb.NR_CH, dtype=bool),
            'cv': _np.ones(self._csorb.NR_CV, dtype=bool),
            'rf': _np.zeros(1, dtype=bool),
            }
        self.selection_pv_names = {
              'ch': 'CHEnblList-RB',
              'cv': 'CVEnblList-RB',
              'bpmx': 'BPMXEnblList-RB',
              'bpmy': 'BPMYEnblList-RB',
              'rf': 'RFEnbl-Sts',
            }
        self.num_sing_values = self._csorb.NR_SING_VALS
        self.sing_values = _np.zeros(self._csorb.NR_CORRS, dtype=float)
        self.respmat = _np.zeros([2*self._csorb.NR_BPMS, self._csorb.NR_CORRS])
        self.inv_respmat = self.respmat.copy().T
        self._load_respmat()

    def set_respmat(self, mat):
        """Set the response matrix in memory and save it in file."""
        self.run_callbacks('Log-Mon', 'Setting New RespMat.')
        if len(mat) != self._csorb.MTX_SZ:
            self._update_log('ERR: Wrong RespMat Size.')
            return False
        mat = _np.reshape(mat, [2*self._csorb.NR_BPMS, self._csorb.NR_CORRS])
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
        kicks = _np.dot(-self.inv_respmat, orbit)
        self.run_callbacks(
                        'DeltaKicksCH-Mon', list(kicks[:self._csorb.NR_CH]))
        self.run_callbacks(
                        'DeltaKicksCV-Mon', list(kicks[self._csorb.NR_CH:-1]))
        self.run_callbacks('DeltaKicksRF-Mon', kicks[-1])
        return kicks

    def set_enbl_list(self, key, val):
        self._update_log('Setting {0:s} Enable List'.format(key.upper()))
        bkup = self.select_items[key]
        new_ = _np.array(val, dtype=bool)
        if key == 'rf':
            new_ = True if val else False
        elif len(new_) >= len(bkup):
            new_ = new_[:len(bkup)]
        else:
            new2_ = bkup.copy()
            new2_[:len(new_)] = new_
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
        self.run_callbacks('NumSingValues-RB', num)
        return True

    def _calc_matrices(self):
        self._update_log('Calculating Inverse Matrix.')
        sel_ = self.select_items
        selecbpm = _np.hstack([sel_['bpmx'], sel_['bpmy']])
        seleccor = _np.hstack([sel_['ch'], sel_['cv'], sel_['rf']])
        if not any(selecbpm):
            self._update_log('ERR: No BPM selected in EnblList')
            return False
        if not any(seleccor):
            self._update_log('ERR: No Corrector selected in EnblList')
            return False
        sel_mat = selecbpm[:, None] * seleccor[None, :]
        mat = self.respmat[sel_mat]
        mat = _np.reshape(mat, [sum(selecbpm), sum(seleccor)])
        try:
            U, s, V = _np.linalg.svd(mat, full_matrices=False)
        except _np.linalg.LinAlgError():
            self._update_log('ERR: Could not calculate SVD')
            return False
        inv_s = 1/s
        inv_s[self.num_sing_values:] = 0
        Inv_S = _np.diag(inv_s)
        inv_mat = _np.dot(_np.dot(V.T, Inv_S), U.T)
        isNan = _np.any(_np.isnan(inv_mat))
        isInf = _np.any(_np.isinf(inv_mat))
        if isNan or isInf:
            self._update_log('ERR: Inverse contains nan or inf.')
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
        filename = self.RESPMAT_FILENAME
        if _os.path.isfile(filename):
            bkup = self.respmat.copy()
            self.respmat = _np.loadtxt(filename)
            if not self._calc_matrices():
                self.respmat = bkup
                return
            self._update_log('Loading RespMat from file.')
            self.run_callbacks('RespMat-RB', list(self.respmat.flatten()))

    def _save_respmat(self, mat):
        self._update_log('Saving RespMat to file')
        _np.savetxt(self.RESPMAT_FILENAME, mat)
