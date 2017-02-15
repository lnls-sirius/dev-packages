
import os as _os
import lnls as _lnls
import pyaccel as _pyaccel
import numpy as _np
from scipy import io as _io
import sirius as _sirius


_flatfilename = _os.path.join(_lnls.folder_db, 'models_flatfiles', 'si-v16-01-s05-01.txt')


def _read_model():
    global _model
    _model = _pyaccel.lattice.read_flat_file(_flatfilename)


def calculate_respm(ctype = ''):
    if _model is None: _read_model()
    model_family_data = _sirius.si.get_family_data(model)
    index_bpm = model_family_data['bpm']['index']
    index_ch = model_family_data['ch']['index']
    index_cv = model_family_data['cv']['index']
    _pyaccel.tracking.set_6d_tracking(_model)
    kick = 10e-06
    if ctype == 'h' or ctype == 'v':
        if ctype == 'h':
            index_c = index_ch
            kick_polynom = 'hkick_polynom'
            pl = 0
        elif ctype == 'v':
            index_c = index_cv
            kick_polynom = 'vkick_polynom'
            pl = 2
        respm = _np.ones((len(index_bpm), len(index_c)))
        for c, i in enumerate(index_c):
            kick0 = getattr(_model[i], kick_polynom)
            setattr(_model[i], kick_polynom, kick0 + kick/2.0)
            p_co = _pyaccel.tracking.find_orbit6(_model, index_bpm)
            setattr(_model[i], kick_polynom, kick0 - kick/2.0)
            n_co = _pyaccel.tracking.find_orbit6(_model, index_bpm)
            setattr(_model[i], kick_polynom, kick0)
            respm[:,c] = (p_co[pl,:]-n_co[pl,:])/kick
    elif ctype == 'hv':
        index_c = []
        index_c.extend(index_ch)
        index_c.extend(index_cv)
        kick_polynom = 'hkick_polynom'
        respm = _np.ones((2*len(index_bpm), len(index_c)))
        for c, i in enumerate(index_c):
            kick0 = getattr(_model[i], kick_polynom)
            setattr(_model[i], kick_polynom, kick0 + kick/2.0)
            p_co = _pyaccel.tracking.find_orbit6(_model, index_bpm)
            setattr(_model[i], kick_polynom, kick0 - kick/2.0)
            n_co = _pyaccel.tracking.find_orbit6(_model, index_bpm)
            setattr(_model[i], kick_polynom, kick0)
            p = []
            p.extend(p_co[0,:])
            p.extend(p_co[2,:])
            n = []
            n.extend(n_co[0,:])
            n.extend(n_co[2,:])
            respm[:,c] = (_np.array(p)-_np.array(n))/kick
            if i == index_ch[-1]:
                kick_polynom = 'vkick_polynom'
    return respm

#si = _sirius.si.create_accelerator()
#si_elem = _sirius.si.get_family_data(si)
#index_bpm = si_elem['bpm']['index']
#index_ch = si_elem['ch']['index']
#index_cv = si_elem['cv']['index']
#si[13].t_in[0] = 10e-06
#si[13].t_out[0] = -10e-06
#_pyaccel.tracking.set_6d_tracking(si)
#measured_orbit = _pyaccel.tracking.find_orbit6(si, index_bpm)
#measured_orbit_x = measured_orbit[0][:]
#measured_orbit_y = measured_orbit[2][:]
# set_reference_orbit(None, 'x')
# set_reference_orbit(None, 'y')
#set_respm(None, 'x')
#set_respm(None, 'y')
# print('Start')
# respm_h = _api_pv._meas_respm('h')
# _np.savetxt('respm_h_va.txt', respm_h)
# respm_v = _api_pv._meas_respm('v')
# _np.savetxt('respm_v_va.txt', respm_v)
# respm_hv = _api_pv.meas_respm('hv')
# _np.savetxt('respm_hv_va.txt', respm_hv)
# respm_hv = _calculate_respm('hv')
# _np.savetxt('respm_hv_model.txt', respm_hv)
# inv_respm_h = _calculate_inv_respm(respm_h)
# _np.savetxt('inv_respm_h_model.txt', inv_respm_h)
# inv_respm_v = _calculate_inv_respm(respm_v)
# _np.savetxt('inv_respm_v_model.txt', inv_respm_v)
# respm_hv = _np.loadtxt('respm_hv_va.txt')
# inv_respm_hv = _calculate_inv_respm(respm_hv)
# _np.savetxt('inv_respm_hv_va.txt', inv_respm_hv)
# kick_x = cod_correction(measured_orbit_x, 'x')
# kick_y = cod_correction(measured_orbit_y, 'y')
# for i in range(len(index_ch)):
#     si[index_ch[i]].hkick_polynom += kick_x[i]
# corrected_orbit = _pyaccel.tracking.find_orbit6(si, index_bpm)
# corrected_orbit_x = corrected_orbit[0][:]
# _plt.plot(measured_orbit_x*1e06,'k-',label='Disturbed Orbit')
# _plt.plot(_reference_orbit_x*1e06,'r-',label='Reference Orbit')
# _plt.plot(corrected_orbit_x*1e06,'b-',label='Corrected Orbit')
# _plt.legend(loc='upper right')
# _plt.title('Orbit Correction')
# _plt.ylabel('x [nm]')
# frame1 = _plt.gca()
# frame1.axes.xaxis.set_ticklabels([])
# _plt.show()
