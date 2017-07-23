"""Class of the Response Matrix."""

import os as _os
import numpy as _np

NR_BPMS = 160
NR_CH = 120
NR_CV = 160
NR_CORRS = NR_CH + NR_CV + 1
MTX_SZ = (2*NR_BPMS) * NR_CORRS


class Matrix:
    """Class of the Response Matrix."""

    RF_ENBL_ENUMS = ('No', 'Yes')
    RSP_MTX_FILENAME = 'data/response_matrix'
    EXT = '.sirspmtx'

    def get_database(self):
        """Get the database of the class."""
        db = dict()
        pre = self.prefix
        db[pre + 'RSPMatrix-SP'] = {
            'type': 'float', 'count': MTX_SZ, 'value': MTX_SZ*[0],
            'unit': '(BH, BV)(nm) x (CH, CV, RF)(urad, Hz)',
            'fun_set_pv': self.set_resp_matrix}
        db[pre + 'RSPMatrix-RB'] = {
            'type': 'float', 'count': MTX_SZ, 'value': MTX_SZ*[0],
            'unit': '(BH, BV)(nm) x (CH, CV, RF)(urad, Hz)'}
        db[pre + 'SingValues-Mon'] = {
            'type': 'float', 'count': NR_CORRS, 'value': NR_CORRS*[0],
            'unit': 'Singular values of the matrix in use'}
        db[pre + 'InvRSPMatrix-Mon'] = {
            'type': 'float', 'count': MTX_SZ, 'value': MTX_SZ*[0],
            'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(nm)'}
        db[pre + 'CHEnblList-SP'] = {
            'type': 'int', 'count': NR_CH, 'value': NR_CH*[1],
            'unit': 'CHs used in correction',
            'fun_set_pv': lambda x: self._set_enbl_list('ch', x)}
        db[pre + 'CHEnblList-RB'] = {
            'type': 'int', 'count': NR_CH, 'value': NR_CH*[1],
            'unit': 'CHs used in correction'}
        db[pre + 'CVEnblList-SP'] = {
            'type': 'int', 'count': NR_CV, 'value': NR_CV*[1],
            'unit': 'CVs used in correction',
            'fun_set_pv': lambda x: self._set_enbl_list('cv', x)}
        db[pre + 'CVEnblList-RB'] = {
            'type': 'int', 'count': NR_CV, 'value': NR_CV*[1],
            'unit': 'CVs used in correction'}
        db[pre + 'BPMXEnblList-SP'] = {
            'type': 'int', 'count': NR_BPMS, 'value': NR_BPMS*[1],
            'unit': 'BPMX used in correction',
            'fun_set_pv': lambda x: self._set_enbl_list('bpmx', x)}
        db[pre + 'BPMXEnblList-RB'] = {
            'type': 'int', 'count': NR_BPMS, 'value': NR_BPMS*[1],
            'unit': 'BPMX used in correction'}
        db[pre + 'BPMYEnblList-SP'] = {
            'type': 'int', 'count': NR_BPMS, 'value': NR_BPMS*[1],
            'unit': 'BPMY used in correction',
            'fun_set_pv': lambda x: self._set_enbl_list('bpmy', x)}
        db[pre + 'BPMYEnblList-RB'] = {
            'type': 'int', 'count': NR_BPMS, 'value': NR_BPMS*[1],
            'unit': 'BPMY used in correction'}
        db[pre + 'RFEnbl-Sel'] = {
            'type': 'enum', 'enums': self.RF_ENBL_ENUMS, 'value': 0,
            'unit': 'If RF is used in correction',
            'fun_set_pv': lambda x: self._set_enbl_list('rf', x)}
        db[pre + 'RFEnbl-Sts'] = {
            'type': 'enum', 'enums': self.RF_ENBL_ENUMS, 'value': 0,
            'unit': 'If RF is used in correction'}
        db[pre + 'NumSingValues-SP'] = {
            'type': 'int', 'value': NR_CORRS, 'lolim': 1, 'hilim': NR_CORRS,
            'unit': 'Maximum number of SV to use',
            'fun_set_pv': self._set_num_sing_values}
        db[pre + 'NumSingValues-RB'] = {
            'type': 'int', 'value': NR_CORRS, 'lolim': 1, 'hilim': NR_CORRS,
            'unit': 'Maximum number of SV to use'}
        db[pre + 'CHCalcdKicks-Mon'] = {
            'type': 'float', 'count': NR_CH, 'value': NR_CH*[0],
            'unit': 'Last CH kicks calculated.'}
        db[pre + 'CVCalcdKicks-Mon'] = {
            'type': 'float', 'count': NR_CV, 'value': NR_CV*[0],
            'unit': 'Last CV kicks calculated.'}
        db[pre + 'RFCalcdKicks-Mon'] = {
            'type': 'float', 'value': 1, 'unit': 'Last RF kick calculated.'}
        return db

    def __init__(self, prefix, callback):
        """Initialize the instance."""
        self.callback = callback
        self.prefix = prefix
        self.select_items = {
            'bpmx': _np.ones(NR_BPMS, dtype=bool),
            'bpmy': _np.ones(NR_BPMS, dtype=bool),
            'ch': _np.ones(NR_CH, dtype=bool),
            'cv': _np.ones(NR_CV, dtype=bool),
            'rf': _np.zeros(1, dtype=bool),
            }
        self.selection_pv_names = {
              'ch': 'CHEnblList-RB',
              'cv': 'CVEnblList-RB',
              'bpmx': 'BPMXEnblList-RB',
              'bpmy': 'BPMYEnblList-RB',
              'rf': 'RFEnbl-Sts',
            }
        self.num_sing_values = NR_CORRS
        self.sing_values = _np.zeros(NR_CORRS, dtype=float)
        self.response_matrix = _np.zeros([2*NR_BPMS, NR_CORRS])
        self.inv_response_matrix = _np.zeros([2*NR_BPMS, NR_CORRS]).T

    def connect(self):
        """Load the response matrix from file."""
        self._load_response_matrix()

    def set_resp_matrix(self, mat):
        """Set the response matrix in memory and save it in file."""
        self._call_callback('Log-Mon', 'Setting New RSP Matrix.')
        if len(mat) != MTX_SZ:
            self._call_callback('Log-Mon', 'Err: Wrong Size.')
            return False
        mat = _np.reshape(mat, [2*NR_BPMS, NR_CORRS])
        old_ = self.response_matrix.copy()
        self.response_matrix = mat
        if not self._calc_matrices():
            self.response_matrix = old_
            return False
        self._save_resp_matrix(mat)
        self._call_callback('RSPMatrix-RB',
                            list(self.response_matrix.flatten()))
        return True

    def calc_kicks(self, orbit):
        """Calculate the kick from the orbit distortion given."""
        kicks = _np.dot(-self.inv_response_matrix, orbit)
        self._call_callback('CHCalcdKicks-Mon', list(kicks[:NR_CH]))
        self._call_callback('CVCalcdKicks-Mon', list(kicks[NR_CH:NR_CH+NR_CV]))
        self._call_callback('RFCalcdKicks-Mon', kicks[-1])
        return kicks

    def _call_callback(self, pv, value):
        self.callback(self.prefix + pv, value)

    def _set_enbl_list(self, key, val):
        self._call_callback('Log-Mon',
                            'Setting {0:s} Enable List'.format(key.upper()))
        copy_ = self.select_items[key]
        new_ = _np.array(val, dtype=bool)
        if key == 'rf':
            new_ = True if val else False
        elif len(new_) >= len(copy_):
            new_ = new_[:len(copy_)]
        else:
            new2_ = copy_.copy()
            new2_[:len(new_)] = new_
            new_ = new2_
        self.select_items[key] = new_
        if not self._calc_matrices():
            self.select_items[key] = copy_
            return False
        self._call_callback(self.selection_pv_names[key], val)
        return True

    def _calc_matrices(self):
        self._call_callback('Log-Mon', 'Calculating Inverse Matrix.')
        sel_ = self.select_items
        selecbpm = _np.hstack([sel_['bpmx'], sel_['bpmy']])
        seleccor = _np.hstack([sel_['ch'], sel_['cv'], sel_['rf']])
        if not any(selecbpm):
            self._call_callback('Log-Mon', 'Err: No BPM selected in EnblList')
            return False
        if not any(seleccor):
            self._call_callback('Log-Mon',
                                'Err: No Corrector selected in EnblList')
            return False
        sel_mat = selecbpm[:, None] * seleccor[None, :]
        mat = self.response_matrix[sel_mat]
        mat = _np.reshape(mat, [sum(selecbpm), sum(seleccor)])
        try:
            U, s, V = _np.linalg.svd(mat, full_matrices=False)
        except _np.linalg.LinAlgError():
            self._call_callback('Log-Mon', 'Err: Could not calculate SVD')
            return False
        inv_s = 1/s
        inv_s[self.num_sing_values:] = 0
        Inv_S = _np.diag(inv_s)
        inv_mat = _np.dot(_np.dot(V.T, Inv_S), U.T)
        isNan = _np.any(_np.isnan(inv_mat))
        isInf = _np.any(_np.isinf(inv_mat))
        if isNan or isInf:
            self._call_callback('Log-Mon',
                                'Pseudo inverse contains nan or inf.')
            return False

        self.sing_values[:] = 0
        self.sing_values[:len(s)] = s
        self._call_callback('SingValues-Mon', list(self.sing_values))
        self.inv_response_matrix = _np.zeros([2*NR_BPMS, NR_CORRS]).T
        self.inv_response_matrix[sel_mat.T] = inv_mat.flatten()
        self._call_callback('InvRSPMatrix-Mon',
                            list(self.inv_response_matrix.flatten()))
        return True

    def _set_num_sing_values(self, num):
        copy_ = self.num_sing_values
        self.num_sing_values = num
        if not self._calc_matrices():
            self.num_sing_values = copy_
            return False
        self._call_callback('NumSingValues-RB', num)
        return True

    def _load_response_matrix(self):
        filename = self.RSP_MTX_FILENAME+self.EXT
        if _os.path.isfile(filename):
            copy_ = self.response_matrix.copy()
            self.response_matrix = _np.loadtxt(filename)
            if not self._calc_matrices():
                self.response_matrix = copy_
                return
            self._call_callback('Log-Mon', 'Loading RSP Matrix from file.')
            self._call_callback('RSPMatrix-RB',
                                list(self.response_matrix.flatten()))

    def _save_resp_matrix(self, mat):
        self._call_callback('Log-Mon', 'Saving RSP Matrix to file')
        _np.savetxt(self.RSP_MTX_FILENAME+self.EXT, mat)
