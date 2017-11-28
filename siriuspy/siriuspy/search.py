"""Search module."""
import copy as _copy

from siriuspy import util as _util
from siriuspy.namesys import Filter as _Filter
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy import servweb as _web
from siriuspy.magnet.excdata import ExcitationData as _ExcitationData


class PSSearch:
    """PS and PU Power Supply Search Class."""

    _connection_timeout = None
    _pstype_dict = None
    _pstype_2_names_dict = None
    _pstype_2_splims_dict = None

    _pstype_2_excdat_dict = dict()

    _splims_labels = None
    _splims_unit = None
    _psnames_list = None

    @staticmethod
    def _reload_pstype_dict():
        """Reload power supply type dictionary from web server."""
        if _web.server_online():
            text = _web.power_supplies_pstypes_names_read(
                timeout=PSSearch._connection_timeout)
            data, params_dict = _util.read_text_data(text)
            PSSearch._pstype_dict = {}
            for datum in data:
                name, polarity, magfunc = datum[0], datum[1], datum[2]
                PSSearch._pstype_dict[name] = (polarity, magfunc)
        else:
            raise Exception('could not read pstypes from web server!')

    @staticmethod
    def _reload_pstype_2_names_dict():
        """Reload power supply type to power supply names dictionary."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        pstypes = sorted(set(PSSearch._pstype_dict.keys()))
        PSSearch._pstype_2_names_dict = {}
        PSSearch._psnames_list = []
        for pstype in pstypes:
            text = _web.power_supplies_pstype_data_read(
                pstype + '.txt', timeout=PSSearch._connection_timeout)
            data, param_dict = _util.read_text_data(text)
            psnames = [_SiriusPVName(datum[0]) for datum in data]
            PSSearch._pstype_2_names_dict[pstype] = psnames
            PSSearch._psnames_list += psnames
        PSSearch._psnames_list = sorted(PSSearch._psnames_list)

    @staticmethod
    def _reload_pstype_2_splims_dict():
        """Reload pstype to splims dictionary."""
        # ps data
        text = _web.power_supplies_pstype_setpoint_limits(
            timeout=PSSearch._connection_timeout)
        ps_data, ps_param_dict = _util.read_text_data(text)
        # pu data
        text = _web.pulsed_power_supplies_pstype_setpoint_limits(
            timeout=PSSearch._connection_timeout)
        pu_data, pu_param_dict = _util.read_text_data(text)

        units = [ps_param_dict['unit'], pu_param_dict['unit']]
        types = ps_param_dict['power_supply_type'] + \
            pu_param_dict['power_supply_type']
        data = ps_data + pu_data

        PSSearch._splims_unit = tuple(units)
        PSSearch._splims_labels = tuple(types)
        PSSearch._pstype_2_splims_dict = {}
        for datum in data:
            pstype, *lims = datum
            PSSearch._pstype_2_splims_dict[pstype] = \
                {PSSearch._splims_labels[i]:
                    float(lims[i]) for i in range(len(lims))}

    @staticmethod
    def _reload_pstype_2_excdat_dict(pstype):
        """Load power supply excitatiom data."""
        if _web.server_online():
            PSSearch._pstype_2_excdat_dict[pstype] = \
                _ExcitationData(filename_web=pstype + '.txt')
        else:
            raise Exception(
                'could not read "' + str(pstype) + '" from web server!')

    @staticmethod
    def get_pstype_dict():
        """Return pstype dictionary.

        With key,value pairs of power supply types and corresponding
        (polarities,mag_function).
        """
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        return _copy.deepcopy(PSSearch._pstype_dict)

    @staticmethod
    def get_pstype_names():
        """Return sorted list of power supply types."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        return sorted(set(PSSearch._pstype_dict.keys()))

    @staticmethod
    def get_polarities():
        """Return sorted list of power supply polarities."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        p = [datum[0] for datum in PSSearch._pstype_dict.values()]
        return sorted(set(p))

    @staticmethod
    def get_pstype_2_names_dict():
        """Return dictionary of power supply type and power supply names."""
        if PSSearch._pstype_2_names_dict is None:
            PSSearch._reload_pstype_2_names_dict()
        return _copy.deepcopy(PSSearch._pstype_2_names_dict)

    @staticmethod
    def conv_psname_2_pstype(name):
        """Return the power supply type of a given power supply name."""
        if PSSearch._pstype_2_names_dict is None:
            PSSearch._reload_pstype_2_names_dict()
        for pstype, names in PSSearch._pstype_2_names_dict.items():
            if name in names:
                return pstype
        print(name)
        return None

    @staticmethod
    def conv_pstype_2_polarity(pstype):
        """Return polarity of a given power supply type."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        for key, value in PSSearch._pstype_dict.items():
            if key == pstype:
                return value[0]
        return None

    @staticmethod
    def conv_pstype_2_magfunc(pstype):
        """Return magnetic function of a given power supply type."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        for key, value in PSSearch._pstype_dict.items():
            if key == pstype:
                return value[1]
        return None

    @staticmethod
    def conv_pstype_2_splims(pstype):
        """Convert pstype to splims."""
        if pstype is None:
            return None
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return _copy.deepcopy(PSSearch._pstype_2_splims_dict[pstype])

    @staticmethod
    def conv_psname_2_excdata(name):
        """Convert psname to excdata."""
        pstype = PSSearch.conv_psname_2_pstype(name)
        if pstype not in PSSearch._pstype_2_excdat_dict:
            PSSearch._reload_pstype_2_excdat_dict(pstype)

        return PSSearch._pstype_2_excdat_dict[pstype]

    @staticmethod
    def get_splim(pstype, label):
        """Return setpoint limit corresponding to given label.

        The label can be either epics' or pcaspy's.
        """
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        if label in PSSearch._splims_labels:
            return PSSearch._pstype_2_splims_dict[pstype][label]
        else:
            label = _util.conv_splims_labels(label)
            if label is None:
                return None
            else:
                return PSSearch._pstype_2_splims_dict[pstype][label]

    @staticmethod
    def get_psnames(filters=None):
        """Return a sorted and filtered list of all power supply names."""
        if PSSearch._pstype_2_names_dict is None:
            PSSearch._reload_pstype_2_names_dict()
        return _Filter.process_filters(PSSearch._psnames_list, filters=filters)

    @staticmethod
    def get_pstype_2_splims_dict():
        """Return a dictionary of power supply type and setpoint limits."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return _copy.deepcopy(PSSearch._pstype_2_splims_dict)

    @staticmethod
    def get_splims_unit():
        """Return SP limts unit."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return PSSearch._splims_unit

    @staticmethod
    def get_splims_labels():
        """Return labels in SP limits dictionary."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return PSSearch._splims_labels


