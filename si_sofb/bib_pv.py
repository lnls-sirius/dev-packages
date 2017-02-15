
import epics as _epics
import numpy as _np
from time import sleep
import bib_status as _bib_status


_PREFIX = 'VA-'
_SUFIX = ''
_SLEEPTIME = 0.1

PV_RF_FREQUENCY = _PREFIX + 'SIRF-FREQUENCY' #virtual accelerator PV
#PV_RF_FREQUENCY = 'DIG-RSSMX100A-0:GENERAL:Freq' #real RF generator PV

global _pvs
_pvs = {}


def _create_pv_names():
    pvnames_bpm_x = []
    pvnames_bpm_y = []
    pvnames_ch = []
    pvnames_cv = []
    for i, device in enumerate(_bib_status.devicenames_bpm):
        pvnames_bpm_x.append(_PREFIX + 'SIDI-' + device + ':MONIT:X')
        pvnames_bpm_y.append(_PREFIX + 'SIDI-' + device + ':MONIT:Y')
        _pvs[pvnames_bpm_x[i]] = _epics.PV(pvnames_bpm_x[i])
        _pvs[pvnames_bpm_y[i]] = _epics.PV(pvnames_bpm_y[i])
    for i, device in enumerate(_bib_status.devicenames_ch):
        pvnames_ch.append(_PREFIX + 'SIPS-' + device + _SUFIX)
        _pvs[pvnames_ch[i]] = _epics.PV(pvnames_ch[i])
    for i, device in enumerate(_bib_status.devicenames_cv):
        pvnames_cv.append(_PREFIX + 'SIPS-' + device + _SUFIX)
        _pvs[pvnames_cv[i]] = _epics.PV(pvnames_cv[i])
    _pvs[_PREFIX + 'SIDI-BPM-FAM:MONIT:X'] = _epics.PV(_PREFIX + 'SIDI-BPM-FAM:MONIT:X')
    _pvs[_PREFIX + 'SIDI-BPM-FAM:MONIT:Y'] = _epics.PV(_PREFIX + 'SIDI-BPM-FAM:MONIT:Y')
    _pvs[PV_RF_FREQUENCY] = _epics.PV(PV_RF_FREQUENCY)
    return pvnames_bpm_x, pvnames_bpm_y, pvnames_ch, pvnames_cv


_pvnames_bpm_x, _pvnames_bpm_y, _pvnames_ch, _pvnames_cv = _create_pv_names()


def get_orbit(plane = ''):
    if plane.lower() == 'x':
        orbit = _pvs[_PREFIX + 'SIDI-BPM-FAM:MONIT:X'].value
    elif plane.lower() == 'y':
        orbit = _pvs[_PREFIX + 'SIDI-BPM-FAM:MONIT:Y'].value
    elif plane.lower() == 'xy':
        orbit = []
        orbit.extend(_pvs[_PREFIX + 'SIDI-BPM-FAM:MONIT:X'].value)
        orbit.extend(_pvs[_PREFIX + 'SIDI-BPM-FAM:MONIT:Y'].value)
    return _np.array(orbit)


def get_kick(ctype = ''):
    kick = []
    if ctype.lower() == 'h' or ctype.lower() == 'h_f':
        pvnames_c = _pvnames_ch[:]
        if ctype.lower() == 'h_f':
            pvnames_c.extend([PV_RF_FREQUENCY])
    elif ctype.lower() == 'v' or ctype.lower() == 'v_f':
        pvnames_c = _pvnames_cv[:]
        if ctype.lower() == 'v_f':
            pvnames_c.extend([PV_RF_FREQUENCY])
    elif ctype.lower() == 'hv' or ctype.lower() == 'hv_f' or ctype.lower() == 'h_v' or ctype.lower() == 'h_v_f':
        pvnames_c = []
        pvnames_c.extend(_pvnames_ch)
        pvnames_c.extend(_pvnames_cv)
        if ctype.lower() == 'hv_f' or ctype.lower() == 'h_v_f':
            pvnames_c.extend([PV_RF_FREQUENCY])
    for pvname in pvnames_c:
        kick.append(_pvs[pvname].value)
    return _np.array(kick)


