
import time as _time

from ..namesys import SiriusPVName as _PVName
from .device import Device as _Device, DeviceSet as _DeviceSet
from mathphys.functions import get_namedtuple as _get_namedtuple

# ------- AMC devices -------


class AMCCtrlBase:
    """Advanced Mezzanine Cards (AMC) control base class."""

    keys = [f'IA{i:02d}' for i in range(1, 21)]
    _devices = {}
    for key in keys:
        temp = []
        for j in range(1, 13):
            # Slot 3 is not used
            if j != 3:
                temp.append(f'IA-{key}RaBPM:CO-AMC-{j:01d}')
        _devices[key] = temp
    temp = []
    for j in range(1, 13):
        if j != 3:
            temp.append(f'IA-20RaBPMTL:CO-AMC-{j:01d}')
    _devices['IA20TL'] = temp
    DEVICES = _get_namedtuple('DEVICES', *zip(*_devices.items()))


class AMCCtrlAcqBase(_Device, AMCCtrlBase):
    """AMC acquisition base device."""

    PROPERTIES_DEFAULT = (
        'Status-Cte',
        # 'FruId-Cte',
        # 'BoarManuf-Cte', 'BoardName-Cte',
        # 'BoardSN-Cte', 'BoardPN-Cte',
        # 'ProdManuf-Cte', 'ProdName-Cte',
        # 'ProdSN-Cte', 'ProdPN-Cte',
        # 'PowerCtl-Sel',
        'SoftRst-Cmd',
        'SoftRstSts-Mon',
        # 'PowerCtl-Sel',
    )

    def __init__(self, devname, **kws):
        """Init."""
        # call base class constructor
        _Device.__init__(self, devname, **kws)

    @property
    def status(self):
        """."""
        return self['Status-Cte']

    @property
    def soft_rst(self):
        """."""
        return self['SoftRst-Cmd']

    @property
    def soft_rst_sts(self):
        """."""
        return self['SoftRstSts-Mon']


class FamAMCAcq(_DeviceSet):

    AMCCTRL_CLASS = AMCCtrlAcqBase

    def __init__(self, ctrlname=None, bpmnames=None, event=None):
        # AMCCtrl devices
        ctrlnames = AMCCtrlBase.DEVICES if not ctrlname else [ctrlname, ]
        self._ctlrs, subs = dict(), list()
        for idx, ctl in enumerate(ctrlnames):
            for i, k in enumerate(ctl):
                self._ctlrs[ctl[i]] = self.AMCCTRL_CLASS(
                    ctl[i], auto_monitor_mon=False
                    )
                subs.append(f'{idx+1:02}')
        # sub = '(' + '|'.join(subs) + ').*'

    # call base class constructor
        devices = list()
        devices.extend(self._ctlrs.values())
        _DeviceSet.__init__(self, devices, devname='')


class AFCPhysicalTrigger(_Device):
    """AFC Physical Trigger device."""

    PROPERTIES_DEFAULT = (
        'Dir-Sel', 'Dir-Sts',
        'DirPol-Sel', 'DirPol-Sts',
        'RcvCnt-Mon',
        'RcvLen-SP', 'RcvLen-RB',
        'RcvCntRst-Cmd',
        'TrnCnt-Mon',
        'TrnLen-SP', 'TrnLen-RB',
        'TrnCntRst-Cmd',
    )

    def __init__(self, devname, index, props2init='all'):
        """Init."""
        if not 0 <= int(index) <= 7:
            raise NotImplementedError(index)

        if props2init == 'all':
            props2init = list(AFCPhysicalTrigger.PROPERTIES_DEFAULT)

        super().__init__(devname+':TRIGGER'+str(index), props2init=props2init)

    @property
    def direction(self):
        """Direction."""
        return self['Dir-Sts']

    @direction.setter
    def direction(self, value):
        self['Dir-Sel'] = value

    @property
    def polarity(self):
        """Polarity."""
        return self['DirPol-Sts']

    @polarity.setter
    def polarity(self, value):
        self['DirPol-Sel'] = value

    @property
    def receiver_counter(self):
        """Receiver counter."""
        return self['RcvCnt-Mon']

    def cmd_reset_receiver_counter(self):
        """Reset receiver counter."""
        self[f'RcvCntRst-Cmd'] = 1
        _time.sleep(1)
        self[f'RcvCntRst-Cmd'] = 0

    @property
    def receiver_length(self):
        """Receiver length."""
        return self['RcvLen-RB']

    @receiver_length.setter
    def receiver_length(self, value):
        self['RcvLen-SP'] = value

    @property
    def transmitter_counter(self):
        """Transmitter counter."""
        return self['TrnCnt-Mon']

    def cmd_reset_transmitter_counter(self):
        """Reset transmitter counter."""
        self[f'TrnCntRst-Cmd'] = 1
        _time.sleep(1)
        self[f'TrnCntRst-Cmd'] = 0

    @property
    def transmitter_length(self):
        """Transmitter length."""
        return self['TrnLen-RB']

    @transmitter_length.setter
    def transmitter_length(self, value):
        self['TrnLen-SP'] = value


class AFCACQLogicalTrigger(_Device):
    """AFC ACQ Logical Trigger device."""

    PROPERTIES_DEFAULT = (
        'RcvSrc-Sel', 'RcvSrc-Sts',
        'RcvInSel-SP', 'RcvInSel-RB',
        'TrnSrc-Sel', 'TrnSrc-Sts',
        'TrnOutSel-SP', 'TrnOutSel-RB',
    )

    def __init__(self, devname, index, acqcore='GEN', props2init='all'):
        """Init."""
        if not 0 <= int(index) <= 23:
            raise NotImplementedError(index)
        propty_prefix = f':TRIGGER_{acqcore}{str(index)}'
        super().__init__(devname + propty_prefix, props2init=props2init)

    @property
    def receiver_source(self):
        """Receiver source."""
        return self['RcvSrc-Sts']

    @receiver_source.setter
    def receiver_source(self, value):
        self['RcvSrc-Sel'] = value

    @property
    def receiver_in_sel(self):
        """Receiver in selection."""
        return self['RcvInSel-RB']

    @receiver_in_sel.setter
    def receiver_in_sel(self, value):
        self['RcvInSel-SP'] = value

    @property
    def transmitter_source(self):
        """Transmitter source."""
        return self['TrnSrc-Sts']

    @transmitter_source.setter
    def transmitter_source(self, value):
        self['TrnSrc-Sel'] = value

    @property
    def transmitter_out_sel(self):
        """Transmitter out selection."""
        return self['TrnOutSel-RB']

    @transmitter_out_sel.setter
    def transmitter_out_sel(self, value):
        self['TrnOutSel-SP'] = value
