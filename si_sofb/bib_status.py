
import os as _os
import lnls as _lnls
import numpy as _np


_sidi_bpm_devicenames_fname = _os.path.join(_lnls.folder_root,
'siriusdb', 'recordnames_flatlists', 'dname-bpm.txt')
_sips_ch_devicenames_fname  = _os.path.join(_lnls.folder_root,
'siriusdb', 'recordnames_flatlists', 'dname-ch.txt')
_sips_cv_devicenames_fname  = _os.path.join(_lnls.folder_root,
'siriusdb', 'recordnames_flatlists', 'cv.txt')


def _read_devicename_file(filename):
    with open(filename, 'r') as fp:
        content = fp.read()
    content = content.splitlines()
    devicenames = []
    for line in content:
        line = line.strip()
        if not line or line[0] == '#': continue
        words = line.split()
        devicenames.append(words[0])
    return devicenames


devicenames_bpm = _read_devicename_file(_sidi_bpm_devicenames_fname)
devicenames_ch  = _read_devicename_file(_sips_ch_devicenames_fname)
devicenames_cv  = _read_devicename_file(_sips_cv_devicenames_fname)

_respm_path = './respm/'
_respm_filetype = '.txt'
_respm_slot = 0
_respm_nslots = 3
_respm_data = None
_respm_full = None

_reforbit_x_path = './reforbit_x/'
_reforbit_y_path = './reforbit_y/'
_reforbit_filetype = '.txt'
_reforbit_x_slot = 0
_reforbit_y_slot = 0
_reforbit_nslots = 3
_reforbit_x_data = None
_reforbit_y_data = None
_reforbit_x_full = None
_reforbit_y_full = None

_bpm_sel = None
_ch_sel = None
_cv_sel = None
_idx_bpm = None
_idx_bpm_xy = None
_idx_c_h = None
_idx_c_v = None
_idx_c_hv_f = None

nBPM = len(devicenames_bpm)
nCH = len(devicenames_ch)
nCV = len(devicenames_cv)


def initialize_slot(var_type = None, slot = None):
    global _reforbit_x_data, _reforbit_y_data, _respm_data
    if slot == None:
        if var_type.lower() == 'reforbit_x':
            _reforbit_x_data = _np.empty((nBPM, _reforbit_nslots))
            for i in range(_reforbit_nslots):
                _reforbit_x_data[:,i] = _load(_reforbit_x_path + str(i) + _reforbit_filetype)
        elif var_type.lower() == 'reforbit_y':
            _reforbit_y_data = _np.empty((nBPM, _reforbit_nslots))
            for i in range(_reforbit_nslots):
                _reforbit_y_data[:,i] = _load(_reforbit_y_path + str(i) + _reforbit_filetype)
        elif var_type.lower() == 'respm':
            _respm_data = _np.empty((2*nBPM, nCH+nCV+1, _respm_nslots))
            for i in range(_respm_nslots):
                _respm_data[:,:,i] = _load(_respm_path + str(i) + _respm_filetype)
        elif var_type.lower() == 'all':
            initialize_slot('reforbit_x')
            initialize_slot('reforbit_y')
            initialize_slot('respm')
    else:
        if var_type.lower() == 'reforbit_x':
            _reforbit_x_data[:,slot] = _load(_reforbit_x_path + str(slot) + _reforbit_filetype)
        elif var_type.lower() == 'reforbit_y':
            _reforbit_y_data[:,slot] = _load(_reforbit_y_path + str(slot) + _reforbit_filetype)
        elif var_type.lower() == 'respm':
            _respm_data[:,:,slot] = _load(_respm_path + str(slot) + _respm_filetype)


def set_respm():
    global _respm_full
    _respm_full = _respm_data[:,:,get_respm_slot()]


def get_respm():
    return _respm_full


def set_respm_slot(slot = None):
    global _respm_slot
    _respm_slot = slot


def get_respm_slot():
    return _respm_slot


def update_respm_slot(respm_array = None, reshape = False):
    if reshape:
        respm = _np.reshape(respm_array, (2*nBPM, nCH+nCV+1), order='F')
    else:
        respm = respm_array
    _save(_respm_path + str(get_respm_slot()) + _respm_filetype, respm)
    initialize_slot('respm', get_respm_slot())


