import numpy as _np
import copy as _copy
from threading import Event as _Event
from threading import Thread as _Thread
from epics import PV as _PV
from siriuspy.epics.fake_pv import PVFake as _PVFake
from siriuspy.epics.fake_pv import add_to_database as _add_to_database
from .pvs import pvs_definitions as pvDB
from .pvs import fft_writable_props

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

    def __init__(self, bpm_name, prefix='', callback=None):
        self.pv_prefix = prefix + bpm_name + ':'
        _add_to_database(pvDB, prefix=self.pv_prefix)
        self.pvs = dict()
        self.bpm_name = bpm_name
        for pv, db in pvDB.items():
            self.pvs[pv] = self._PV_class(self.pv_prefix + pv)
            if callback:
                self.pvs[pv].add_callback(callback)

    for pv, db in pvDB.items():
        prop, suf = get_prop_and_suffix(pv)
        # define methods for calling and setting callbacks for each pv
        exec(_callbacks.format(prop, suf, pv))
        # Create all properties
        exec(_rb_prop.format(prop, suf, pv))
        if suf in ('sp', 'cmd', 'sel') or pv in fft_writable_props:
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

    def __init__(self, bpm_name, prefix='', callback=None):
        super().__init__(bpm_name=bpm_name, prefix=prefix, callback=callback)
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
            if name.endswith('ArrayData-Mon'):
                self.pvs[name].add_callback(self.__update_stats_fft)

        # simulate triggered acquisition (includes single pass)
        self.pvs['ACQTriggerEvent-Sts'].add_callback(self.__do_acquisition)

        # simulate Post Mortem
        self.pvs['ACQ_PMTriggerEvent-Sts'].add_callback(self.__do_post_mortem)

        # create timer to simulate slow measurements:
        self.timer = _Timer(0.5, self.__monitor_pos)
        self.timer.start()

    def set_ref_pos(self, x=None, y=None, q=None):
        if x is not None:
            self._x_ref = float(x)
        if y is not None:
            self._y_ref = float(y)
        if q is not None:
            self._q_ref = float(q)

    def __update_stats_fft(self, pvname, value, **kws):
        self._calc_statistics_fft(pvname, value)

    def __calc_statistics_fft(self, pvname, value):
        fft = _np.fft.rfft(value)
        freq = _np.fft.rfftfreq(len(fft))
        name = pvname.replace(self.pv_prefix, '')[:-4]
        self.pvs[name+'_STATSMaxValue_RBV'].value = value.max()
        self.pvs[name+'_STATSMeanValue_RBV'].value = value.min()
        self.pvs[name+'_STATSMinValue_RBV'].value = value.mean()
        self.pvs[name+'_STATSSigma_RBV'].value = value.std()
        self.pvs[name+'FFTFreq-Mon'].value = freq
        self.pvs[name+'FFTData.AMP'].value = _np.abs(fft)
        self.pvs[name+'FFTData.PHA'].value = _np.angle(fft)
        self.pvs[name+'FFTData.SIN'].value = fft.imag
        self.pvs[name+'FFTData.COS'].value = fft.real
        self.pvs[name+'FFTData.WAVN'].value = freq

    def __set_readback(self, pvname, value=None, **kws):
        name = pvname.replace(self.pv_prefix, '')
        if name.endswith('SP'):
            name = name[:-2] + 'RB'
        elif name.endswith('Sel'):
            name = name[:-3] + 'Sts'
        else:
            raise Exception('Internal Error: PV is not SP nor Sel.')
        self.pvs[name].value = value

    def __do_post_mortem(self, pvname, value=None, **kws):
        self.__do_acquisition(pvname, value=value, post_morten=True, **kws)

    def __do_acquisition(self, pvname, value=None, post_morten=False, **kws):
        if value:
            returns
        pref = 'ACQ'
        pref += '_PM' if post_morten else ''
        if not post_morten and self.pvs[pref+'BPMMode-Sts'].value:
            self.__do_single_pass(pvname, value=value, **kws)

        self.pvs[pref+'Status-Sts'].value = 2
        acq_type = self.pvs[pref+'Channel-Sts'].char_value
        acq_spl_pre = self.pvs[pref+'SamplesPre-RB']
        acq_spl_pos = self.pvs[pref+'SamplesPost-RB']
        acq_shots = self.pvs[pref+'Shots-RB']
        nr = (acq_spl_pre + acq_spl_pos) * acq_shots
        t = _np.arange(nr)
        freq = _np.random.rand()/10
        phi = _np.random.rand()*_np.pi
        amp = _np.random.rand()*1e-4
        posx = amp*_np.cos(2*_np.pi*freq*t + phi) + self._x

        freq = _np.random.rand()/10
        phi = _np.random.rand()*_np.pi
        amp = _np.random.rand()*5e-5
        posy = amp*_np.cos(2*_np.pi*freq*t + phi) + self._y

        freq = _np.random.rand()/10
        phi = _np.random.rand()*_np.pi
        amp = _np.random.rand()*1e-5
        posq = amp*_np.cos(2*_np.pi*freq*t + phi) + self._q

        poss = _np.ones(nr)
        M = self.M
        Amps = _np.dot(M, _np.array([posx, posy, posq, poss]))
        dt_nm = 'PM_' if post_morten else 'GEN_'
        self.pvs[dt_nm+'AArrayData-Mon'].value = Amps[0, :]
        self.pvs[dt_nm+'BArrayData-Mon'].value = Amps[1, :]
        self.pvs[dt_nm+'CArrayData-Mon'].value = Amps[2, :]
        self.pvs[dt_nm+'DArrayData-Mon'].value = Amps[3, :]
        if not acq_type.startswith('adc'):
            self.pvs[dt_nm+'XArrayData-Mon'].value = posx
            self.pvs[dt_nm+'YArrayData-Mon'].value = posy
            self.pvs[dt_nm+'QArrayData-Mon'].value = posq
            self.pvs[dt_nm+'SumArrayData-Mon'].value = poss
        self.pvs[pref+'Status-Sts'].value = 0

    def __monitor_pos(self):
        self._x = self._x_ref + _np.random.rand()*80
        self._y = self._y_ref + _np.random.rand()*80
        self._q = self._q_ref + _np.random.rand()*80
        self.pvs['PosX-Mon'].value = self._x
        self.pvs['PosY-Mon'].value = self._y
        self.pvs['PosQ-Mon'].value = self._q
        self.pvs['Sum-Mon'].value = 1 + _np.random.rand()*80e-9
        v = _np.array([[self._x], [self._y], [self._q], [1]])
        amps = _np.dot(self.M, v)
        self.pvs['AmplA-Mon'].value = amps[0]
        self.pvs['AmplB-Mon'].value = amps[1]
        self.pvs['AmplC-Mon'].value = amps[2]
        self.pvs['AmplD-Mon'].value = amps[3]

    def __do_single_pass(self, pvname, value=None, **kws):
        if not self.opmode_sts:
            return

        self.pvs['ACQStatus-Sts'].value = 2
        acq_spl_pre = self.pvs['ACQSamplesPre-RB']
        acq_spl_pos = self.pvs['ACQSamplesPost-RB']
        acq_shots = self.pvs['ACQShots-RB']
        nr = (acq_spl_pre + acq_spl_pos) * acq_shots
        t = _np.linspace(0, 1, nr)

        t0 = _np.random.rand()
        sig = _np.random.rand()*3e-2
        amp = _np.random.rand()*1e-3
        posx = amp*_np.exp(-(t-t0)**2/2/sig**2)

        sig = _np.random.rand()*3e-2
        amp = _np.random.rand()*1e-3
        posy = amp*_np.exp(-(t-t0)**2/2/sig**2)

        sig = _np.random.rand()*3e-2
        amp = _np.random.rand()*1e-3
        posq = amp*_np.exp(-(t-t0)**2/2/sig**2)

        poss = _np.ones(nr)
        M = self.M
        Amps = _np.dot(M, _np.array([posx, posy, posq, poss]))
        self.pvs['SPPosX-Mon'].value = posx.mean()
        self.pvs['SPPosY-Mon'].value = posy.mean()
        self.pvs['SPPosQ-Mon'].value = posq.mean()
        self.pvs['SPSum-Mon'].value = poss.mean()
        self.pvs['SPAmplA-Mon'].value = Amps[0, :].mean()
        self.pvs['SPAmplB-Mon'].value = Amps[1, :].mean()
        self.pvs['SPAmplC-Mon'].value = Amps[2, :].mean()
        self.pvs['SPAmplD-Mon'].value = Amps[3, :].mean()
        self.pvs['SP_AArrayData-Mon'].value = Amps[0, :]
        self.pvs['SP_BArrayData-Mon'].value = Amps[1, :]
        self.pvs['SP_CArrayData-Mon'].value = Amps[2, :]
        self.pvs['SP_DArrayData-Mon'].value = Amps[3, :]
        self.pvs['ACQStatus-Sts'].value = 0
