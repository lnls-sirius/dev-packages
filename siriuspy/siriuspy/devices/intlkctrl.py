"""Beamline Control."""

import time as _time

from .device import Device as _Device


class ASPPSCtrl(_Device):
    """Accelerator PPS Control."""

    DEVICE = 'AS-Glob:PP-Summary'

    PROPERTIES_DEFAULT = (
        'TunAccessWaitTime-Cte',
        'TunAccessWaitTimeLeft-Mon',
        'TunAccessWaitTimeElapsed-Mon',
    )

    def __init__(self, props2init='all', **kwargs):
        """Init."""
        super().__init__(ASPPSCtrl.DEVICE, props2init=props2init, **kwargs)

    @property
    def tunnel_access_wait_time(self):
        """Return total wait time for tunnel access [s]."""
        return self['TunAccessWaitTime-Cte']

    @property
    def tunnel_access_wait_time_left(self):
        """Return wait time left for tunnel access [s]."""
        return self['TunAccessWaitTimeLeft-Mon']

    @property
    def tunnel_access_wait_time_elapsed(self):
        """Return wait time elapsed for tunnel access [s]."""
        return self['TunAccessWaitTimeElapsed-Mon']


class ASMPSCtrl(_Device):
    """Accelerator MPS Control."""

    DEVICE = 'AS-Glob:MP-Summary'

    PROPERTIES_DEFAULT = (
        'AlarmGammaShutter-Mon',
        'DsblGamma-Cmd', 'EnblGamma-Cmd',
        # 'DsblGamma-Mon', 'EnblGamma-Mon',
        )

    def __init__(self, props2init='all', **kwargs):
        """Init."""
        super().__init__(ASMPSCtrl.DEVICE, props2init=props2init, **kwargs)

    @property
    def gamma_enabled(self):
        """."""
        return self['AlarmGammaShutter-Mon'] == 1

    @property
    def gamma_disabled(self):
        """."""
        return self['AlarmGammaShutter-Mon'] == 0

    def cmd_gamma_enable(self, timeout=None):
        """Enable gamma signal for beamlines."""
        self['EnblGamma-Cmd'] = 1
        return self._wait('AlarmGammaShutter-Mon', 1, timeout)

    def cmd_gamma_disable(self, timeout=None):
        """Disable gamma signal for beamlines."""
        self['DsblGamma-Cmd'] = 1
        return self._wait('AlarmGammaShutter-Mon', 0, timeout)


