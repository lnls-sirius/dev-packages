"""Beamline Control."""

from .device import DeviceNC as _DeviceNC


class BLPPSCtrl(_DeviceNC):
    """Beamline Control."""

    class DEVICES:
        """Devices names."""

        CAX = 'CAX'
        ALL = (CAX, )

    _properties = (
        'F:PPS01:FOEOPEN',  # Enviar 1 para abrir o Front-end completo (abre o gamma e o photon)
        'F:PPS01:FOECLOSE',  # Enviar 1 para fechar o Front-end completo (fecha o photon e o gamma)
        'F:PPS01:GS_X_STATUS',  # Status gamma shutter front-end – 0 indica aberto
        'F:PPS01:PS_STATUS',  # Status photon shutter front-end – 0 indica aberto
        'A:PPS01:OEAOPENCLOSE',  # shutter da cabana a - Enviar 1 –se estiver fechado abre – se estiver aberto fecha
        'A:PPS01:PG_STATUS',  # Status do gamma shutter da cabana A – 0 indica aberto
        'M:PPS01:HABILITACAO_MAQUINA',  # Status da liberação do gamma pela máquina – 1 indica liberado
        'A:PPS01:SEARCH_OK',  # status da procura cabana A – 1 indica procura feita
        'B:PPS01:SEARCH_OK',  # status da procura cabana B – 1 indica procura feita
    )

    def __init__(self, devname, *args, **kwargs):
        """Init."""
        # check if device exists
        if devname not in BLPPSCtrl.DEVICES.ALL:
            raise NotImplementedError(devname)
        # call base class constructor
        super().__init__(devname, properties=self._properties, *args, **kwargs)

    @property
    def is_hutchA_intlk_search_done(self):
        """."""
        return self['A:PPS01:SEARCH_OK'] == 1

    @property
    def is_hutchB_intlk_search_done(self):
        """."""
        return self['B:PPS01:SEARCH_OK'] == 1

    @property
    def is_machine_gamma_enabled(self):
        """."""
        return self['M:PPS01:HABILITACAO_MAQUINA'] == 1

    @property
    def is_frontend_gamma_shutter_opened(self):
        """."""
        return self['F:PPS01:GS_X_STATUS'] == 0

    @property
    def is_frontend_photon_shutter_opened(self):
        """."""
        return self['F:PPS01:PS_STATUS'] == 0
    
    @property
    def is_hutchA_gamma_shutter_opened(self):
        """."""
        return self['A:PPS01:PG_STATUS'] == 0
    
    def cmd_frontend_gamma_and_photon_open(self):
        """"."""
        self['F:PPS01:FOEOPEN'] = 1

    def cmd_frontend_gamma_and_photon_close(self):
        """"."""
        self['F:PPS01:FOECLOSE'] = 1

    def cmd_hutchA_gamma_open(self):
        """"."""
        if not self.is_hutchA_gamma_shutter_opened:
            self['A:PPS01:OEAOPENCLOSE'] = 1

    def cmd_hutchA_gamma_close(self):
        """"."""
        if self.is_hutchA_gamma_shutter_opened:
            self['A:PPS01:OEAOPENCLOSE'] = 1

    def cmd_frontend_gamma_and_photon_close(self):
        """"."""
        self['F:PPS01:FOECLOSE'] = 1