def set_reforbit(plane = ''):
    global _reforbit_x_full, _reforbit_y_full
    if plane.lower() == 'x':
        _reforbit_x_full = _reforbit_x_data[:,get_reforbit_slot('x')]
    elif plane.lower() == 'y':
        _reforbit_y_full = _reforbit_y_data[:,get_reforbit_slot('y')]


def get_reforbit(plane = ''):
    if plane.lower() == 'x':
        return _reforbit_x_full
    elif plane.lower() == 'y':
        return _reforbit_y_full


def set_reforbit_slot(slot = None, plane = ''):
    global _reforbit_x_slot, _reforbit_y_slot
    if plane.lower() == 'x': _reforbit_x_slot = slot
    elif plane.lower() == 'y': _reforbit_y_slot = slot


def get_reforbit_slot(plane = ''):
    if plane.lower() == 'x': return _reforbit_x_slot
    elif plane.lower() == 'y': return _reforbit_y_slot


def update_reforbit_slot(reforbit = None, plane = ''):
    if plane.lower() == 'x':
        _save(_reforbit_x_path + str(get_reforbit_slot('x')) + _reforbit_filetype, reforbit)
        initialize_slot('reforbit_x', get_reforbit_slot('x'))
    elif plane.lower() == 'y':
        _save(_reforbit_y_path + str(get_reforbit_slot('y')) + _reforbit_filetype, reforbit)
        initialize_slot('reforbit_y', get_reforbit_slot('y'))


def initialize_device_sel():
    global _bpm_sel, _ch_sel, _cv_sel
    _bpm_sel = _np.ones(nBPM)
    _ch_sel = _np.ones(nCH)
    _cv_sel = _np.ones(nCV)


def set_device_sel(device = '', device_sel = None):
    global _bpm_sel, _ch_sel, _cv_sel
    if device.lower() == 'bpm':
        _bpm_sel = _np.array(device_sel)
    elif device.lower() == 'ch':
        _ch_sel = _np.array(device_sel)
    elif device.lower() == 'cv':
        _cv_sel = _np.array(device_sel)


def get_device_sel(device = ''):
    if device.lower() == 'bpm':
        return _bpm_sel
    elif device.lower() == 'ch':
        return _ch_sel
    elif device.lower() == 'cv':
        return _cv_sel


def set_device_idx(device = ''):
    global _idx_bpm, _idx_bpm_xy, _idx_c_h, _idx_c_v, _idx_c_hv_f
    if device.lower() == 'bpm':
        _idx_bpm = _np.where(_bpm_sel)[0]
        _idx_bpm_xy = _np.where(_np.concatenate((_bpm_sel,_bpm_sel),axis=0))[0]
    elif device.lower() == 'ch':
        _idx_c_h = _np.where(_ch_sel)[0]
        _idx_c_hv_f = _np.where(_np.concatenate((_ch_sel,_cv_sel,[1]),axis=0))[0]
    elif device.lower() == 'cv':
        _idx_c_v = _np.where(_cv_sel)[0]
        _idx_c_hv_f = _np.where(_np.concatenate((_ch_sel,_cv_sel,[1]),axis=0))[0]
    elif device.lower() == 'all':
        set_device_idx('bpm')
        set_device_idx('ch')
        set_device_idx('cv')


def get_device_idx(device = ''):
    if device.lower() == 'bpm_x' or device.lower() == 'bpm_y':
        return _idx_bpm
    elif device.lower() == 'bpm_xy':
        return _idx_bpm_xy
    elif device.lower() == 'ch':
        return _idx_c_h
    elif device.lower() == 'cv':
        return _idx_c_v
    elif device.lower() == 'chcv_f':
        return _idx_c_hv_f


def change_device_status(device = '', devicename = '', status = None):
    global _bpm_sel, _ch_sel, _cv_sel
    if device.lower() == 'bpm':
        idx = devicenames_bpm.index(devicename)
        _bpm_sel[idx] = status
    elif device.lower() == 'ch':
        idx = devicenames_ch.index(devicename)
        _ch_sel[idx] = status
    elif device.lower() == 'cv':
        idx = devicenames_cv.index(devicename)
        _cv_sel[idx] = status


def _load(fname):
    return _np.loadtxt(fname, delimiter=' ')


def _save(fname, var):
    _np.savetxt(fname, var, fmt='%+.8e', delimiter = ' ')
