import numpy as _np
import copy as _copy
from threading import Event as _Event
from threading import Thread as _Thread
from epics import PV as _PV
from siriuspy.epics.fake_pv import PVFake as _PVFake
from siriuspy.epics.fake_pv import add_to_database as _add_to_database
from .pvs import pvs_definitions as pvDB
from .pvs import additional_acq_data_props as _additional_acq_data_props
from .pvs import additional_acq_data_props as _additional_acq_data_props
from .pvs import existent_acq_data_props as _existent_acq_data_props
from .pvs import max_number_of_shots as _max_number_of_shots


def get_prop_and_suffix(name):
    prop = name.lower().replace('-', '_').replace('.', '')
    prop = prop.split('_')
    suf = prop[1] if len(prop) > 1 else ''
    prop = prop[0]
    return prop, suf


class _Timer(_Thread):
    def __init__(self, interval, function, args=tuple(), niter=100):
        super().__init__(daemon=True)
        self.interval = interval
        self.function = function
        self.args = args
        self.stopped = _Event()
        self.run_now = True

    def run(self):
        while not self.stopped.wait(self.interval):
            if self.run_now:
                self.function(*self.args)

    def restart(self):
        self.run_now = True

    def stop(self):
        self.run_now = False


_sp_prop = """
@{0}_{1}.setter
def {0}_{1}(self, new_val):
    if not self.pvs['{2}'].connected:
        return
    count = pvDB['{2}'].get('count', 1)
    if count > 1:
        self.pvs['{2}'].value = _np.array(new_val)
    else:
        self.pvs['{2}'].value = new_val
"""

_rb_prop = """
@property
def {0}_{1}(self):
    if self.pvs['{2}'].connected:
        return _copy.deepcopy(self.pvs['{2}'].value)
"""

_callbacks = """
def {0}_{1}_add_callback(self, callback, index=None):
    return self.pvs['{2}'].add_callback(callback, index)

def {0}_{1}_remove_callback(self, index):
    self.pvs['{2}'].remove_callback(index)

def {0}_{1}_clear_callbacks(self):
    self.pvs['{2}'].clear_callbacks()

def {0}_{1}_run_callbacks(self):
    self.pvs[{2}].run_callbacks()
"""


class BPM:
    _PV_class = None
    _PV_add_class = None

    def __init__(self, bpm_name, prefix=''):
        self.pv_prefix = prefix + bpm_name + ':'
        _add_to_database(pvDB, prefix=self.pv_prefix)
        self.pvs = dict()
        self.bpm_name = bpm_name
        for pv, db in pvDB.items():
            if pv in _additional_acq_data_props:
                self.pvs[pv] = self._PV_add_class(self.pv_prefix + pv)
            else:
                self.pvs[pv] = self._PV_class(self.pv_prefix + pv)
            if self._PV_add_class == _PVFake and\
               pv in _existent_acq_data_props and\
               pv.endswith('-Mon'):
                self.pvs[pv].add_callback(self.__update_shots_pvs)

    def __update_shots_pvs(self, pvname, value, **kwargs):
        self._calc_statistics_fft(pvname, value, is_shot=True)

    def _calc_statistics_fft(self, pvname, value, is_shot=False):
        nr_shots = self.acqnrshots_rb if is_shot else 1
        value = value.reshape(nr_shots, -1)
        max_ = value.max(axis=1)
        min_ = value.min(axis=1)
        ave_ = value.mean(axis=1)
        std_ = value.std(axis=1)
        nr_points = value.shape[1]
        fft = _np.fft.rfft(value)
        freq = _np.fft.rfftfreq(nr_points)
        loop = list(range(1, _max_number_of_shots+1)) if is_shot else (0,)
        for i in loop:
            ind, fac = (i-1, 1.0) if i <= nr_shots else (0, 0.0)
            name = pvname.replace(self.pv_prefix, '')[:-4]
            if is_shot:
                name += 'Shot{0}'.format(i)
                self.pvs[name+'-Mon'].value = value[ind, :] * fac
            self.pvs[name+'Max'].value = max_[ind] * fac
            self.pvs[name+'Min'].value = min_[ind] * fac
            self.pvs[name+'Ave'].value = ave_[ind] * fac
            self.pvs[name+'Std'].value = std_[ind] * fac
            self.pvs[name+'FFT.SPAN'].value = nr_points
            self.pvs[name+'FFT.FREQ'].value = freq
            self.pvs[name+'FFT.AMP'].value = _np.abs(fft[ind, :]) * fac
            self.pvs[name+'FFT.PHA'].value = _np.angle(fft[ind, :]) * fac
            self.pvs[name+'FFT.SIN'].value = fft[ind, :].imag * fac
            self.pvs[name+'FFT.COS'].value = fft[ind, :].real * fac

    for pv, db in pvDB.items():
        prop, suf = get_prop_and_suffix(pv)
        # define methods for calling and setting callbacks for each pv
        exec(_callbacks.format(prop, suf, pv))
        # Create all properties
        exec(_rb_prop.format(prop, suf, pv))
        if suf in ('sp', 'cmd', 'sel'):
            exec(_sp_prop.format(prop, suf, pv))
        else:
            exec(_rb_prop.format(prop, suf, pv))
    del pv, db, prop, suf


