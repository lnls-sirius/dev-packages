
import time as _time

from ..namesys import SiriusPVName
from .device import Device as _Device


class AFCPhysicalTrigger(_Device):
    """AFC Physical Trigger device."""

    PROPERTIES_DEFAULT = (
        'Dir-Sel', 'Dir-Sts',
        'DirPol-Sel', 'DirPol-Sts',
        'RcvCnt-Mon',
        'RcvLen-SP', 'RcvLen-RB',
        'TrnCnt-Mon',
        'TrnLen-SP', 'TrnLen-RB',
    )

    def __init__(self, devname, index, props2init='all'):
        """Init."""
        if not 0 <= int(index) <= 7:
            raise NotImplementedError(index)

        # handle FOFB and BPM IOC differences
        # TODO: remove when new BPM IOC is updated.
        if props2init == 'all':
            props2init = list(AFCPhysicalTrigger.PROPERTIES_DEFAULT)
            if SiriusPVName(devname).dev == 'BPM':
                props2init += ['RcvCntRst-SP', 'TrnCntRst-SP']
            else:
                props2init += ['RcvCntRst-Cmd', 'TrnCntRst-Cmd']

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
        # handle FOFB and BPM IOC differences
        # TODO: remove when new BPM IOC is updated.
        suf = 'SP' if 'BPM' in self.devname else 'Cmd'
        self[f'RcvCntRst-{suf}'] = 1
        _time.sleep(1)
        self[f'RcvCntRst-{suf}'] = 0

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
        # handle FOFB and BPM IOC differences
        # TODO: remove when new BPM IOC is updated.
        suf = 'SP' if 'BPM' in self.devname else 'Cmd'
        self[f'TrnCntRst-{suf}'] = 1
        _time.sleep(1)
        self[f'TrnCntRst-{suf}'] = 0

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

    def __init__(self, devname, index, acqcore='', props2init='all'):
        """Init."""
        if not 0 <= int(index) <= 23:
            raise NotImplementedError(index)
        propty_prefix = ':TRIGGER'+('_'+acqcore if acqcore else '')+str(index)
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
