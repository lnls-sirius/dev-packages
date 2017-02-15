
from utils import log
import threading
import bib_status as _bib_status
import bib_pv as _bib_pv
import bib_correction as _bib_correction
from time import sleep
from collections import deque
import numpy as _np


class CODCorrectionThread(threading.Thread):

    def __init__(self, name, stop_event, interval):
        """Orbit Correction Thread Object

        Keyword arguments:
        name -- threading object's name
        interval -- processing interval [s]
        stop_event -- event to stop processing

        Class main attribute: mode
        Defines what type of correction should be done.
        0-Off, 1-H, 2-V, 3-H_V, 4-HV, 5-H_F, 6-V_F, 7-H_V_F, 8-HV_F
        """

        self._name = name
        super().__init__(name=self._name, target=self._main, daemon=True)
        self._interval = interval
        self._stop_event = stop_event
        self._mode = 0
        self._autocorr = True

    def cod_correction(self, ctype = ''):
        if ctype.lower() == 'h' or ctype.lower() == 'h_f':
            orbit = self._driver.getParam('SI-GLOB:AP-SOFB.AvgMeasOrbX')
            weight = [self._driver.getParam('SI-GLOB:AP-SOFB.StrthCH')/100]
        elif ctype.lower() == 'v' or ctype.lower() == 'v_f':
            orbit = self._driver.getParam('SI-GLOB:AP-SOFB.AvgMeasOrbY')
            weight = [self._driver.getParam('SI-GLOB:AP-SOFB.StrthCV')/100]
        elif ctype.lower() == 'hv' or ctype.lower() == 'hv_f' or ctype.lower() == 'h_v' or ctype.lower() == 'h_v_f':
            orbit = []
            orbit.extend(self._driver.getParam('SI-GLOB:AP-SOFB.AvgMeasOrbX'))
            orbit.extend(self._driver.getParam('SI-GLOB:AP-SOFB.AvgMeasOrbY'))
            weight = []
            weight.append(self._driver.getParam('SI-GLOB:AP-SOFB.StrthCH')/100)
            weight.append(self._driver.getParam('SI-GLOB:AP-SOFB.StrthCV')/100)
        delta_kick = _bib_correction.calc_kick(_np.array(orbit), ctype)
        status = _bib_pv.add_kick(delta_kick, ctype, weight)
        if str(status).lower() == 'failed':
            self._driver.setParam('SI-GLOB:AP-SOFB.Err', 12)
            self._mode = 0
            self._driver.setParam('SI-GLOB:AP-SOFB.OpMode', 0)
        if not self._autocorr:
            self._mode = 0


    def _main(self):
        _bib_status.initialize_device_sel()
        _bib_status.set_device_idx('all')
        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListBPM', _bib_status.get_device_sel('bpm'))
        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListCH', _bib_status.get_device_sel('ch'))
        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListCV', _bib_status.get_device_sel('cv'))
        _bib_status.initialize_slot(var_type = 'all')
        _bib_status.set_reforbit('x')
        self._driver.setParam('SI-GLOB:AP-SOFB.RefOrbX', _bib_status.get_reforbit('x'))
        _bib_status.set_reforbit('y')
        self._driver.setParam('SI-GLOB:AP-SOFB.RefOrbY', _bib_status.get_reforbit('y'))
        _bib_status.set_respm()
        self._driver.setParam('SI-GLOB:AP-SOFB.RespMat', _bib_status.get_respm())
        _bib_correction.set_reforbit()
        _bib_correction.set_respm()
        _bib_correction.set_inv_respm()
        while not self._stop_event.is_set():
            if self._mode == 1:
                self.cod_correction('h')
            elif self._mode == 2:
                self.cod_correction('v')
            elif self._mode == 3:
                self.cod_correction('h_v')
            elif self._mode == 4:
                self.cod_correction('hv')
            elif self._mode == 5:
                self.cod_correction('h_f')
            elif self._mode == 6:
                self.cod_correction('v_f')
            elif self._mode == 7:
                self.cod_correction('h_v_f')
            elif self._mode == 8:
                self.cod_correction('hv_f')
            else:
                sleep(self._interval)
        else:
            log('exit', 'orbit correction thread')