class BPMEpics(BPM):
    _PV_class = _PV
    _PV_add_class = _PVFake


class BPMFake(BPM):
    _PV_class = _PVFake
    _PV_add_class = _PVFake
    M = _np.array([[-2, -2,  0,  0],
                   [-2,  0,  0, -2],
                   [-2,  0, -2,  0],
                   [-2, -2, -2, -2]])

    def __init__(self, bpm_name, prefix=''):
        super().__init__(bpm_name=bpm_name, prefix=prefix)
        self._x_ref = 0
        self._y_ref = 0
        self._q_ref = 0
        self._x = 0
        self._y = 0
        self._q = 0
        for name, pv in pvDB.items():
            prop, suf = get_prop_and_suffix(name)
            # connect changes in sp and sel pvs to rb and sts pvs:
            if suf in ('sp', 'sel'):
                self.pvs[name].add_callback(self.__set_readback)
            # update statistics after measurements
            if name in _existent_acq_data_props and\
               name.endswith('-Mon'):
                self.pvs[name].add_callback(self.__update_stats_fft)

        # simulate triggered acquisition
        self.pvs['AcqStart-Cmd'].add_callback(self.__do_acquisition)

        # simulate single pass
        self.pvs['SglStart-Cmd'].add_callback(self.__do_single_pass)

        # create timer to simulate slow measurements:
        self.timer = _Timer(0.5, self.__monitor_pos)
        self.timer.start()

        # change operation mode
        self.pvs['OpMode-Sel'].add_callback(self.__change_operation_mode)

    def set_ref_pos(self, x=None, y=None, q=None):
        if x is not None:
            self._x_ref = float(x)
        if y is not None:
            self._y_ref = float(y)
        if q is not None:
            self._q_ref = float(q)

    def __update_stats_fft(self, pvname, value, **kws):
        self._calc_statistics_fft(pvname, value, is_shot=False)

    def __set_readback(self, pvname, value=None, **kws):
        name = pvname.replace(self.pv_prefix, '')
        if name.endswith('SP'):
            name = name[:-2] + 'RB'
        elif name.endswith('Sel'):
            name = name[:-3] + 'Sts'
        else:
            raise Exception('Internal Error: PV is not SP nor Sel.')
        self.pvs[name].value = value

    def __change_operation_mode(self, pvname, value, **kws):
        if value:
            self.timer.stop()
        else:
            self.timer.restart()

    def __do_acquisition(self, pvname, value=None, **kws):
        if self.opmode_sts:
            return

        self.pvs['AcqState-Sts'].value = 2
        acq_type = self.acqrate_sts
        acq_type = self.pvs['AcqRate-Sts'].enum_strs[acq_type]
        acq_spl_pre = self.acqnrsmplspre_rb
        acq_spl_pos = self.acqnrsmplspos_rb
        acq_shots = self.acqnrshots_rb
        nr = (acq_spl_pre + acq_spl_pos) * acq_shots
        t = _np.linspace(0, 1, nr)
        freq = _np.random.rand()/2
        phi = _np.random.rand()*_np.pi
        amp = _np.random.rand()*1e-4
        posx = amp*_np.cos(2*_np.pi*freq*t + phi) + self._x

        freq = _np.random.rand()/2
        phi = _np.random.rand()*_np.pi
        amp = _np.random.rand()*5e-5
        posy = amp*_np.cos(2*_np.pi*freq*t + phi) + self._y

        freq = _np.random.rand()/2
        phi = _np.random.rand()*_np.pi
        amp = _np.random.rand()*1e-5
        posq = amp*_np.cos(2*_np.pi*freq*t + phi) + self._q

        poss = _np.ones(nr)
        M = self.M
        Amps = _np.dot(M, _np.array([posx, posy, posq, poss]))
        if acq_type in ('TbT', 'FOFB'):
            self.pvs[acq_type+'PosX-Mon'].value = posx
            self.pvs[acq_type+'PosY-Mon'].value = posy
            self.pvs[acq_type+'PosQ-Mon'].value = posq
            self.pvs[acq_type+'PosS-Mon'].value = poss
            self.pvs[acq_type+'AmpA-Mon'].value = Amps[0, :]
            self.pvs[acq_type+'AmpB-Mon'].value = Amps[1, :]
            self.pvs[acq_type+'AmpC-Mon'].value = Amps[2, :]
            self.pvs[acq_type+'AmpD-Mon'].value = Amps[3, :]
        else:
            self.pvs[acq_type+'AntA-Mon'].value = Amps[0, :]
            self.pvs[acq_type+'AntB-Mon'].value = Amps[1, :]
            self.pvs[acq_type+'AntC-Mon'].value = Amps[2, :]
            self.pvs[acq_type+'AntD-Mon'].value = Amps[3, :]
        self.pvs['AcqState-Sts'].value = 0

    def __monitor_pos(self):
        self._x = self._x_ref + _np.random.rand()*80e-9
        self._y = self._y_ref + _np.random.rand()*80e-9
        self._q = self._q_ref + _np.random.rand()*80e-9
        self.pvs['PosX-Mon'].value = self._x
        self.pvs['PosY-Mon'].value = self._y
        self.pvs['PosQ-Mon'].value = self._q
        self.pvs['PosS-Mon'].value = 1 + _np.random.rand()*80e-9
        v = _np.array([[self._x], [self._y], [self._q], [1]])
        amps = _np.dot(self.M, v)
        self.pvs['AmpA-Mon'].value = amps[0]
        self.pvs['AmpB-Mon'].value = amps[1]
        self.pvs['AmpC-Mon'].value = amps[2]
        self.pvs['AmpD-Mon'].value = amps[3]

    def __do_single_pass(self, pvname, value=None, **kws):
        if not self.opmode_sts:
            return

        self.pvs['SglState-Sts'].value = 2
        t = _np.linspace(0, 1, 1000)

        t0 = _np.random.rand()
        sig = _np.random.rand()*3e-2
        amp = _np.random.rand()*1e-3
        posx = amp*_np.exp((t-t0)**2/2/sig**2)

        sig = _np.random.rand()*3e-2
        amp = _np.random.rand()*1e-3
        posy = amp*_np.exp((t-t0)**2/2/sig**2)

        sig = _np.random.rand()*3e-2
        amp = _np.random.rand()*1e-3
        posq = amp*_np.exp((t-t0)**2/2/sig**2)

        poss = _np.ones(1000)
        M = self.M
        Amps = _np.dot(M, _np.array([posx, posy, posq, poss]))
        self.pvs['SglPosX-Mon'].value = posx.mean()
        self.pvs['SglPosY-Mon'].value = posy.mean()
        self.pvs['SglPosQ-Mon'].value = posq.mean()
        self.pvs['SglPosS-Mon'].value = poss.mean()
        self.pvs['SglAmpA-Mon'].value = Amps[0, :].mean()
        self.pvs['SglAmpB-Mon'].value = Amps[1, :].mean()
        self.pvs['SglAmpC-Mon'].value = Amps[2, :].mean()
        self.pvs['SglAmpD-Mon'].value = Amps[3, :].mean()
        self.pvs['SglAntA-Mon'].value = Amps[0, :]
        self.pvs['SglAntB-Mon'].value = Amps[1, :]
        self.pvs['SglAntC-Mon'].value = Amps[2, :]
        self.pvs['SglAntD-Mon'].value = Amps[3, :]
        self.pvs['SglState-Sts'].value = 0