class MASearch:
    """MA and PM Magnet Search class."""

    _connection_timeout = None
    _manames_list = None

    _maname_2_splims_dict = None  # magnets-stpoint-limits file
    _maname_2_psnames_dict = None  # magnet-excitation-ps file
    _maname_2_trim_dict = None
    _splims_labels = None
    _splims_unit = None

    @staticmethod
    def _reload_maname_2_splims_dict():
        """Build dict with limits for each magnet."""
        if _web.server_online():
            # MA data
            text = _web.magnets_setpoint_limits(
                timeout=MASearch._connection_timeout)
            ma_data, ma_param_dict = _util.read_text_data(text)
            # PM data
            text = _web.pulsed_magnets_setpoint_limits(
                timeout=MASearch._connection_timeout)
            pm_data, pm_param_dict = _util.read_text_data(text)

            units = [ma_param_dict['unit'], pm_param_dict['unit']]
            types = ma_param_dict['power_supply_type']
            data = ma_data + pm_data

            MASearch._splims_unit = tuple(units)
            MASearch._splims_labels = tuple(types)
            MASearch._maname_2_splims_dict = {}

            for datum in data:
                maname, *limits = datum
                db = {MASearch._splims_labels[i]: float(limits[i])
                      for i in range(len(MASearch._splims_labels))}
                MASearch._maname_2_splims_dict[maname] = db
        else:
            raise Exception('could not read magnet splims from web server!')

    @staticmethod
    def _reload_maname_2_psnames_dict():
        """Build a dict of tuples with power supplies of each magnet."""
        if _web.server_online():
            text = _web.magnets_excitation_ps_read(
                timeout=MASearch._connection_timeout)
            data, param_dict = _util.read_text_data(text)
            MASearch._maname_2_psnames_dict = {}
            MASearch._maname_2_trim_dict = {}
            MASearch._manames_list = []
            for datum in data:
                magnet, *ps_names = datum
                MASearch._manames_list.append(magnet)
                MASearch._maname_2_psnames_dict[magnet] = tuple(ps_names)
                if 'Fam' not in magnet:
                    famname = _SiriusPVName(magnet)
                    famname = famname.replace(
                        famname.subsection, 'Fam').replace('MA-', 'PS-')
                    if '-Fam:PS-Q' in famname and famname in ps_names:
                        ps_names.remove(famname)
                        maname = famname.replace('PS-', 'MA-')
                        if maname not in MASearch._maname_2_trim_dict:
                            MASearch._maname_2_trim_dict[maname] = \
                                tuple(ps_names)
                        else:
                            MASearch._maname_2_trim_dict[maname] += \
                                tuple(ps_names)
        else:
            raise Exception(
                'could not read magnet-excitation-ps from web server!')

    @staticmethod
    def get_splims_unit():
        """Get unit of SP limits."""
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        return MASearch._splims_unit

    @staticmethod
    def get_splim(maname, label):
        """Return setpoint limits.

        that correspond to given label (either epics' or pcaspy's).
        """
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        if label in MASearch._splims_labels:
            return MASearch._maname_2_splims_dict[maname][label]
        else:
            label = _util.conv_splims_labels(label)
            if label is None:
                return None
            else:
                return MASearch._maname_2_splims_dict[maname][label]

    @staticmethod
    def conv_maname_2_trims(maname):
        """Convert maname to trims."""
        if MASearch._maname_2_trim_dict is None:
            MASearch._reload_maname_2_psnames_dict()
        return MASearch._maname_2_trim_dict.get(maname, None)

    @staticmethod
    def conv_maname_2_magfunc(maname):
        """Return a dict mapping power supplies functions for given magnet."""
        if MASearch._maname_2_psnames_dict is None:
            MASearch._reload_maname_2_psnames_dict()
        ps = MASearch._maname_2_psnames_dict[maname]
        ps_types = tuple(map(PSSearch.conv_psname_2_pstype, ps))
        ma_func = tuple(map(PSSearch.conv_pstype_2_magfunc, ps_types))

        ret = dict()
        for i, psname in enumerate(ps):
            ret[psname] = ma_func[i]

        return ret

    @staticmethod
    def conv_maname_2_splims(maname):
        """Convert maname to splims."""
        if maname is None:
            return None
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        return _copy.deepcopy(MASearch._maname_2_splims_dict[maname])

    @staticmethod
    def conv_maname_2_psnames(maname):
        """Return list of power supplies associated with a given magnet."""
        if MASearch._maname_2_psnames_dict is None:
            MASearch._reload_maname_2_psnames_dict()
        return MASearch._maname_2_psnames_dict[maname]

    @staticmethod
    def get_manames(filters=None, sorting=None):
        """Return a sorted and filtered list of all magnet names.

        This list also includes pulsed magnets (PM).
        """
        if MASearch._manames_list is None:
            MASearch._reload_maname_2_psnames_dict()
        return _Filter.process_filters(MASearch._manames_list,
                                       filters=filters,
                                       sorting=sorting)

    @staticmethod
    def get_pwrsupply_manames(filters=None, sorting=None):
        """Return a sorted and filtered list of all pwrsupply magnet names."""
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        ps_manames_list = list(MASearch._maname_2_splims_dict.keys())
        return _Filter.process_filters(ps_manames_list,
                                       filters=filters,
                                       sorting=sorting)
