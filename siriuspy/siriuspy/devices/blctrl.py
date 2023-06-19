"""Beamline Control."""

import time as _time
from .device import DeviceNC as _DeviceNC


class BLPPSCtrl(_DeviceNC):
    """Beamline Control."""

    GATEVALVE_TIMEOUT = 20  # [s]
    SHUTTER_TIMEOUT = 7  # [s]

    class DEVICES:
        """Devices names."""

        CAX = 'CAX'
        ALL = (CAX, )

    _properties = (
        # Status da liberação do gamma pela máquina – 1 indica liberado
        'M:PPS01:HABILITACAO_MAQUINA',

        # general EPS status for frontend shutter
        'F:PPS01:HABILITACAO_EPS_GS_X',

        # general EPS status for hutchA shutter
        'A:PPS01:HABILITACAO_EPS',

        # open front-end and first hutchA valve gates
        'F:EPS01:openGates',

        'A:EPS01:GV5open', 'A:EPS01:GV5closed',  # open/close gate status
        'F:EPS01:GV4open', 'F:EPS01:GV4closed',  # open/close gate status
        'F:EPS01:GV3open', 'F:EPS01:GV3closed',  # open/close gate status
        # 'F:EPS01:GV2open', 'F:EPS01:GV2closed',  # open/close gate status
        'F:EPS01:GV1open', 'F:EPS01:GV1closed',  # open/close gate status

        # reset EPS
        'F:EPS01:resetCmd',

        # Enviar 1 para abrir o Front-end completo (abre o gamma e o photon)
        'F:PPS01:FOEOPEN',

        # Enviar 1 para fechar o Front-end completo (fecha o photon e o gamma)
        'F:PPS01:FOECLOSE',

        # Status photon shutter front-end – 0 indica aberto
        'F:PPS01:PS_STATUS',

        # Status gamma shutter front-end – 0 indica aberto
        'F:PPS01:GS_X_STATUS',

        # shutter da cabana a
        # - Enviar 1 – se estiver fechado abre – se estiver aberto fecha
        'A:PPS01:OEAOPENCLOSE',
        # Status do gamma shutter da cabana A – 0 indica aberto
        'A:PPS01:PG_STATUS',
        # status da procura cabana A – 1 indica procura feita
        'A:PPS01:SEARCH_OK',
        # status da procura cabana B – 1 indica procura feita
        'B:PPS01:SEARCH_OK',
        # open other hutchA and hutchB valve gates
        'B:EPS01:openGates',
        'B:EPS01:GV7open', 'B:EPS01:GV7closed',  # open/close gate status
        'A:EPS01:GV6open', 'A:EPS01:GV6closed',  # open/close gate status
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

    @property
    def is_frontend_gatevalves_opened(self):
        """."""
        if not bool(self['A:EPS01:GV5open']):
            return False
        if not bool(self['F:EPS01:GV4open']):
            return False
        if not bool(self['F:EPS01:GV3open']):
            return False
        # if not bool(self['F:EPS01:GV2open']):
        #     return False
        if not bool(self['F:EPS01:GV1open']):
            return False
        return True

    @property
    def is_frontend_gatevalves_closed(self):
        """."""
        if not bool(self['A:EPS01:GV5closed']):
            return False
        if not bool(self['F:EPS01:GV4closed']):
            return False
        if not bool(self['F:EPS01:GV3closed']):
            return False
        # if not bool(self['F:EPS01:GV2open']):
        #     return False
        if not bool(self['F:EPS01:GV1closed']):
            return False
        return True

    @property
    def is_beamline_gatevalves_opened(self):
        """."""
        if not bool(self['B:EPS01:GV7open']):
            return False
        if not bool(self['A:EPS01:GV6open']):
            return False
        if not self.is_frontend_gatevalves_opened:
            return False
        return True

    @property
    def is_beamline_gatevalves_closed(self):
        """."""
        if not bool(self['B:EPS01:GV7closed']):
            return False
        if not bool(self['A:EPS01:GV6closed']):
            return False
        if not self.is_frontend_gatevalves_closed:
            return False
        return True

    @property
    def is_frontend_shutter_eps_permission_ok(self):
        """."""
        return bool(self['F:PPS01:HABILITACAO_EPS_GS_X'])

    @property
    def is_hutchA_shutter_eps_permission_ok(self):
        """."""
        return bool(self['A:PPS01:HABILITACAO_EPS'])

    def cmd_beamline_eps_reset(self):
        """."""
        self['F:EPS01:resetCmd'] = 1

    def cmd_frontend_gatevalves_open(self):
        """."""
        self['F:EPS01:openGates'] = 1

    def cmd_hutchB_gatevalves_open(self):
        """."""
        self['B:EPS01:openGates'] = 1

    def cmd_frontend_gamma_and_photon_open(self):
        """."""
        self['F:PPS01:FOEOPEN'] = 1

    def cmd_frontend_gamma_and_photon_close(self):
        """."""
        self['F:PPS01:FOECLOSE'] = 1

    def cmd_hutchA_gamma_open(self):
        """."""
        if not self.is_hutchA_gamma_shutter_opened:
            self['A:PPS01:OEAOPENCLOSE'] = 1

    def cmd_hutchA_gamma_close(self):
        """."""
        if self.is_hutchA_gamma_shutter_opened:
            self['A:PPS01:OEAOPENCLOSE'] = 1

    def cmd_open_beamline(self):
        """."""
        if not self.is_machine_gamma_enabled:
            print('Machine gamma signal not enabled.')
            return False

        if not self.is_hutchA_intlk_search_done:
            print('hutchA search is not done!')
            return False

        if not self.is_hutchB_intlk_search_done:
            print('hutchB search is not done!')
            return False

        self.cmd_beamline_eps_reset()
        # self.is_beamline_eps_ok()
        _time.sleep(1.5)  # while is_beamline_eps_ok is not implemented

        if not self.is_hutchA_shutter_eps_permission_ok and \
                not self.is_frontend_shutter_eps_permission_ok:
            # open hutchB gatevalves
            self.cmd_hutchB_gatevalves_open()
            t0 = _time.time()
            while not self.is_beamline_gatevalves_opened:
                if _time.time() - t0 > BLPPSCtrl.GATEVALVE_TIMEOUT:
                    print('open gatevalve timeout reached!')
                    return False
                _time.sleep(0.5)

        self.cmd_frontend_gamma_and_photon_open()
        t0 = _time.time()
        while \
                not self.is_frontend_gamma_shutter_opened or \
                not self.is_frontend_photon_shutter_opened:
            if _time.time() - t0 > BLPPSCtrl.SHUTTER_TIMEOUT:
                print('frontend gamma and photon shutters timeout reached!')
                return False
            _time.sleep(0.5)

        return True
