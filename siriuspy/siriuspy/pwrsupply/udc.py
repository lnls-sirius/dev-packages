"""UDC class."""

import time as _time
from .psbsmp import PSBSMPFactory as _PSBSMPFactory
from .psmodel import PSModelFactory as _PSModelFactory
from . import prucparms as _prucparms


class UDC:
    """UDC."""

    _prucparms = {
        'FBP': _prucparms.PRUCParmsFBP,
        'FBP_DCLink': _prucparms.PRUCParmsFBP_DCLink,
        'FAC_2S_DCDC': _prucparms.PRUCParmsFAC_2S_DCDC,
        'FAC_2P4S_DCDC': _prucparms.PRUCParmsFAC_2P4S_DCDC,
        'FAC_DCDC': _prucparms.PRUCParmsFAC_DCDC,
        'FAC_2S_ACDC': _prucparms.PRUCParmsFAC_2S_ACDC,
        'FAC_2P4S_ACDC': _prucparms.PRUCParmsFAC_2P4S_ACDC,
        'FAP': _prucparms.PRUCParmsFAP,
        'FAP_4P': _prucparms.PRUCParmsFAP_4P,
        'FAP_2P2S': _prucparms.PRUCParmsFAP_2P2S,
    }

    def __init__(self, pru, psmodel, device_ids):
        """Init."""
        self._pru = pru
        self._device_ids = device_ids
        self._psmodel = psmodel
        self._bsmp_devs = self._create_bsmp_connectors()
        self._first_dev = self._bsmp_devs[min(self._device_ids)]

    @property
    def pru(self):
        """Return PRU used for communication with UDC."""
        return self._pru

    @property
    def psmodel(self):
        """Return power supply model associated with UDC."""
        return self._psmodel

    @property
    def device_ids(self):
        """."""
        return self._device_ids

    @property
    def prucparms(self):
        """Return PRU Controller parameters object."""
        prucparms_class = UDC._prucparms[self._psmodel]
        return prucparms_class()

    @property
    def CONST_BSMP(self):
        """Return PSBSMP constants."""
        return self._first_dev.CONST_BSMP

    @property
    def CONST_PSBSMP(self):
        """Return PSBSMP constants."""
        return self.prucparms.CONST_PSBSMP

    def reset(self, **kwargs):
        """Reset UDC."""
        # turn off all power supplies (NOTE: or F_RESET_UDC does not work)
        for bsmp in self._bsmp_devs.values():
            ack, data = bsmp.execute_function(
                func_id=self.CONST_PSBSMP.F_TURN_OFF, timeout=timeout)
            if ack != self.CONST_BSMP.ACK_OK:
                dev_id = bsmp.channel.address
                print(('UDC.reset: could not turn off '
                       'device id:{} !').format(dev_id))
                return ack, data

        # reset UDC proper.
        self._first_dev.execute_function(
            func_id=self.CONST_PSBSMP.F_RESET_UDC, **kwargs, read_flag=False)

        return ack, data

    def bufsample_disable(self):
        """Disable DSP from writting to bufsample curve."""
        for bsmp in self._bsmp_devs.values():
            ack, data = bsmp.wfmref_mon_bufsample_disable()
            if ack != self.CONST_BSMP.ACK_OK:
                return ack, data
        # a single sleep for all devices
        sleep_time = self._first_dev._sleep_disable_bufsample = 0.5  # [s]
        _time.sleep(sleep_time)
        return ack, data

    def bufsample_enable(self):
        """Enable DSP from writting to bufsample curve."""
        for bsmp in self._bsmp_devs.values():
            ack, data = bsmp.wfmref_mon_bufsample_enable()
            if ack != self.CONST_BSMP.ACK_OK:
                return ack, data
        return ack, data

    def parse_firmware_version(self, version):
        """Process firmware version from BSMP device."""
        # uses first BSMP device
        bsmp_dev = self._bsmp_devs[next(iter(self._bsmp_devs))]  # first bsmp
        return bsmp_dev.parse_firmware_version(version)

    def reset_groups_of_variables(self, groups):
        """Reset groups of variables."""
        for bsmp_dev in self._bsmp_devs.values():
            bsmp_dev.reset_groups_of_variables(groups=groups)

    def _create_bsmp_connectors(self):
        bsmp = dict()
        model = _PSModelFactory.create(self._psmodel)
        bsmpsim_class = model.simulation_class
        for dev_id in self._device_ids:
            if self._pru.simulated:
                bsmp[dev_id] = bsmpsim_class(self._pru)
            else:
                bsmp[dev_id] = _PSBSMPFactory.create(
                    self._psmodel, dev_id, self._pru)
        return bsmp

    def __getitem__(self, index):
        """Return BSMP."""
        return self._bsmp_devs[index]
