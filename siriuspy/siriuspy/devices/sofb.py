"""."""

import time as _time

from ..csdevice.orbitcorr import SOFBFactory
from .device import Device as _Device


class SOFB(_Device):
    """SOFB Device."""

    class DEVICES:
        """Devices names."""

        TB = 'TB-Glob:AP-SOFB'
        BO = 'BO-Glob:AP-SOFB'
        TS = 'TS-Glob:AP-SOFB'
        SI = 'SI-Glob:AP-SOFB'
        ALL = (TB, BO, TS, SI)

    _propty_tmpl = (
        'SlowOrbX-Mon', 'SlowOrbY-Mon',
        'KickCH-Mon', 'KickCV-Mon',
        'DeltaKickCH-Mon', 'DeltaKickCV-Mon',
        'DeltaKickCH-SP', 'DeltaKickCV-SP',
        'DeltaFactorCH-SP', 'DeltaFactorCV-SP',
        'DeltaFactorCH-RB', 'DeltaFactorCV-RB',
        'RefOrbX-SP', 'RefOrbY-SP',
        'RefOrbX-RB', 'RefOrbY-RB',
        'BPMXEnblList-SP', 'BPMYEnblList-SP',
        'BPMXEnblList-RB', 'BPMYEnblList-RB',
        'CHEnblList-SP', 'CVEnblList-SP',
        'CHEnblList-RB', 'CVEnblList-RB',
        'RFEnbl-Sel', 'RFEnbl-Sts'
        'CalcDelta-Cmd', 'ApplyDelta-Cmd', 'SmoothReset-Cmd',
        'SmoothNrPts-SP', 'SmoothNrPts-RB',
        'BufferCount-Mon',
        'TrigNrSamplesPost-SP',
        'TrigNrSamplesPost-RB',
        'ClosedLoop-Sts', 'ClosedLoop-Sel'
        # ring-type dependent properties
        '<ORBTP>' + 'Sum-Mon',
        '<ORBTP>' + 'OrbX-Mon', '<ORBTP>' + 'OrbY-Mon',
        # properties used only for ring-type accelerators:
        '<ORBTP>' + 'Idx' + 'OrbX-Mon', '<ORBTP>' + 'Idx' + 'OrbY-Mon')

    _default_timeout = 10  # [s]
    _off, _on = 0, 1

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in SOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        # SOFB object
        self.data = SOFBFactory.create(devname[:2])

        # define device properties
        self._orbtp, properties = \
            self._set_attributes_properties()

        # call base class constructor
        super().__init__(devname, properties=properties)

        # shortcut attributes to property names
        self._trajx = self._orbtp + 'OrbX-Mon'
        self._trajy = self._orbtp + 'OrbY-Mon'
        self._sum = self._orbtp + 'Sum-Mon'
        self._trajx_idx = self._orbtp + 'Idx' + 'OrbX-Mon'
        self._trajy_idx = self._orbtp + 'Idx' + 'OrbY-Mon'

    @property
    def orbit_type(self):
        """."""
        return self._orbtp

    @property
    def trajx(self):
        """."""
        return self[self._trajx]

    @property
    def trajy(self):
        """."""
        return self[self._trajy]

    @property
    def sum(self):
        """."""
        return self[self._sum]

    @property
    def trajx_idx(self):
        """."""
        return self[self._trajx_idx] if self.data.isring \
            else self.trajx

    @property
    def trajy_idx(self):
        """."""
        return self[self._trajy_idx] if self.data.isring \
            else self.trajy

    @property
    def orbx(self):
        """."""
        return self['SlowOrbX-Mon']

    @property
    def orby(self):
        """."""
        return self['SlowOrbY-Mon']

    @property
    def kickch(self):
        """."""
        return self['KickCH-Mon']

    @property
    def kickcv(self):
        """."""
        return self['KickCV-Mon']

    @property
    def deltakickch(self):
        """."""
        return self['DeltaKickCH-Mon']

    @deltakickch.setter
    def deltakickch(self, value):
        """."""
        self['DeltaKickCH-Mon'] = value

    @property
    def deltakickcv(self):
        """."""
        return self['DeltaKickCV-Mon']

    @deltakickcv.setter
    def deltakickcv(self, value):
        """."""
        self['DeltaKickCV-Mon'] = value

    @property
    def deltafactorch(self):
        """."""
        return self['DeltaFactorCH-RB']

    @deltafactorch.setter
    def deltafactorch(self, value):
        """."""
        self['DeltaFactorCH-SP'] = value

    @property
    def deltafactorcv(self):
        """."""
        return self['DeltaFactorCV-RB']

    @deltafactorcv.setter
    def deltafactorcv(self, value):
        """."""
        self['DeltaFactorCV-SP'] = value

    @property
    def refx(self):
        """."""
        return self['RefOrbX-RB']

    @refx.setter
    def refx(self, value):
        """."""
        self['RefOrbX-SP'] = value

    @property
    def refy(self):
        """."""
        return self['RefOrbY-RB']

    @refy.setter
    def refy(self, value):
        """."""
        self['RefOrbY-SP'] = value

    @property
    def bpmxenbl(self):
        """."""
        return self['BPMXEnblList-RB']

    @bpmxenbl.setter
    def bpmxenbl(self, value):
        """."""
        self['BPMXEnblList-SP'] = value

    @property
    def bpmyenbl(self):
        """."""
        return self['BPMYEnblList-RB']

    @bpmyenbl.setter
    def bpmyenbl(self, value):
        """."""
        self['BPMYEnblList-SP'] = value

    @property
    def chenbl(self):
        """."""
        return self['CHEnblList-RB']

    @chenbl.setter
    def chenbl(self, value):
        """."""
        self['CHEnblList-SP'] = value

    @property
    def cvenbl(self):
        """."""
        return self['CVEnblList-RB']

    @cvenbl.setter
    def cvenbl(self, value):
        """."""
        self['CVEnblList-SP'] = value

    @property
    def rfenbl(self):
        """."""
        return self['RFEnbl-Sts']

    @rfenbl.setter
    def rfenbl(self, value):
        """."""
        self['RFEnbl-Sel'] = value

    @property
    def buffer_count(self):
        """."""
        return self['BufferCount-Mon']

    @property
    def nr_points(self):
        """."""
        return self['SmoothNrPts-RB']

    @nr_points.setter
    def nr_points(self, value):
        """."""
        self['SmoothNrPts-SP'] = int(value)

    @property
    def trigsample(self):
        """."""
        return self['TrigNrSamplesPost-RB']

    @trigsample.setter
    def trigsample(self, value):
        """."""
        self['TrigNrSamplesPost-SP'] = int(value)

    def cmd_reset(self):
        """."""
        self['SmoothReset-Cmd'] = SOFB._on

    def cmd_calccorr(self):
        """."""
        self['CalcDelta-Cmd'] = SOFB._on

    def cmd_applycorr(self):
        """."""
        self['ApplyDelta-Cmd'] = self.data.ApplyDelta.CH
        _time.sleep(0.3)
        self['ApplyDelta-Cmd'] = self.data.ApplyDelta.CV

    @property
    def autocorrsts(self):
        """."""
        return self['ClosedLoop-Sts']

    def cmd_turn_on_autocorr(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout
        self['ClosedLoop-Sel'] = SOFB._on
        self._wait(
            'ClosedLoop-Sts', SOFB._on, timeout=timeout)

    def cmd_turn_off_autocorr(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout
        self['ClosedLoop-Sel'] = SOFB._off
        self._wait(
            'ClosedLoop-Sts', SOFB._off, timeout=timeout)

    def wait_buffer(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout
        interval = 0.050  # [s]
        ntrials = int(timeout/interval)
        _time.sleep(10*interval)
        for _ in range(ntrials):
            if self.buffer_count >= self['SmoothNrPts-SP']:
                break
            _time.sleep(interval)
        else:
            print('WARN: Timed out waiting orbit.')

    # --- private methods ---

    def _set_attributes_properties(self):
        orbtp = 'MTurn' if self.data.isring else 'SPass'
        properties = []
        for propty in SOFB._propty_tmpl:
            propty = propty.replace('<ORBTP>', orbtp)
            if self.data.isring or \
                    ('IdxOrbX-Mon' not in propty and
                     'IdxOrbY-Mon' not in propty):
                properties.append(propty)
        return orbtp, properties
