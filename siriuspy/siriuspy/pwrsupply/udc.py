"""UDC class."""

from .bsmp import PSBSMPFactory as _PSBSMPFactory
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
        self._bsmp = self._create_bsmp_connectors()

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
    def parameters(self):
        """PRU Controller parameters."""
        return UDC._prucparms[self._psmodel]

    @property
    def ConstBSMP(self):
        """Return BSMP constants."""
        return self.parameters.ConstBSMP

    def reset(self, timeout):
        """Reset UDC."""
        # turn off all power supplies (NOTE: or F_RESET_UDC does not work)
        for bsmp in self._bsmp.values():
            bsmp.execute_function(
                func_id=self.ConstBSMP.F_TURN_OFF, timeout=timeout)
        # reset UDC
        bsmp = self._bsmp[next(iter(self._bsmp))]  # uses first BSMP device
        bsmp.execute_function(
            func_id=self.ConstBSMP.F_RESET_UDC, timeout=timeout,
            read_flag=False)

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
        return self._bsmp[index]