class MEASOrbitThread(threading.Thread):

    def __init__(self, name, stop_event, interval, n_samples):
        """Orbit Measurement Thread Object

        Keyword arguments:
        name -- threading object's name
        interval -- processing interval [s]
        stop_event -- event to stop processing
        n_samples -- number of measurements to compute orbit average
        """

        self._name = name
        super().__init__(name=self._name, target=self._main, daemon=True)
        self._interval = interval
        self._stop_event = stop_event
        self._n_samples = n_samples
        self._max_length = 100
        self._orbit_buffer = deque(maxlen = self._max_length)

    def average_orbit(self):
        orbit = _np.array(self._orbit_buffer)[-self._n_samples:]
        avg_orbit = _np.mean(orbit, axis=0)
        return avg_orbit

    def _main(self):
        while not self._stop_event.is_set():
            try:
                orbit = _bib_pv.get_orbit('xy')
                self._orbit_buffer.append(orbit)
                avg_orbit = self.average_orbit()
                orbit_x = avg_orbit[:_bib_status.nBPM]
                orbit_y = avg_orbit[_bib_status.nBPM:]
                self._driver.setParam('SI-GLOB:AP-SOFB.AvgMeasOrbX', orbit_x)
                self._driver.setParam('SI-GLOB:AP-SOFB.AvgMeasOrbY', orbit_y)
            except:
                self._driver.setParam('SI-GLOB:AP-SOFB.Err', 3)
            self._driver.updatePVs()
        else:
            log('exit', 'orbit measurement thread')


