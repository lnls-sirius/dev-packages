"""Module to deal with orbit acquisition."""

import time as _time
import os as _os
import numpy as _np
import epics as _epics
import siriuspy.util as _util
import siriuspy.csdevice.orbitcorr as _csorb
from siriuspy.thread import RepeaterThread as _Repeat
from siriuspy.envars import vaca_prefix as LL_PREF
from .base_class import BaseClass as _BaseClass

TIMEOUT = 0.05


class BaseOrbit(_BaseClass):
    pass


class EpicsOrbit(BaseOrbit):
    """Class to deal with orbit acquisition."""
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    REF_ORBIT_FILENAME = _os.path.join(path_, 'data', 'reference_orbit.siorb')
    del path_

    def get_database(self):
        """Get the database of the class."""
        db = _csorb.get_orbit_database(self.acc)
        prop = 'fun_set_pv'
        db['OrbitRefX-SP'][prop] = lambda x: self.set_ref_orbit('x', x)
        db['OrbitRefY-SP'][prop] = lambda x: self.set_ref_orbit('y', x)
        db['OrbitOfflineX-SP'][prop] = lambda x: self.set_offline_orbit('x', x)
        db['OrbitOfflineY-SP'][prop] = lambda x: self.set_offline_orbit('y', x)
        db['OrbitPointsNum-SP'][prop] = self.set_smooth_npts
        db['CorrMode-Sel'][prop] = self.set_correction_mode
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self.ref_orbits = {
                'x': _np.zeros(self._const.NR_BPMS),
                'y': _np.zeros(self._const.NR_BPMS)}
        self._load_ref_orbits()
        self.raw_orbs = {'x': [], 'y': []}
        self.smooth_orb = {'x': None, 'y': None}
        self.offline_orbit = {
                'x': _np.zeros(self._const.NR_BPMS),
                'y': _np.zeros(self._const.NR_BPMS)}
        self._smooth_npts = 1
        self.correction_mode = _csorb.CorrMode.Online
        dic = {'connection_timeout': TIMEOUT}
        self.pvs_pos = {
            name: {
                'x': _epics.PV(LL_PREF+name+':PosX-Mon', **dic),
                'y': _epics.PV(LL_PREF+name+':PosY-Mon', **dic)}
            for name in self._const.BPM_NAMES}
        self._orbit_thread = _Repeat(0.1, self._update_orbits, niter=0)
        self._orbit_thread.start()

    def get_orbit(self, reset=False):
        """Return the orbit distortion."""
        if self.correction_mode == _csorb.CorrMode.Offline:
            orbx = self.offline_orbit['x']
            orby = self.offline_orbit['y']
        else:
            if reset:
                self._reset_orbs()
            for i in range(3 * self._smooth_npts):
                if self.smooth_orb['x'] and self.smooth_orb['y']:
                    orbx = self.smooth_orb['x']
                    orby = self.smooth_orb['y']
                    break
                _time.sleep(0.1)  # assuming 10Hz of update rate of orbit
            else:
                self._update_log('ERR: get orbit function timeout.')
                orbx = self.ref_orbit['x']
                orby = self.ref_orbit['y']
        refx = self.ref_orbit['x']
        refy = self.ref_orbit['y']
        return _np.hstack([orbx-refx, orby-refy])

    def set_correction_mode(self, value):
        self.correction_mode = value
        self._update_log(
            'Changing to {0:s} mode.'.format(_csorb.CorrMode._fields[value])
            )
        self.run_callbacks('CorrMode-Sts', value)
        return True

    def set_offline_orbit(self, plane, value):
        self._update_log('Setting New Offline Orbit.')
        if len(value) != self._const.NR_BPMS:
            self._update_log('ERR: Wrong Size.')
            return False
        self.offline_orbit[plane] = _np.array(value)
        self.run_callbacks(
                    'OrbitOffline'+plane.upper()+'-RB', _np.array(value))
        return True

    def set_smooth_npts(self, num):
        self._update_log('Setting new number of points for median.')
        self._smooth_npts = num
        self.run_callbacks('OrbitPointsNum-RB', num)
        return True

    def set_ref_orbit(self, plane, orb):
        self._update_log('Setting New Reference Orbit.')
        if len(orb) != self._const.NR_BPMS:
            self._update_log('ERR: Wrong Size.')
            return False
        self.ref_orbits[plane] = _np.array(orb, dtype=float)
        self._save_ref_orbits()
        self._reset_orbs()
        self.run_callbacks('OrbitRef'+plane.upper()+'-RB', orb)
        return True

    def _update_log(self, value):
        self.run_callbacks(self.prefix + 'Log-Mon', value)

    def _load_ref_orbits(self):
        if _os.path.isfile(self.REF_ORBIT_FILENAME):
            self.ref_orbits['x'], self.ref_orbits['y'] = _np.loadtxt(
                                        self.REF_ORBIT_FILENAME, unpack=True)

    def _save_ref_orbits(self):
        orbs = _np.array([self.ref_orbits['x'], self.ref_orbits['y']]).T
        _np.savetxt(self.REF_ORBIT_FILENAME, orbs)

    def _reset_orbs(self):
        self.smooth_orb = {'x': None, 'y': None}

    def _update_orbits(self):
        orb = _np.zeros(self._const.NR_BPMS, dtype=float)
        orbs = {'x': orb, 'y': orb.copy()}
        for i, name in enumerate(self._const.BPM_NAMES):
            pvx = self.pvs_pos[name]['x']
            pvy = self.pvs_pos[name]['y']
            orbs['x'][i] = pvx.value if pvx.connected else 0.0
            orbs['y'][i] = pvy.value if pvy.connected else 0.0

        for plane in ('x', 'y'):
            self.run_callbacks('OrbitRaw'+plane.upper()+'-Mon', list(orb))
            self.raw_orbs[plane].append(orbs[plane])
            self.raw_orbs[plane] = self.raw_orbs[plane][-self._smooth_npts:]
            orb = _np.mean(self.raw_orbs[plane], axis=0)
            self.smooth_orb[plane] = orb
            self.run_callbacks('OrbitSmooth'+plane.upper()+'-Mon', list(orb))

    def _update_status(self):
        status = 0b11
        for i, plane in enumerate(('x', 'y')):
            nok = not all(v[plane].connected for v in self.pvs_pos.values())
            status = _util.update_bit(v=status, bit_pos=i, bit_val=nok)
        self._status = status
        self.run_callbacks('OrbitStatus-Mon', status)
