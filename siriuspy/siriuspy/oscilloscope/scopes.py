"""Oscilloscopes and scope psignals."""


class Scopes:
    """Keysight oscilloscopes names and IPs."""

    AS_DI_FCTDIG = '10.128.150.22'  # 'AS-DI-FCTDig.lnls-sirius.com.br'
    AS_DI_FPMDIG = '10.128.150.21'  # 'AS-DI-FPMDig.lnls-sirius.com.br'
    LI_DI_ICTOSC = '10.128.1.150'  # 'li-di-ictosc.lnls-sirius.com.br'
    LI_PU_OSC_MODLTR = '10.128.150.20'  # 'KEYSIGH-QQI8MNR.abtlus.org.br'
    TB_PU_OSC_INJBO = '10.128.101.70'  # 'TB-PU-Osc-InjBO.abtlus.org.br'
    TS_PU_OSC_EJEBO = '10.128.120.70'  # 'TS-PU-Osc-EjeBO.abtlus.org.br'
    TS_PU_OSC_INJSI = '10.128.101.72'  # 'TS-PU-Osc-InjSI.abtlus.org.br'
    SI_PU_OSC_INJSI = '10.128.101.71'  # 'SI-PU-Osc-InjSI.abtlus.org.br'


class ScopeSignals:
    """Mapping of physical signals to scope channels."""

    SI_FILL_PATTERN = (Scopes.AS_DI_FPMDIG, 5025, 'CHAN1')
    BO_FILL_PATTERN = (Scopes.AS_DI_FPMDIG, 5025, 'CHAN4')
    TS_EJESEPTG_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN1')
    TS_EJESEPTF_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN2')
    BO_EJEKCKR_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN3')
    SI_PINGV_PULSE = (Scopes.TS_PU_OSC_EJEBO, 5025, 'CHAN4')
    LI_ICT1 = (Scopes.LI_DI_ICTOSC, 5025, 'CHAN1')
    LI_ICT2 = (Scopes.LI_DI_ICTOSC, 5025, 'CHAN2')
    TB_ICT1 = (Scopes.LI_DI_ICTOSC, 5025, 'CHAN3')
    TB_ICT2 = (Scopes.LI_DI_ICTOSC, 5025, 'CHAN4')
    TS_ICT1 = (Scopes.AS_DI_FCTDIG, 5025, 'CHAN3')
    TS_ICT2 = (Scopes.AS_DI_FCTDIG, 5025, 'CHAN4')
    MODLTR1_PULSE = (Scopes.LI_PU_OSC_MODLTR, 5025, 'CHAN1')
    MODLTR2_PULSE = (Scopes.LI_PU_OSC_MODLTR, 5025, 'CHAN3')

    @staticmethod
    def get_scope(scope_signal=None, scope=None):
        """."""
        if scope_signal is not None:
            if scope and scope_signal[0] != scope:
                raise ValueError('Inconsistent inputs!')
            scope = scope_signal[0]
        for symb in Scopes.__dict__:
            if symb[:2] in ('AS', 'LI', 'TB', 'TS', 'SI'):
                host = getattr(Scopes, symb)
                if host == scope:
                    return symb

    @staticmethod
    def get_signals(scope):
        """."""
        signals = dict()
        for symb in ScopeSignals.__dict__:
            if symb[:2] in ('SI', 'BO', 'TS', 'LI', 'TB', 'MO'):
                sig = getattr(ScopeSignals, symb)
                if sig[0] == scope:
                    signals[symb] = sig
        return signals
