"""Oscilloscopes and scope psignals."""


class Scopes:
    """Keysight oscilloscopes names and IPs."""

    AS_DI_FCTDIG = 'AS-DI-FCTDig.lnls-sirius.com.br'  # '10.128.150.124'
    AS_DI_FPMDIG = 'AS-DI-FPMDig.lnls-sirius.com.br'  # '10.128.150.77'
    LI_DI_ICTOSC = 'li-di-ictosc.lnls-sirius.com.br'  # '10.128.1.52'
    LI_PU_OSC_MODLTR = 'KEYSIGH-QQI8MNR.abtlus.org.br'  # '10.0.38.48'
    TB_PU_OSC_INJBO = 'TB-PU-Osc-InjBO.abtlus.org.br'  # '10.0.38.74'
    TS_PU_OSC_EJEBO = 'TS-PU-Osc-EjeBO.abtlus.org.br'  # '10.0.38.77'
    TS_PU_OSC_INJSI = 'TS-PU-Osc-InjSI.abtlus.org.br'  # '10.0.38.20'
    SI_PU_OSC_INJSI = 'SI-PU-Osc-InjSI.abtlus.org.br'  # '10.0.38.69'


class ScopeSignals:
    """Mapping of physical signals to scope channels."""

    SI_FILL_PATTERN = (Scopes.AS_DI_FPMDIG, 5025, 'CHAN1')
    BO_FILL_PATTERN = (Scopes.AS_DI_FPMDIG, 5025, 'CHAN2')
    TS_EJESEPTG_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN1')
    TS_EJESEPTF_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN2')
    BO_EJEKCKR_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN3')
    SI_PINGV_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN4')

    @staticmethod
    def get_scope_name(scopesignal=None, scope_ip=None):
        """."""
        for symb in Scopes.__dict__:
            if symb[:2] in ('AS', 'LI', 'TB', 'BO', 'TS', 'SI'):
                scope_ip = getattr(Scopes, symb)
                if scope_ip == scopesignal[0] or scope_ip == scope_ip:
                    return symb
