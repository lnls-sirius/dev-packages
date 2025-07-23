"""Beam stability info App."""

import os as _os
import logging as _log
import time as _time
from functools import partial as _part
import epics as _epics

import numpy as _np

from ..epics import PV as _PV
from ..callbacks import Callback as _Callback
from ..envars import VACA_PREFIX as _vaca_prefix
from ..namesys import SiriusPVName as _PVName
from ..devices import Device as _Device

from .csdev import StabInfoConst as _Const


class App(_Callback):
    """Main application for handling machine shift."""

    SCAN_FREQUENCY = 2  # [Hz]

    def __init__(self):
        """Class constructor."""
        super().__init__()
        self._const = _Const()
        self._pvs_database = self._const.get_propty_database()

        self._bbbh_oscamp = 0
        self._bbbv_oscamp = 0
        self._bbbl_oscamp = 0
        self._bbbh_oscamp_thres = self._const.BBBH_OSCAMP_THRES
        self._bbbv_oscamp_thres = self._const.BBBV_OSCAMP_THRES
        self._bbbl_oscamp_thres = self._const.BBBL_OSCAMP_THRES
        self._bbbh_status = self._const.StabUnstab.Stable
        self._bbbv_status = self._const.StabUnstab.Stable
        self._bbbl_status = self._const.StabUnstab.Stable
        self._bbbh_calibfactor = self._const.DEF_BBBH_CALIBFACTOR
        self._bbbv_calibfactor = self._const.DEF_BBBV_CALIBFACTOR
        self._bbbl_calibfactor = self._const.DEF_BBBL_CALIBFACTOR
        self.read_autosave_file()

        # connections
        # use pyepics recommendations for threading
        _epics.ca.use_initial_context()

        self._dev_bbb = dict()
        bbbprops = ['SRAM_PEAK1', ]
        for plane in ['H', 'V', 'L']:
            devname = 'SI-Glob:DI-BbBProc-'+plane
            self._dev_bbb[plane] = _Device(devname, props2init=bbbprops)

        sicurrent_pvname = _PVName(
            'SI-Glob:AP-CurrInfo:Current-Mon').substitute(
                prefix=_vaca_prefix)
        self.si_current_pv = _PV(sicurrent_pvname, connection_timeout=0.05)

        # pvs to write methods
        self.map_pv2write = {
            'BbBHCalibFactor-SP': _part(self.set_bbbcalibfactor, 'h'),
            'BbBVCalibFactor-SP': _part(self.set_bbbcalibfactor, 'v'),
            'BbBLCalibFactor-SP': _part(self.set_bbbcalibfactor, 'l'),
        }

        self.quit = False
        self.scanning = False
        self._thread_update = _epics.ca.CAThread(
            target=self._update_pvs, daemon=True)
        self._thread_update.start()

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('BbBHCalibFactor-SP', self._bbbh_calibfactor)
        self.run_callbacks('BbBHCalibFactor-RB', self._bbbh_calibfactor)
        self.run_callbacks('BbBHOscAmp-Mon', self._bbbh_oscamp)
        self.run_callbacks('BbBHOscAmpThres-Cte', self._bbbh_oscamp_thres)
        self.run_callbacks('BbBHStatus-Mon', self._bbbh_status)
        self.run_callbacks('BbBVCalibFactor-SP', self._bbbv_calibfactor)
        self.run_callbacks('BbBVCalibFactor-RB', self._bbbv_calibfactor)
        self.run_callbacks('BbBVOscAmp-Mon', self._bbbv_oscamp)
        self.run_callbacks('BbBVOscAmpThres-Cte', self._bbbv_oscamp_thres)
        self.run_callbacks('BbBVStatus-Mon', self._bbbv_status)
        self.run_callbacks('BbBLCalibFactor-SP', self._bbbl_calibfactor)
        self.run_callbacks('BbBLCalibFactor-RB', self._bbbl_calibfactor)
        self.run_callbacks('BbBLOscAmp-Mon', self._bbbl_oscamp)
        self.run_callbacks('BbBLOscAmpThres-Cte', self._bbbl_oscamp_thres)
        self.run_callbacks('BbBLStatus-Mon', self._bbbl_status)
        self._update_log('Started.')

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        _log.info('Write received for: %s --> %s', reason, str(value))
        if reason in self.map_pv2write.keys():
            status = self.map_pv2write[reason](value)
            _log.info('%s Write for: %s --> %s',
                      str(status).upper(), reason, str(value))
            return status
        _log.warning('PV %s does not have a set function.', reason)
        return False

    def set_bbbcalibfactor(self, plane, value):
        """Set BbB calibration factor."""
        setattr(self, '_bbb'+plane+'_calibfactor', value)
        self.run_callbacks('BbB'+plane.upper()+'CalibFactor-RB', value)
        self.update_autosave_file()
        return True

    #  ----- log auxiliary methods -----

    def _update_log(self, msg):
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)

    # ----- auto save methods -----

    @property
    def auto_save_data(self):
        """Data to be saved in autosave file."""
        data = [
            self._bbbh_calibfactor,
            self._bbbv_calibfactor,
            self._bbbl_calibfactor,
            ]
        return _np.array(data)

    def read_autosave_file(self):
        """Read autosave file."""
        filename = self._const.autosave_fname
        data = None
        if _os.path.isfile(filename):
            data = _np.loadtxt(filename)
        if data is not None:
            bbbh, bbbv, bbbl = data
            self._bbbh_calibfactor = bbbh
            self._bbbv_calibfactor = bbbv
            self._bbbl_calibfactor = bbbl
        else:
            _log.info(
                'No backup file was found, default values '
                'were used for calibration factors.')
            self.update_autosave_file()
            _log.info('First autosave file was created.')

    def update_autosave_file(self):
        """Update autosave file."""
        path = _os.path.split(self._const.autosave_fname)[0]
        _os.makedirs(path, exist_ok=True)
        _np.savetxt(
            self._const.autosave_fname, self.auto_save_data)

    # ----- update pvs methods -----

    def _update_pvs(self):
        tplanned = 1.0/App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            pvcurr = self.si_current_pv
            if pvcurr.connected and pvcurr.value is not None:
                curr = pvcurr.value
                for pln in ['H', 'V', 'L']:
                    dev = self._dev_bbb[pln]
                    harmn = self._const.SI_HARMNUM
                    calib = getattr(self, '_bbb'+pln.lower()+'_calibfactor')
                    thres = getattr(self, '_bbb'+pln.lower()+'_oscamp_thres')
                    cthres = self._const.CURR_THRES
                    oscamp_db = dev['SRAM_PEAK1']
                    if oscamp_db is not None:
                        oscamp_phy = 10**(oscamp_db/20) * harmn / curr / calib
                        self.run_callbacks('BbB'+pln+'OscAmp-Mon', oscamp_phy)
                        status = curr > cthres and oscamp_phy > thres
                        self.run_callbacks('BbB'+pln+'Status-Mon', int(status))

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'Update loop took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))
