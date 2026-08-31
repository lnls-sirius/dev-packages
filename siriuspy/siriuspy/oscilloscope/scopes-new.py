"""Oscilloscopes and scope psignals."""


class Scopes:
    """Keysight oscilloscopes names and IPs."""

<<<<<<< Updated upstream
    AS_DI_FCTDIG = '10.128.150.22'  # 'AS-DI-FCTDig.lnls-sirius.com.br'
    AS_DI_FPMDIG = '10.128.150.21'  # 'AS-DI-FPMDig.lnls-sirius.com.br'
    LI_DI_ICTOSC = '10.128.1.150'  # 'li-di-ictosc.lnls-sirius.com.br'
    LI_PU_OSC_MODLTR = '10.128.150.20'  # 'KEYSIGH-QQI8MNR.abtlus.org.br'
    TB_PU_OSC_INJBO = '10.128.101.70'  # 'TB-PU-Osc-InjBO.abtlus.org.br'
    TS_PU_OSC_EJEBO = '10.128.120.70'  # 'TS-PU-Osc-EjeBO.abtlus.org.br'
    TS_PU_OSC_INJSI = '10.128.101.72'  # 'TS-PU-Osc-InjSI.abtlus.org.br'
    SI_PU_OSC_INJSI = '10.128.101.71'  # 'SI-PU-Osc-InjSI.abtlus.org.br'
