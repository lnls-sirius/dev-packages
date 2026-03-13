"""Gamma Monitor Search module."""

from ..namesys import Filter as _Filter, SiriusPVName as _SiriusPVName


class GammaMonitorSearch:
    """Gamma Monitor Search Class."""

    # TODO: This mapping should be moved to a configuration file at
    # control-system-constants, and not hardcoded in the code.
    _gamma2counter = {
        'SI-01M2:CO-Gamma': 'SI-01C2:CO-Counter:Ch1',
        'SI-01C1:CO-Gamma': 'SI-01C2:CO-Counter:Ch2',
        'SI-01C2:CO-Gamma': 'SI-01C3:CO-Counter:Ch1',
        'SI-01C3:CO-Gamma': 'SI-01C3:CO-Counter:Ch2',
        'SI-01C4:CO-Gamma': 'SI-02M1:CO-Counter:Ch1',
        'SI-02M2:CO-Gamma': 'SI-02C2:CO-Counter:Ch1',
        'SI-02C1:CO-Gamma': 'SI-02C2:CO-Counter:Ch2',
        'SI-02C2:CO-Gamma': 'SI-02C3:CO-Counter:Ch1',
        'SI-02C3:CO-Gamma': 'SI-02C3:CO-Counter:Ch2',
        'SI-02C4:CO-Gamma': 'SI-03M1:CO-Counter:Ch1',
        'SI-03M2:CO-Gamma': 'SI-03C2:CO-Counter:Ch1',
        'SI-03C1:CO-Gamma': 'SI-03C2:CO-Counter:Ch2',
        'SI-03C2:CO-Gamma': 'SI-03C3:CO-Counter:Ch1',
        'SI-03C3:CO-Gamma': 'SI-03C3:CO-Counter:Ch2',
        'SI-03C4:CO-Gamma': 'SI-04M1:CO-Counter:Ch1',
        'SI-04M2:CO-Gamma': 'SI-04C2:CO-Counter:Ch1',
        'SI-04C1:CO-Gamma': 'SI-04C2:CO-Counter:Ch2',
        'SI-04C2:CO-Gamma': 'SI-04C3:CO-Counter:Ch1',
        'SI-04C3:CO-Gamma': 'SI-04C3:CO-Counter:Ch2',
        'SI-04C4:CO-Gamma': 'SI-05M1:CO-Counter:Ch1',
        'SI-05M2:CO-Gamma': 'SI-05C2:CO-Counter:Ch1',
        'SI-05C1:CO-Gamma': 'SI-05C2:CO-Counter:Ch2',
        'SI-05C2:CO-Gamma': 'SI-05C3:CO-Counter:Ch1',
        'SI-05C3:CO-Gamma': 'SI-05C3:CO-Counter:Ch2',
        'SI-05C4:CO-Gamma': 'SI-06M1:CO-Counter:Ch1',
        'SI-06M2:CO-Gamma': 'SI-06C2:CO-Counter:Ch1',
        'SI-06C1:CO-Gamma': 'SI-06C2:CO-Counter:Ch2',
        'SI-06C2:CO-Gamma': 'SI-06C3:CO-Counter:Ch1',
        'SI-06C3:CO-Gamma': 'SI-06C3:CO-Counter:Ch2',
        'SI-06C4:CO-Gamma': 'SI-07M1:CO-Counter:Ch1',
        'SI-07M2:CO-Gamma': 'SI-07C2:CO-Counter:Ch1',
        'SI-07C1:CO-Gamma': 'SI-07C2:CO-Counter:Ch2',
        'SI-07C2:CO-Gamma': 'SI-07C3:CO-Counter:Ch1',
        'SI-07C3:CO-Gamma': 'SI-07C3:CO-Counter:Ch2',
        'SI-07C4:CO-Gamma': 'SI-08M1:CO-Counter:Ch1',
        'SI-08M2:CO-Gamma': 'SI-08C2:CO-Counter:Ch1',
        'SI-08C1:CO-Gamma': 'SI-08C2:CO-Counter:Ch2',
        'SI-08C2:CO-Gamma': 'SI-08C3:CO-Counter:Ch1',
        'SI-08C3:CO-Gamma': 'SI-08C3:CO-Counter:Ch2',
        'SI-08C4:CO-Gamma': 'SI-09M1:CO-Counter:Ch1',
        'SI-09M2:CO-Gamma': 'SI-09C2:CO-Counter:Ch1',
        'SI-09C1:CO-Gamma': 'SI-09C2:CO-Counter:Ch2',
        'SI-09C2:CO-Gamma': 'SI-09C3:CO-Counter:Ch1',
        'SI-09C3:CO-Gamma': 'SI-09C3:CO-Counter:Ch2',
        'SI-09C4:CO-Gamma': 'SI-10M1:CO-Counter:Ch1',
        'SI-10M2:CO-Gamma': 'SI-10C2:CO-Counter:Ch1',
        'SI-10C1:CO-Gamma': 'SI-10C2:CO-Counter:Ch2',
        'SI-10C2:CO-Gamma': 'SI-10C3:CO-Counter:Ch1',
        'SI-10C3:CO-Gamma': 'SI-10C3:CO-Counter:Ch2',
        'SI-10C4:CO-Gamma': 'SI-11M1:CO-Counter:Ch1',
        'SI-11M2:CO-Gamma': 'SI-11C2:CO-Counter:Ch1',
        'SI-11C1:CO-Gamma': 'SI-11C2:CO-Counter:Ch2',
        'SI-11C2:CO-Gamma': 'SI-11C3:CO-Counter:Ch1',
        'SI-11C3:CO-Gamma': 'SI-11C3:CO-Counter:Ch2',
        'SI-11C4:CO-Gamma': 'SI-12M1:CO-Counter:Ch1',
        'SI-12M2:CO-Gamma': 'SI-12C2:CO-Counter:Ch1',
        'SI-12C1:CO-Gamma': 'SI-12C2:CO-Counter:Ch2',
        'SI-12C2:CO-Gamma': 'SI-12C3:CO-Counter:Ch1',
        'SI-12C3:CO-Gamma': 'SI-12C3:CO-Counter:Ch2',
        'SI-12C4:CO-Gamma': 'SI-13M1:CO-Counter:Ch1',
        'SI-13M2:CO-Gamma': 'SI-13C2:CO-Counter:Ch1',
        'SI-13C1:CO-Gamma': 'SI-13C2:CO-Counter:Ch2',
        'SI-13C2:CO-Gamma': 'SI-13C3:CO-Counter:Ch1',
        'SI-13C3:CO-Gamma': 'SI-13C3:CO-Counter:Ch2',
        'SI-13C4:CO-Gamma': 'SI-14M1:CO-Counter:Ch1',
        'SI-14M2:CO-Gamma': 'SI-14C2:CO-Counter:Ch1',
        'SI-14C1:CO-Gamma': 'SI-14C2:CO-Counter:Ch2',
        'SI-14C2:CO-Gamma': 'SI-14C3:CO-Counter:Ch1',
        'SI-14C3:CO-Gamma': 'SI-14C3:CO-Counter:Ch2',
        'SI-14C4:CO-Gamma': 'SI-15M1:CO-Counter:Ch1',
        'SI-15M2:CO-Gamma': 'SI-15C2:CO-Counter:Ch1',
        'SI-15C1:CO-Gamma': 'SI-15C2:CO-Counter:Ch2',
        'SI-15C2:CO-Gamma': 'SI-15C3:CO-Counter:Ch1',
        'SI-15C3:CO-Gamma': 'SI-15C3:CO-Counter:Ch2',
        'SI-15C4:CO-Gamma': 'SI-16M1:CO-Counter:Ch1',
        'SI-16M2:CO-Gamma': 'SI-16C2:CO-Counter:Ch1',
        'SI-16C1:CO-Gamma': 'SI-16C2:CO-Counter:Ch2',
        'SI-16C2:CO-Gamma': 'SI-16C3:CO-Counter:Ch1',
        'SI-16C3:CO-Gamma': 'SI-16C3:CO-Counter:Ch2',
        'SI-16C4:CO-Gamma': 'SI-17M1:CO-Counter:Ch1',
        'SI-17M2:CO-Gamma': 'SI-17C2:CO-Counter:Ch1',
        'SI-17C1:CO-Gamma': 'SI-17C2:CO-Counter:Ch2',
        'SI-17C2:CO-Gamma': 'SI-17C3:CO-Counter:Ch1',
        'SI-17C3:CO-Gamma': 'SI-17C3:CO-Counter:Ch2',
        'SI-17C4:CO-Gamma': 'SI-18M1:CO-Counter:Ch1',
        'SI-18M2:CO-Gamma': 'SI-18C2:CO-Counter:Ch1',
        'SI-18C1:CO-Gamma': 'SI-18C2:CO-Counter:Ch2',
        'SI-18C2:CO-Gamma': 'SI-18C3:CO-Counter:Ch1',
        'SI-18C3:CO-Gamma': 'SI-18C3:CO-Counter:Ch2',
        'SI-18C4:CO-Gamma': 'SI-19M1:CO-Counter:Ch1',
        'SI-19M2:CO-Gamma': 'SI-19C2:CO-Counter:Ch1',
        'SI-19C1:CO-Gamma': 'SI-19C2:CO-Counter:Ch2',
        'SI-19C2:CO-Gamma': 'SI-19C3:CO-Counter:Ch1',
        'SI-19C3:CO-Gamma': 'SI-19C3:CO-Counter:Ch2',
        'SI-19C4:CO-Gamma': 'SI-20M1:CO-Counter:Ch1',
        'SI-20M2:CO-Gamma': 'SI-20C2:CO-Counter:Ch1',
        'SI-20C1:CO-Gamma': 'SI-20C2:CO-Counter:Ch2',
        'SI-20C2:CO-Gamma': 'SI-20C3:CO-Counter:Ch1',
        'SI-20C3:CO-Gamma': 'SI-20C3:CO-Counter:Ch2',
        'SI-20C4:CO-Gamma': 'SI-01M1:CO-Counter:Ch1',
    }
    _gamma2counter = {
        _SiriusPVName(gamma): _SiriusPVName(counter)
        for gamma, counter in _gamma2counter.items()
    }

    @staticmethod
    def get_gammanames(filters=None):
        """Return a sorted and filtered list of all Gamma names."""
        gamma_names_list = list(GammaMonitorSearch._gamma2counter.keys())
        gamma_names = _Filter.process_filters(
            gamma_names_list, filters=filters
        )
        return sorted(gamma_names)

    @staticmethod
    def get_counter_names(filters=None):
        """Return a sorted and filtered list of all Counter names."""
        counter_names = list({
            dev.device_name
            for dev in GammaMonitorSearch._gamma2counter.values()
        })
        counter_names = _Filter.process_filters(counter_names, filters=filters)
        return sorted(counter_names)

    @staticmethod
    def conv_gammaname_2_countername(gammaname):
        """Return the counter name to which the gamma monitor is connected."""
        return GammaMonitorSearch._gamma2counter[gammaname].device_name

    @staticmethod
    def conv_gammaname_2_counter_channel(gammaname):
        """Return the counter channel of a Gamma Monitor."""
        return GammaMonitorSearch._gamma2counter[gammaname].propty
