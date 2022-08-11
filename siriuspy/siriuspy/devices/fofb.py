"""FOFB devices."""

import time as _time

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..search import BPMSearch as _BPMSearch

from .device import Device as _Device, ProptyDevice as _ProptyDevice


class _FOFBCtrlBase:
    """FOFB Ctrl base."""

    _devices = {
        f'SI{i:02d}': f'IA-{i:02d}RaBPM:BS-FOFBCtrl' for i in range(1, 21)}
    DEVICES = _get_namedtuple('DEVICES', *zip(*_devices.items()))


class _DCCDevice(_ProptyDevice):

    DEF_TIMEOUT = 1

    _properties = (
        'BPMId-Cte', 'BPMCnt-Mon',
        'CCEnable-SP', 'CCEnable-RB',
        'TimeFrameLen-SP', 'TimeFrameLen-RB',
    )

    def __init__(self, devname, dccname):
        """Init."""
        super().__init__(
            devname, dccname, properties=_DCCDevice._properties)

    @property
    def bpm_id(self):
        """BPM Id constant."""
        return self['BPMId-Cte']

    @property
    def bpm_count(self):
        """BPM count."""
        return self['BPMCnt-Mon']

    @property
    def cc_enable(self):
        """Communication enable."""
        return self['CCEnable-RB']

    @cc_enable.setter
    def cc_enable(self, value):
        self['CCEnable-SP'] = value

    @property
    def time_frame_len(self):
        """Time frame length."""
        return self['TimeFrameLen-RB']

    @time_frame_len.setter
    def time_frame_len(self, value):
        self['TimeFrameLen-SP'] = value

    def cmd_sync(self, timeout=DEF_TIMEOUT):
        """Synchronize DCC."""
        self.cc_enable = 1
        if not self._wait('CCEnable-RB', 1, timeout/2):
            return False
        _time.sleep(1)
        self.cc_enable = 0
        return self._wait('CCEnable-RB', 0, timeout/2)


class FOFBCtrlDCC(_DCCDevice, _FOFBCtrlBase):
    """FOFBCtrl DCC device."""

    class PROPDEVICES:
        """DCC devices."""

        FMC = 'DCCFMC'
        P2P = 'DCCP2P'
        ALL = (FMC, P2P)

    def __init__(self, devname, dccname):
        """Init."""
        if devname not in self.DEVICES:
            raise NotImplementedError(devname)
        if dccname not in self.PROPDEVICES.ALL:
            raise NotImplementedError(dccname)
        super().__init__(devname, dccname)


class BPMDCC(_DCCDevice):
    """BPM DCC device."""

    def __init__(self, devname):
        """Init."""
        if not _BPMSearch.is_valid_devname(devname):
            raise NotImplementedError(devname)
        super().__init__(devname, 'DCC')