class MEASRespmThread(threading.Thread):

    def __init__(self, name, stop_event, interval):
        """Orbit Measurement Thread Object

        Keyword arguments:
        name -- threading object's name
        interval -- processing interval [s]
        stop_event -- event to stop processing

        Class main attribute: mode
        Defines what type of respm should be measured.
        0-Off, 1-H, 2-V, 3-HV, 4-H_F, 5-V_F, 6-HV_F
        """

        self._name = name
        super().__init__(name=self._name, target=self._main, daemon = True)
        self._interval = interval
        self._stop_event = stop_event
        self._mode = 0
        self._interrupt_measrespm_event = threading.Event()

    def _finalise_meas_respm(self, respm):
        if respm.shape != (0,):
            _respm = _np.zeros((_bib_status.nBPM*2, _bib_status.nCH+_bib_status.nCV+1))
            if self._mode == 1:
                _respm[:_bib_status.nBPM,:_bib_status.nCH] = respm
            elif self._mode == 2:
                _respm[_bib_status.nBPM:,_bib_status.nCH:-1] = respm
            elif self._mode == 3 or self._mode == 4:
                _respm[:,:-1] = respm
            elif self._mode == 5:
                _respm[:_bib_status.nBPM,:_bib_status.nCH] = respm[:,:-1]
                _respm[:_bib_status.nBPM,-1] = respm[:,-1]
            elif self._mode == 6:
                _respm[_bib_status.nBPM:,_bib_status.nCH:-1] = respm[:,:-1]
                _respm[_bib_status.nBPM:,-1] = respm[:,-1]
            elif self._mode == 7 or self._mode == 8:
                _respm = respm
            self._driver.write('SI-GLOB:AP-SOFB.RespMat', _respm)
        self._interrupt_measrespm_event.clear()
        self._mode = 0
        self._driver.setParam('SI-GLOB:AP-SOFB.OpMode', 0)

    def _main(self):
        while not self._stop_event.is_set():
            if self._mode == 1:
                respm = _bib_pv.meas_respm('h', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 2:
                respm = _bib_pv.meas_respm('v', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 3:
                respm = _bib_pv.meas_respm('h_v', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 4:
                respm = _bib_pv.meas_respm('hv', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 5:
                respm = _bib_pv.meas_respm('h_f', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 6:
                respm = _bib_pv.meas_respm('v_f', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 7:
                respm = _bib_pv.meas_respm('h_v_f', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            elif self._mode == 8:
                respm = _bib_pv.meas_respm('hv_f', self._interrupt_measrespm_event)
                self._finalise_meas_respm(respm)
            else:
                sleep(self._interval)
        else:
            log('exit', 'response matrix measurement thread')


class UPDATEVariablesThread(threading.Thread):

    def __init__(self, name, stop_event, interval):
        """Variable Update Thread Object

        Keyword arguments:
        name -- threading object's name
        interval -- processing interval [s]
        stop_event -- event to stop processing

        Class main attribute: mode
        Defines what variable should be updated.
        0-Off, 1-respm, 2-reforbit_x, 3-reforbit_y, 4-respm_sel, 5-reforbit_x_sel, 6-reforbit_y_sel, 7-bpm_sel, 8-ch_sel, 9-cv_sel, 10-add_bpm, 11-add_ch, 12-add_cv, 13-rmv_bpm, 14-rmv_ch 15-rmv_cv
        """

        self._name = name
        super().__init__(name=self._name, target=self._main, daemon = True)
        self._interval = interval
        self._stop_event = stop_event
        self._mode = 0

    def _main(self):
        while not self._stop_event.is_set():
            if self._mode != 0:
                if self._mode == 1:
                    try:
                        _bib_status.update_respm_slot(self._driver.getParam('SI-GLOB:AP-SOFB.RespMat'), reshape = True)
                        _bib_status.set_respm()
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 9)
                elif self._mode == 2:
                    try:
                        _bib_status.update_reforbit_slot(self._driver.getParam('SI-GLOB:AP-SOFB.RefOrbX'), 'x')
                        _bib_status.set_reforbit('x')
                        _bib_correction.set_reforbit()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 10)
                elif self._mode == 3:
                    try:
                        _bib_status.update_reforbit_slot(self._driver.getParam('SI-GLOB:AP-SOFB.RefOrbY'), 'y')
                        _bib_status.set_reforbit('y')
                        _bib_correction.set_reforbit()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 10)
                elif self._mode == 4:
                    try:
                        _bib_status.set_respm_slot(self._driver.getParam('SI-GLOB:AP-SOFB.RespMatSlot'))
                        _bib_status.set_respm()
                        _bib_correction.set_respm()
                        self._driver.setParam('SI-GLOB:AP-SOFB.RespMat', _bib_correction.get_respm())
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 9)
                elif self._mode == 5:
                    try:
                        _bib_status.set_reforbit_slot(self._driver.getParam('SI-GLOB:AP-SOFB.RefOrbXSlot'), 'x')
                        _bib_status.set_reforbit('x')
                        _bib_correction.set_reforbit()
                        self._driver.setParam('SI-GLOB:AP-SOFB.RefOrbX', _bib_correction.get_reforbit('x'))
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 10)
                elif self._mode == 6:
                    try:
                        _bib_status.set_reforbit_slot(self._driver.getParam('SI-GLOB:AP-SOFB.RefOrbYSlot'), 'y')
                        _bib_status.set_reforbit('y')
                        _bib_correction.set_reforbit()
                        self._driver.setParam('SI-GLOB:AP-SOFB.RefOrbY', _bib_correction.get_reforbit('y'))
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 10)
                elif self._mode == 7:
                    try:
                        _bib_status.set_device_sel('bpm', self._driver.getParam('SI-GLOB:AP-SOFB.EnblListBPM'))
                        _bib_status.set_device_idx('bpm')
                        _bib_correction.set_reforbit()
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 8:
                    try:
                        _bib_status.set_device_sel('ch', self._driver.getParam('SI-GLOB:AP-SOFB.EnblListCH'))
                        _bib_status.set_device_idx('ch')
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 9:
                    try:
                        _bib_status.set_device_sel('cv', self._driver.getParam('SI-GLOB:AP-SOFB.EnblListCV'))
                        _bib_status.set_device_idx('cv')
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 10:
                    try:
                        _bib_status.change_device_status('bpm', self._driver.getParam('SI-GLOB:AP-SOFB.AddBPM'), 1)
                        _bib_status.set_device_idx('bpm')
                        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListBPM', _bib_status.get_device_sel('bpm'))
                        _bib_correction.set_reforbit()
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 11:
                    try:
                        _bib_status.change_device_status('ch', self._driver.getParam('SI-GLOB:AP-SOFB.AddCH'), 1)
                        _bib_status.set_device_idx('ch')
                        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListCH', _bib_status.get_device_sel('ch'))
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 12:
                    try:
                        _bib_status.change_device_status('cv', self._driver.getParam('SI-GLOB:AP-SOFB.AddCV'), 1)
                        _bib_status.set_device_idx('cv')
                        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListCV', _bib_status.get_device_sel('cv'))
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 13:
                    try:
                        _bib_status.change_device_status('bpm', self._driver.getParam('SI-GLOB:AP-SOFB.RmvBPM'), 0)
                        _bib_status.set_device_idx('bpm')
                        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListBPM', _bib_status.get_device_sel('bpm'))
                        _bib_correction.set_reforbit()
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 14:
                    try:
                        _bib_status.change_device_status('ch', self._driver.getParam('SI-GLOB:AP-SOFB.RmvCH'), 0)
                        _bib_status.set_device_idx('ch')
                        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListCH', _bib_status.get_device_sel('ch'))
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                elif self._mode == 15:
                    try:
                        _bib_status.change_device_status('cv', self._driver.getParam('SI-GLOB:AP-SOFB.RmvCV'), 0)
                        _bib_status.set_device_idx('cv')
                        self._driver.setParam('SI-GLOB:AP-SOFB.EnblListCV', _bib_status.get_device_sel('cv'))
                        _bib_correction.set_respm()
                        _bib_correction.set_inv_respm()
                    except:
                        self._driver.setParam('SI-GLOB:AP-SOFB.Err', 11)
                self._mode = 0
                corr_onhold = str(self._driver._threads_dic['orbit_correction']._mode).split('_')
                meas_onhold = str(self._driver._threads_dic['respm_measurement']._mode).split('_')
                if corr_onhold[0] == 'W':
                    self._driver.write('SI-GLOB:AP-SOFB.OpMode', int(corr_onhold[1]))
                elif meas_onhold[0] == 'W':
                    self._driver.write('SI-GLOB:AP-SOFB.OpMode', int(meas_onhold[1]))
            else:
                sleep(self._interval)
        else:
            log('exit', 'update variables thread')