class BLInterlockCtrl(_Device):
    """Beamline Interlock Control."""

    TIMEOUT_GATEVALVE = 20  # [s]
    TIMEOUT_SHUTTER = 7  # [s]
    TIMEOUT_EPS_RESET = 3  # [s]

    class DEVICES:
        """Devices names."""

        CAX = 'CAX'
        ALL = (CAX, )

    PROPERTIES_DEFAULT = (
        # Status da liberação do gamma pela máquina – 1 indica liberado
        'M:PPS01:HABILITACAO_MAQUINA',

        # general EPS status for frontend shutter
        'F:PPS01:HABILITACAO_EPS_GS_X',

        # general EPS status for hutchA shutter
        'A:PPS01:HABILITACAO_EPS',

        # EPS status
        'A:EPS01:StatusPos',
        'A:EPS01:StatusTemp',
        'A:EPS01:StatusVac',
        'B:EPS01:StatusVac',
        'F:EPS01:StatusPos',
        'F:EPS01:StatusTemp',
        'F:EPS01:StatusVac',

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

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        if devname is None:
            devname = self.DEVICES.CAX
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)

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
    def is_hutchA_eps_dvf_pos_ok(self):
        """."""
        return bool(self['A:EPS01:StatusPos'])

    @property
    def is_hutchA_eps_temperatures_ok(self):
        """."""
        return bool(self['A:EPS01:StatusTemp'])

    @property
    def is_hutchA_eps_vacuum_ok(self):
        """."""
        return bool(self['A:EPS01:StatusVac'])

    @property
    def is_hutchB_eps_vacuum_ok(self):
        """."""
        return bool(self['B:EPS01:StatusVac'])

    @property
    def is_frontend_eps_mirror_pos_ok(self):
        """."""
        return bool(self['F:EPS01:StatusPos'])

    @property
    def is_frontend_eps_temperatures_ok(self):
        """."""
        return bool(self['F:EPS01:StatusTemp'])

    @property
    def is_frontend_eps_vacuum_ok(self):
        """."""
        return bool(self['F:EPS01:StatusVac'])

    @property
    def is_frontend_gatevalves_opened(self):
        """."""
        if not bool(self['A:EPS01:GV5open']):
            return False
        if not bool(self['F:EPS01:GV4open']):
            return False
        if not bool(self['F:EPS01:GV3open']):
            return False
        # NOTE: GV2open not installed yet.
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
    def is_hutchB_gatevalves_opened(self):
        """."""
        if not bool(self['B:EPS01:GV7open']):
            return False
        if not bool(self['A:EPS01:GV6open']):
            return False
        return True

    @property
    def is_hutchB_gatevalves_closed(self):
        """."""
        if not bool(self['B:EPS01:GV7closed']):
            return False
        if not bool(self['A:EPS01:GV6closed']):
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

    @property
    def is_frontend_eps_ok(self):
        """."""
        state = True
        state &= self.is_frontend_eps_mirror_pos_ok
        state &= self.is_frontend_eps_temperatures_ok
        state &= self.is_frontend_eps_vacuum_ok
        return state

    @property
    def is_hutchA_eps_ok(self):
        """."""
        state = True
        state &= self.is_hutchA_eps_dvf_pos_ok
        state &= self.is_hutchA_eps_temperatures_ok
        state &= self.is_hutchA_eps_vacuum_ok
        return state

    @property
    def is_hutchB_eps_ok(self):
        """."""
        state = True
        state &= self.is_hutchB_eps_vacuum_ok
        return state

    @property
    def is_beamline_eps_ok(self):
        """."""
        state = True
        state &= self.is_frontend_eps_ok
        state &= self.is_hutchA_eps_ok
        state &= self.is_hutchB_eps_ok
        return state

    @property
    def is_beamline_opened(self):
        """Return whether BL is opened."""
        if not self.is_hutchA_intlk_search_done:
            return False
        if not self.is_hutchB_intlk_search_done:
            return False
        if not self.is_machine_gamma_enabled:
            return False
        if not self.is_beamline_eps_ok:
            return False
        if not self.is_frontend_shutter_eps_permission_ok:
            return False
        if not self.is_hutchA_shutter_eps_permission_ok:
            return False
        if not self.is_frontend_gamma_shutter_opened or \
                not self.is_frontend_photon_shutter_opened:
            return False
        if not self.is_hutchA_gamma_shutter_opened:
            return False
        return True

    def cmd_beamline_eps_reset(self):
        """."""
        self['F:EPS01:resetCmd'] = 1

    def cmd_frontend_gatevalves_open(self, timeout=None):
        """."""
        if self.is_frontend_gatevalves_opened:
            return True
        else:
            self['F:EPS01:openGates'] = 1

        if timeout is None:
            return True
        t0 = _time.time()
        while not self.is_frontend_gatevalves_opened:
            if _time.time() - t0 > timeout:
                print('open frontend gatevalve timeout reached!')
                return False
            _time.sleep(0.5)

        return True

    def cmd_hutchB_gatevalves_open(self, timeout=None):
        """."""
        if self.is_hutchB_gatevalves_opened:
            return True
        else:
            self['B:EPS01:openGates'] = 1

        if timeout is None:
            return True
        t0 = _time.time()
        while not self.is_hutchB_gatevalves_opened:
            if _time.time() - t0 > timeout:
                print('open hutchB gatevalve timeout reached!')
                return False
            _time.sleep(0.5)

        return True

    def cmd_frontend_gamma_and_photon_open(self, timeout=None):
        """."""
        if self.is_frontend_gamma_shutter_opened and \
                self.is_frontend_photon_shutter_opened:
            return True
        else:
            self['F:PPS01:FOEOPEN'] = 1

        if timeout is None:
            return True
        t0 = _time.time()
        while \
                not self.is_frontend_gamma_shutter_opened or \
                not self.is_frontend_photon_shutter_opened:
            if _time.time() - t0 > timeout:
                print('open frontend shutter timeout reached!')
                return False
            _time.sleep(0.5)

        return True

    def cmd_frontend_gamma_and_photon_close(self, timeout=None):
        """."""
        if \
                not self.is_frontend_gamma_shutter_opened and \
                not self.is_frontend_photon_shutter_opened:
            return True
        else:
            self['F:PPS01:FOECLOSE'] = 1

        if timeout is None:
            return True
        t0 = _time.time()
        while \
                self.is_frontend_gamma_shutter_opened or \
                self.is_frontend_photon_shutter_opened:
            if _time.time() - t0 > timeout:
                print('close frontend shutter timeout reached!')
                return False
            _time.sleep(0.5)

        return True

    def cmd_hutchA_photon_open(self, timeout=None):
        """."""
        if self.is_hutchA_gamma_shutter_opened:
            return True
        else:
            self['A:PPS01:OEAOPENCLOSE'] = 1

        if timeout is None:
            return True
        t0 = _time.time()
        while not self.is_hutchA_gamma_shutter_opened:
            if _time.time() - t0 > timeout:
                print('open hutchA photon shutter timeout reached!')
                return False
            _time.sleep(0.5)

        return True

    def cmd_hutchA_photon_close(self, timeout=None):
        """."""
        if not self.is_hutchA_gamma_shutter_opened:
            return True
        else:
            self['A:PPS01:OEAOPENCLOSE'] = 1

        if timeout is None:
            return True
        t0 = _time.time()
        while self.is_hutchA_gamma_shutter_opened:
            if _time.time() - t0 > timeout:
                print('close hutchA photon shutter timeout reached!')
                return False
            _time.sleep(0.5)

        return True

    def cmd_beamline_open(self):
        """."""
        if not self.is_hutchA_intlk_search_done:
            print('hutchA search is not done!')
            return False

        if not self.is_hutchB_intlk_search_done:
            print('hutchB search is not done!')
            return False

        if not self.is_machine_gamma_enabled:
            print('machine gamma signal not enabled.')
            return False

        # check and reset EPS
        if not self.is_beamline_eps_ok:
            print('beamline eps reset')
            self.cmd_beamline_eps_reset()
            t0 = _time.time()
            while not self.is_beamline_eps_ok:
                if _time.time() - t0 > self.TIMEOUT_EPS_RESET:
                    print('eps reset timeout reached!')
                    return False
                _time.sleep(0.5)

        # check frontend shutter permission and open gatevalves for hutchA
        if not self.is_frontend_shutter_eps_permission_ok:
            print('open frontend and hutchA gatevalves')
            # open frontend and hutchA gatevalves
            self.cmd_frontend_gatevalves_open()
            t0 = _time.time()
            while not self.is_frontend_gatevalves_opened:
                if _time.time() - t0 > self.TIMEOUT_GATEVALVE:
                    msg = 'open frontend and hutchA gatevalve timeout reached!'
                    print(msg)
                    return False
                _time.sleep(0.5)

        # check hutchA shutter permission and open gatevalves for hutchB
        if not self.is_hutchA_shutter_eps_permission_ok:
            print('open hutchB gatevalves')
            is_ok = self.cmd_hutchB_gatevalves_open(
                timeout=self.TIMEOUT_GATEVALVE)
            if not is_ok:
                return False

        # open frontend gamma and photon shutter
        print('open frontend gamma and photon shutters')
        is_ok = self.cmd_frontend_gamma_and_photon_open(
            timeout=self.TIMEOUT_SHUTTER)
        if not is_ok:
            return False

        # open hutchA photon shutter
        print('open hutchA photon shutter')
        is_ok = self.cmd_hutchA_photon_open(timeout=self.TIMEOUT_SHUTTER)
        if not is_ok:
            return False

        return True