=======
    AS_DI_FCTDIG = '10.128.150.22'      # 'AS-DI-Osc-IctFct.abtlus.org.br'
    # channel 1 "TB-04:FCT"
    #   f1      "TS-ICT1-integral" -> src "channel 1" : integrate
    #   f3      "TB-ICT1-charge"   -> src f1          : 1/5
    #   f11     "TB-04-FCT"        -> src "channel 1" : high pass filter 60MHz
    # channel 2 "TS-04:FCT"
    #   f2      "TB-ICT2-integral" -> src "channel 2" : integrate
    #   f4      "TB-ICT2-charge"   -> src f2          : 1/5
    #   f12     "TB-04-FCT"        -> src "channel 2" : high pass filter 60MHz
    # channel 3 "TS-01:ICT"
    #   f6      "TS-ICT1-integral" -> src "channel 3" : integrate
    #   f8      "Charge-TS-ICT1"   -> src f6          : 1/5
    #   m1      "Charge TS-ICT2"   -> src f8          : Vpp
    #   m2      "Charge TS-ICT1"   -> src f8          : Vpp
    # channel 4 "TS-04:ICT"
    #   f7      "TS-ICT2-integral" -> src "channel 4" : integrate
    #   f9      "Charge-TS-ICT2"   -> src f7          : 1/5
    # f5      "efficiency"       -> src f3, f4        : / ?
    # f10     "efficiency-TS"    -> src f8, f9        : / ?

    AS_DI_FPMDIG = '10.128.150.21'      # 'AS-DI-Osc-FPMDig.abtlus.org.br'
    # channel 1 "SI-17C4:TunePkup" (SI FPM)
    #   f1      "SI-17C4:TunePkup" -> src "channel 1" : high pass filter 60MHz
    #   m1      "Period"           -> src "channel 1" : ?
    #   m2      "Duty cycle"       -> src "channel 1" : ?
    # channel 2 "SI-18SB:TunePkup"
    #   f2      "SI-18SB:TunePkup" -> src "channel 2" : high pass filter 60MHz
    # channel 3 "BO-04U:TuneSigma" (BO FPM)
    #   f3      "BO-04U:TuneSigma" -> src "channel 3" : high pass filter 60MHz
    # channel 4 "BO-04D:GSL07Sigm"
    #   f4      "BO-04D:GLS07Sigm" -> src "channel 4" : high pass filter 60MHz

    LI_DI_ICTOSC = '10.128.1.150'       # 'LI-DI-Osc-Ict.abtlus.org.br'
    # channel 1 LI-01:ICT-1
    #   f1 Integral-LI-ICT1 Integrate (channel 1)
    #   f3 charge-LI-ICT1 f3 = f1/5
    #   m4 Charge-LI-ICT2 Vpp f3
    # channel 2 LI-01:ICT-2
    #   f2 Integral-LI-ICT2 Integrate (channel 2)
    #   f4 charge-LI-ICT2 f4 = f2/5
    #   m3 Charge-LI-ICT2 Vpp f4
    # channel 3 TB-02:ICT
    #   f5 integral-TB-ICT1 Integrate (channel 3)
    #   f7 charge-TB-ICT1 f7 = f5/5
    #   m2 Charge-TB-ICT1 Vpp f7
    # channel 4 TB-04:ICT
    #   f6 integral-TB-ICT2 Integrate (channel 4)
    #   f8 charge-TB-ICT2 f8 = f6/5
    #   m1 Charge-TB-ICT2 Vpp f8

    LI_PU_OSC_MODLTR = '10.128.150.20'  # 'LI-PU-Osc-Modltr.abtlus.org.br'
    # channel 1 "Mod_01"  (LI-01:Modltr-1)
    # m2 "Vmin" Vmin (channel 1)
    # channel 2 TB-04-ICT ???
    # channel 3 "Mod_02"  (LI-01:Modltr-2)
    # m1 "Vmin" Vmin (channel 3)
    # channel 4 "4" ?

    TB_PU_OSC_INJBO = '10.128.101.70'   # 'TB-PU-Osc-InjBO.abtlus.org.br'
    # channel 1 "Boo_Inj_Sep" (TB-04:InjSept)
    # m1 "Vpp" Vpp (channel 1)
    # m2 "Period" Period (channel 1)
    # m3 "Frequency" Frequency (channel 1)
    # m4 "Rise time" Rise time (channel 1)
    # m5 "Fall time" Fall time (channel 1)
    # m6 "V max" V max (channel 1)
    # m7 "V min" V min (channel 1)
    # m8 "+ width" + width (channel 1)
    # m9 "- width" - width (channel 1)
    # m10 "Duty cycle" Duty cycle (channel 1)
    # channel 2 "TCLK" ?
    # channel 3 "Boo_Inj_KC" (BO-01D:InjKckr)
    # f1 "f1" Integrate (channel 3)
    # f2 "f2" f2 = channel 3 - m3
    # f3 "f3" f3 = -700u + channel 3
    # f4 "f4" Integrate (f3)

    # channel 4 "Trg" ?

    TS_PU_OSC_EJEBO = '10.128.120.70'   # 'TS-PU-Osc-EjeBO.abtlus.org.br'
    # channel 1 "1" ?
    # m2 "TS-01:PU-EjeSeptF" Vmax (channel 1)
    # channel 2 "Boo_Thick_Sep" (TS-01:EjeSeptG)
    # m3 "TS-01:PU-EjeSeptG" V max (channel 2)
    # channel 3 "3" ?
    # m4 "BO-48D:PU-EjeKckr" V max (channel 3)
    # channel 4 "PingerV" (SI-19C4:PingV)
    # m1 "SI-19C4:PU-PingV" V max (channel 4)

    TS_PU_OSC_INJSI = '10.128.101.72'   # 'TS-PU-Osc-InjSI.abtlus.org.br'
    # channel 1 "1" (TS-04:InjSeptG-2)
    # m1 "TS-04:PU-InjSeptG-2" V max (channel 1)
    # channel 2 "2" (TS-04:InjSeptG-1)
    # m2 "TS-04:PU-InjSeptG-1" V max (channel 2)
    # channel 3 "3" (TS-04:InjSeptF)
    # m3 "TS-04:PU-InjSeptF" V max (channel 3)
    # channel 4 "4" ?

    SI_PU_OSC_INJSI = '10.128.101.71'   # 'SI-PU-Osc-InjSI.abtlus.org.br'
    # channel 1 "1" -> SI-??:InjSeptF
    #   m4 "V max" V max (channel 1)
    # channel 2 "2" -> Pulso de corrente na bobina da corretora horizontal do NLK
    #   m3 "V max" V max (channel 2)
    # channel 3 "3" -> Pulso de corrente do NLK
    #   m5 "V max" V max (channel 3)
    # channel 4 "4" -> Pulso de corrente na bobina da corretora vertical do NLK
    #   m1 "V min" V min (channel 4)
    #   m2 "V max" V max (channel 4)





>>>>>>> Stashed changes


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
    def get_scope(scope_signal=None, scope_hostname=None):
        """."""
        if scope_signal is not None:
            if scope_hostname and scope_signal[0] != scope_hostname:
                raise ValueError('Inconsistent inputs!')
            scope_hostname = scope_signal[0]
        for symb in Scopes.__dict__:
            if symb[:2] in ('AS', 'LI', 'TB', 'BO', 'TS', 'SI'):
                host = getattr(Scopes, symb)
                if host == scope_hostname:
                    return symb
