
import queue
from pcaspy import Driver
import epics


class PCASDriver(Driver):

    def  __init__(self, threads_dic, start_event, stop_event, interval):
        super().__init__()
        self._threads_dic = threads_dic
        self._interval = interval
        self._start_event = start_event
        self._queue = queue.Queue()
        self._stop_event = stop_event
        for tn in threads_dic:
            self._threads_dic[tn]._driver = self

    def read(self, reason):
        return super().read(reason)

    def write(self, reason, value):
        if reason == 'SI-GLOB:AP-SOFB.OpMode':
            if value == 0:
                self._threads_dic['orbit_correction']._mode = 0
                if self._threads_dic['respm_measurement']._mode != 0: self._threads_dic['respm_measurement']._interrupt_measrespm_event.set()
                else: self._threads_dic['respm_measurement']._mode = 0
            elif value == 1:
                if self._threads_dic['respm_measurement']._mode != 0:
                    self.setParam('SI-GLOB:AP-SOFB.Err', 6)
                    return
                else:
                    corr_mode = (self.getParam('SI-GLOB:AP-SOFB.RFreqEnbl')*4) + self.getParam('SI-GLOB:AP-SOFB.RespMatType') + 1
                    if self._threads_dic['var_update']._mode != 0:
                        self._threads_dic['orbit_correction']._mode = 'W_'+str(corr_mode)
                    else:
                        self._threads_dic['orbit_correction']._mode = corr_mode
                    self._threads_dic['orbit_correction']._autocorr = True
            elif value == 2:
                if self._threads_dic['orbit_correction']._mode != 0:
                    self.setParam('SI-GLOB:AP-SOFB.Err', 1)
                    return
                else:
                    meas_mode = (self.getParam('SI-GLOB:AP-SOFB.RFreqEnbl')*4) + self.getParam('SI-GLOB:AP-SOFB.RespMatType') + 1
                    if self._threads_dic['var_update']._mode != 0:
                        self._threads_dic['respm_measurement']._mode = 'W_'+str(meas_mode)
                    else:
                        self._threads_dic['respm_measurement']._mode = meas_mode
        elif reason == 'SI-GLOB:AP-SOFB.RespMatType' or reason == 'SI-GLOB:AP-SOFB.RFreqEnbl':
            if self.getParam('SI-GLOB:AP-SOFB.OpMode') != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 14)
                return
        elif reason == 'SI-GLOB:AP-SOFB.NrSpl':
            if not 1 <= value <= self._threads_dic['orbit_measurement']._max_length:
                self.setParam('SI-GLOB:AP-SOFB.Err', 2)
                return
            else:
                self._threads_dic['orbit_measurement']._n_samples = value
        elif reason == 'SI-GLOB:AP-SOFB.RespMatSlot':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 7)
                return
            else:
                self._threads_dic['var_update']._mode = 4
        elif reason == 'SI-GLOB:AP-SOFB.RefOrbXSlot':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 8)
                return
            else:
                self._threads_dic['var_update']._mode = 5
        elif reason == 'SI-GLOB:AP-SOFB.RefOrbYSlot':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 8)
                return
            else:
                self._threads_dic['var_update']._mode = 6
        elif reason == 'SI-GLOB:AP-SOFB.RESPM':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 4)
                return
            else:
                self._threads_dic['var_update']._mode = 1
        elif reason == 'SI-GLOB:AP-SOFB.RefOrbX':
            if self.getParam('SI-GLOB:AP-SOFB.RefOrbXSlot') == 0 or self.getParam('SI-GLOB:AP-SOFB.RefOrbXSlot') == 1:
                self.setParam('SI-GLOB:AP-SOFB.Err', 16)
                return
            else:
                if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                    self.setParam('SI-GLOB:AP-SOFB.Err', 5)
                    return
                else:
                    self._threads_dic['var_update']._mode = 2
        elif reason == 'SI-GLOB:AP-SOFB.RefOrbY':
            if self.getParam('SI-GLOB:AP-SOFB.RefOrbYSlot') == 0 or self.getParam('SI-GLOB:AP-SOFB.RefOrbYSlot') == 1:
                self.setParam('SI-GLOB:AP-SOFB.Err', 16)
                return
            else:
                if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                    self.setParam('SI-GLOB:AP-SOFB.Err', 5)
                    return
                else:
                    self._threads_dic['var_update']._mode = 3
        elif reason == 'SI-GLOB:AP-SOFB.EnblListBPM':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 7
        elif reason == 'SI-GLOB:AP-SOFB.EnblListCH':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 8
        elif reason == 'SI-GLOB:AP-SOFB.EnblListCV':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 9
        elif reason == 'SI-GLOB:AP-SOFB.AddBPM':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 10
        elif reason == 'SI-GLOB:AP-SOFB.AddCH':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 11
        elif reason == 'SI-GLOB:AP-SOFB.AddCV':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 12
        elif reason == 'SI-GLOB:AP-SOFB.RmvBPM':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 13
        elif reason == 'SI-GLOB:AP-SOFB.RmvCH':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 14
        elif reason == 'SI-GLOB:AP-SOFB.RmvCV':
            if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['var_update']._mode != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 11)
                return
            else:
                self._threads_dic['var_update']._mode = 15
        elif reason == 'SI-GLOB:AP-SOFB.StrthCH' or reason == 'SI-GLOB:AP-SOFB.StrthCV':
            if not 0 <= value <= 100 or self.getParam('SI-GLOB:AP-SOFB.OpMode') != 0:
                self.setParam('SI-GLOB:AP-SOFB.Err', 13)
                return
        elif reason == 'SI-GLOB:AP-SOFB.ManCorrTrig':
            if value == 1:
                if self._threads_dic['orbit_correction']._mode != 0 or self._threads_dic['respm_measurement']._mode != 0:
                    self.setParam('SI-GLOB:AP-SOFB.Err', 15)
                    return
                else:
                    corr_mode = (self.getParam('SI-GLOB:AP-SOFB.RFreqEnbl')*4) + self.getParam('SI-GLOB:AP-SOFB.RespMatType') + 1
                    if self._threads_dic['var_update']._mode != 0:
                        self._threads_dic['orbit_correction']._mode = 'W_'+str(corr_mode)
                    else:
                        self._threads_dic['orbit_correction']._mode = corr_mode
                    self._threads_dic['orbit_correction']._autocorr = False
        self.setParam(reason, value)
        self.pvDB[reason].flag = False # avoid double camonitor update
        return True