def add_kick(delta_kick = None, ctype = '', weight = [1]):
    kick0_full = get_kick(ctype)
    if ctype.lower() == 'h' or ctype.lower() == 'h_f':
        plane = 'x'
        pvnames_c = list(_np.asarray(_pvnames_ch)[_bib_status.get_device_idx('ch')])
        kick0 = kick0_full[_bib_status.get_device_idx('ch')]
        weighted_kick = weight[0]*delta_kick[:len(_bib_status.get_device_idx('ch'))]
    elif ctype.lower() == 'v' or ctype.lower() == 'v_f':
        plane = 'y'
        pvnames_c = list(_np.asarray(_pvnames_cv)[_bib_status.get_device_idx('cv')])
        kick0 = kick0_full[_bib_status.get_device_idx('cv')]
        weighted_kick = weight[0]*delta_kick[:len(_bib_status.get_device_idx('cv'))]
    elif ctype.lower() == 'hv' or ctype.lower() == 'hv_f' or ctype.lower() == 'h_v' or ctype.lower() == 'h_v_f':
        plane = 'xy'
        pvnames_c = []
        pvnames_c.extend(_np.asarray(_pvnames_ch)[_bib_status.get_device_idx('ch')])
        pvnames_c.extend(_np.asarray(_pvnames_cv)[_bib_status.get_device_idx('cv')])
        kickh_full = kick0_full[:len(_pvnames_ch)]
        kickv_full = kick0_full[len(_pvnames_ch):]
        kickh0 = kickh_full[_bib_status.get_device_idx('ch')]
        kickv0 = kickv_full[_bib_status.get_device_idx('cv')]
        kick0 = _np.concatenate((kickh0, kickv0), axis=0)
        weighted_kickh = weight[0]*delta_kick[:len(_bib_status.get_device_idx('ch'))]
        weighted_kickv = weight[1]*delta_kick[len(_bib_status.get_device_idx('ch')):(len(_bib_status.get_device_idx('ch')) + len(_bib_status.get_device_idx('cv')))]
        weighted_kick = _np.concatenate((weighted_kickh, weighted_kickv))
    if ctype.lower() == 'h_f' or ctype.lower() == 'v_f' or ctype.lower() == 'hv_f' or ctype.lower() == 'h_v_f':
        pvnames_c.extend([PV_RF_FREQUENCY])
        kick0 = _np.append(kick0, kick0_full[-1])
        weighted_kick = _np.append(weighted_kick, delta_kick[-1])
        kick = kick0 + weighted_kick
        if any(_np.where(abs(kick[:-1])>10, True, False)): return 'failed'
    else:
        kick = kick0 + weighted_kick
        if any(_np.where(abs(kick)>10, True, False)): return 'failed'
    old_orbit = get_orbit(plane)
    for i, pvname in enumerate(pvnames_c):
        _pvs[pvname].value = kick[i]
    _meas_new_orbit(old_orbit, plane) #delay for update the closed orbit


def _meas_new_orbit(old_orbit, plane):
    while True:
        orbit = get_orbit(plane)
        if all(orbit != old_orbit): break
        sleep(_SLEEPTIME)
    return orbit


def meas_respm(ctype = '', interruption_event = None):
    sleep(6) #delay for waiting correction finalise
    delta_kick = 0.31833 #hardware units
    #delta_kick = 10e-06 #physics units
    if ctype.lower() == 'h' or ctype.lower() == 'h_f':
        pvnames_bpm = _pvnames_bpm_x[:]
        pvnames_c = _pvnames_ch[:]
        plane = 'x'
    elif ctype.lower() == 'v' or ctype.lower() == 'v_f':
        pvnames_bpm = _pvnames_bpm_y[:]
        pvnames_c = _pvnames_cv[:]
        plane = 'y'
    elif ctype.lower() == 'hv' or ctype.lower() == 'hv_f':
        pvnames_bpm = []
        pvnames_bpm.extend(_pvnames_bpm_x)
        pvnames_bpm.extend(_pvnames_bpm_y)
        pvnames_c = []
        pvnames_c.extend(_pvnames_ch)
        pvnames_c.extend(_pvnames_cv)
        plane = 'xy'
    elif ctype.lower() == 'h_v' or ctype.lower() == 'h_v_f':
        if ctype.lower() == 'h_v':
            respm = meas_respm('hv', interruption_event)
            respm[:_bib_status.nBPM, _bib_status.nCH:] = 0
        elif ctype.lower() == 'h_v_f':
            respm = meas_respm('hv_f', interruption_event)
            respm[:_bib_status.nBPM, _bib_status.nCH:-1] = 0
        respm[_bib_status.nBPM:, :_bib_status.nCH] = 0
        return respm
    kick0 = get_kick(ctype)
    respm = _np.empty((len(pvnames_bpm), len(pvnames_c)+1))
    old_orbit = get_orbit(plane)
    for i, pvname in enumerate(pvnames_c):
        _pvs[pvname].value = kick0[i] + delta_kick/2.0
        p_orbit = _meas_new_orbit(old_orbit, plane)
        _pvs[pvname].value = kick0[i] - delta_kick/2.0
        n_orbit = _meas_new_orbit(p_orbit, plane)
        _pvs[pvname].value = kick0[i]
        old_orbit = _meas_new_orbit(n_orbit, plane)
        respm[:,i] = (p_orbit-n_orbit)/delta_kick
        if interruption_event.is_set(): return _np.array([])
    if ctype.lower() == 'h_f' or ctype.lower() == 'v_f' or ctype.lower() == 'hv_f':
        delta_freq = 100.0
        freq0_RF = _pvs[PV_RF_FREQUENCY].value
        _pvs[PV_RF_FREQUENCY].value = freq0_RF + delta_freq/2.0
        p_orbit = _meas_new_orbit(old_orbit, plane)
        _pvs[PV_RF_FREQUENCY].value = freq0_RF - delta_freq/2.0
        n_orbit = _meas_new_orbit(p_orbit, plane)
        _pvs[PV_RF_FREQUENCY].value = freq0_RF
        old_orbit = _meas_new_orbit(n_orbit, plane)
        respm[:,-1] = (p_orbit-n_orbit)/delta_freq
    else:
        respm = _np.delete(respm, -1, axis=1)
    return respm
