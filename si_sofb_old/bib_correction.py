
import numpy as _np
import epics as _epics
import bib_pv as _bib_pv
import bib_status as _bib_status
from time import sleep


_respm_hv = None
_respm_h = None
_respm_v = None
_respm_h_v = None
_inv_respm_hv = None
_inv_respm_h = None
_inv_respm_v = None
_inv_respm_h_v = None
_respm_hv_f = None
_respm_h_f = None
_respm_v_f = None
_respm_h_v_f = None
_inv_respm_hv_f = None
_inv_respm_h_f = None
_inv_respm_v_f = None
_inv_respm_h_v_f = None
_reforbit_xy = None
_reforbit_x = None
_reforbit_y = None


def set_reforbit():
    global _reforbit_xy, _reforbit_x, _reforbit_y
    _reforbit_x = _np.copy(_bib_status.get_reforbit('x'))[_bib_status.get_device_idx('bpm_x')]
    _reforbit_y = _np.copy(_bib_status.get_reforbit('y'))[_bib_status.get_device_idx('bpm_y')]
    _reforbit_xy = _np.concatenate((_reforbit_x, _reforbit_y))[0]


def get_reforbit(plane = ''):
    if plane.lower() == 'x':
        return _reforbit_x
    elif plane.lower() == 'y':
        return _reforbit_y
    elif plane.lower() == 'xy':
        return _reforbit_xy


def set_respm():
    global _respm_h, _respm_v, _respm_hv, _respm_h_v, _respm_h_f, _respm_v_f, _respm_hv_f, _respm_h_v_f
    _respm_hv_f = _np.copy(_bib_status.get_respm()[_bib_status.get_device_idx('bpm_xy'),:][:,_bib_status.get_device_idx('chcv_f')])
    _respm_hv = _np.copy(_respm_hv_f[:,:-1])
    _respm_h = _np.copy(_respm_hv[:len(_bib_status.get_device_idx('bpm_x')),:len(_bib_status.get_device_idx('ch'))])
    _respm_v = _np.copy(_respm_hv[-len(_bib_status.get_device_idx('bpm_y')):,-len(_bib_status.get_device_idx('cv')):])
    _respm_h_v_f = _np.copy(_respm_hv_f)
    _respm_h_v_f[:len(_bib_status.get_device_idx('bpm_x')),len(_bib_status.get_device_idx('ch')):-1] = 0
    _respm_h_v_f[-len(_bib_status.get_device_idx('bpm_y')):,:len(_bib_status.get_device_idx('ch'))] = 0
    _respm_h_v = _np.copy(_respm_h_v_f[:,:-1])
    _respm_h_f = _np.copy(_respm_h)
    _respm_h_f = _np.c_[_respm_h_f,_respm_hv_f[:len(_bib_status.get_device_idx('bpm_x')),-1]]
    _respm_v_f = _np.copy(_respm_v)
    _respm_v_f = _np.c_[_respm_v_f,_respm_hv_f[-len(_bib_status.get_device_idx('bpm_y')):,-1]]


def get_respm(ctype = ''):
    if ctype.lower() == 'h':
        return _respm_h
    elif ctype.lower() == 'v':
        return _respm_v
    elif ctype.lower() == 'h_v':
        return _respm_h_v
    elif ctype.lower() == 'hv':
        return _respm_hv
    elif ctype.lower() == 'h_f':
        return _respm_h_f
    elif ctype.lower() == 'v_f':
        return _respm_v_f
    elif ctype.lower() == 'h_v_f':
        return _respm_h_v_f
    elif ctype.lower() == 'hv_f':
        return _respm_hv_f


def set_inv_respm():
    global _inv_respm_h, _inv_respm_v, _inv_respm_hv, _inv_respm_h_v, _inv_respm_h_f, _inv_respm_v_f, _inv_respm_hv_f, _inv_respm_h_v_f
    if (_respm_hv_f != []) and (_respm_hv_f is not None):
        _inv_respm_hv = _calculate_inv_respm(_respm_hv)
        _inv_respm_h = _calculate_inv_respm(_respm_h)
        _inv_respm_v = _calculate_inv_respm(_respm_v)
        _inv_respm_h_v = _calculate_inv_respm(_respm_h_v)
        _inv_respm_hv_f = _calculate_inv_respm(_respm_hv_f)
        _inv_respm_h_f = _calculate_inv_respm(_respm_h_f)
        _inv_respm_v_f = _calculate_inv_respm(_respm_v_f)
        _inv_respm_h_v_f = _calculate_inv_respm(_respm_h_v_f)


def get_inv_respm(ctype = ''):
    if ctype.lower() == 'h':
        return _inv_respm_h
    elif ctype.lower() == 'v':
        return _inv_respm_v
    elif ctype.lower() == 'h_v':
        return _inv_respm_h_v
    elif ctype.lower() == 'hv':
        return _inv_respm_hv
    elif ctype.lower() == 'h_f':
        return _inv_respm_h_f
    elif ctype.lower() == 'v_f':
        return _inv_respm_v_f
    elif ctype.lower() == 'h_v_f':
        return _inv_respm_h_v_f
    elif ctype.lower() == 'hv_f':
        return _inv_respm_hv_f


def calc_kick(orbit_full = None, ctype = ''):
    kick, reforbit, inv_respm = None, None, None
    if ctype.lower() == 'h' or ctype.lower() == 'v' or ctype.lower() == 'h_f' or ctype.lower() == 'v_f':
        if ctype.lower() == 'h':
            orbit = orbit_full[_bib_status.get_device_idx('bpm_x')]
            reforbit = get_reforbit('x')
            inv_respm = get_inv_respm('h')
        elif ctype.lower() == 'v':
            orbit = orbit_full[_bib_status.get_device_idx('bpm_y')]
            reforbit = get_reforbit('y')
            inv_respm = get_inv_respm('v')
        elif ctype.lower() == 'h_f':
            orbit = orbit_full[_bib_status.get_device_idx('bpm_x')]
            reforbit = get_reforbit('x')
            inv_respm = get_inv_respm('h_f')
        elif ctype.lower() == 'v_f':
            orbit = orbit_full[_bib_status.get_device_idx('bpm_y')]
            reforbit = get_reforbit('y')
            inv_respm = get_inv_respm('v_f')
    elif ctype.lower() == 'h_v' or ctype.lower() == 'hv' or ctype.lower() == 'h_v_f' or ctype.lower() == 'hv_f':
        orbit = orbit_full[_bib_status.get_device_idx('bpm_xy')]
        if ctype.lower() == 'hv':
            reforbit = get_reforbit('xy')
            inv_respm = get_inv_respm('hv')
        elif ctype.lower() == 'h_v':
            reforbit = get_reforbit('xy')
            inv_respm = get_inv_respm('h_v')
        elif ctype.lower() == 'hv_f':
            reforbit = get_reforbit('xy')
            inv_respm = get_inv_respm('hv_f')
        elif ctype.lower() == 'h_v_f':
            reforbit = get_reforbit('xy')
            inv_respm = get_inv_respm('h_v_f')
    if reforbit is not None and inv_respm is not None:
        kick = _np.dot(-inv_respm,(reforbit-orbit))
    return kick


def _calculate_inv_respm(respm = None):
    U, s, V = _np.linalg.svd(respm, full_matrices = False)
    S = _np.diag(s)
    inv_respm = _np.dot(_np.dot(_np.transpose(V),_np.linalg.pinv(S)),_np.transpose(U))
    return inv_respm
