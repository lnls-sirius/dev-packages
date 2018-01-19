"""Search module."""
import copy as _copy

from siriuspy import util as _util
from siriuspy.namesys import Filter as _Filter
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy import servweb as _web
from siriuspy.magnet.excdata import ExcitationData as _ExcitationData


class PSSearch:
    """PS and PU Power Supply Search Class."""

    _pstype_dict = None
    _splims_labels = None
    _splims_ps_unit = None
    _splims_pu_unit = None
    _psnames_list = None
    _pstype_2_psnames_dict = None
    _pstype_2_splims_dict = None
    _pstype_2_excdat_dict = dict()
    _psname_2_psmodel_dict = None

    @staticmethod
    def get_psnames(filters=None):
        """Return a sorted and filtered list of all power supply names."""
        if PSSearch._pstype_2_psnames_dict is None:
            PSSearch._reload_pstype_2_psnames_dict()
        return _Filter.process_filters(PSSearch._psnames_list, filters=filters)

    @staticmethod
    def get_pstype_names():
        """Return sorted list of power supply types."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        return sorted(set(PSSearch._pstype_dict.keys()))

    @staticmethod
    def get_splims(pstype, label):
        """Return setpoint limit corresponding to given label.

        The label can be either epics' or pcaspy's.
        """
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        if label in PSSearch._splims_labels:
            return PSSearch._pstype_2_splims_dict[pstype][label]
        else:
            label = _util.conv_splims_labels(label)
            return PSSearch._pstype_2_splims_dict[pstype][label]

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
    def get_polarities():
        """Return sorted list of power supply polarities."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        p = [datum[0] for datum in PSSearch._pstype_dict.values()]
        return sorted(set(p))

    @staticmethod
    def conv_psname_2_pstype(psname):
        """Return the power supply type of a given power supply name."""
        if PSSearch._pstype_2_psnames_dict is None:
            PSSearch._reload_pstype_2_psnames_dict()
        for pstype, psnames in PSSearch._pstype_2_psnames_dict.items():
            if psname in psnames:
                return pstype
        raise KeyError('Invalid psname "' + psname + '"!')

    @staticmethod
    def conv_pstype_2_polarity(pstype):
        """Return polarity of a given power supply type."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        return PSSearch._pstype_dict[pstype][0]

    @staticmethod
    def conv_pstype_2_magfunc(pstype):
        """Return magnetic function of a given power supply type."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        for key, value in PSSearch._pstype_dict.items():
            if key == pstype:
                return value[1]
        raise KeyError('Invalid pstype "'+pstype+'"!')

    @staticmethod
    def conv_pstype_2_splims(pstype):
        """Convert pstype to splims."""
        if pstype is None:
            return None
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return _copy.deepcopy(PSSearch._pstype_2_splims_dict[pstype])

    @staticmethod
    def conv_psname_2_excdata(psname):
        """Convert psname to excdata."""
        pstype = PSSearch.conv_psname_2_pstype(psname)
        if pstype not in PSSearch._pstype_2_excdat_dict:
            PSSearch._reload_pstype_2_excdat_dict(pstype)

        return PSSearch._pstype_2_excdat_dict[pstype]

    @staticmethod
    def check_psname_ispulsed(psname):
        """Return True if psname is a pulsed power supply, False otherwise."""
        spvname = _SiriusPVName(psname)
        if spvname.dis == 'PU':
            return True
        elif spvname.dis == 'PS':
            return False
        else:
            raise KeyError('Invalid psname "' + psname + '"!')

    @staticmethod
    def conv_psname_2_psmodel(psname):
        """Conver psname to psmodel."""
        if PSSearch._psname_2_psmodel_dict is None:
            PSSearch._reload_psname_2_psmodel_dict()
        return PSSearch._psname_2_psmodel_dict[psname]

    @staticmethod
    def check_pstype_ispulsed(pstype):
        """Return True if pstype is of a pulsed pwrsupply type, False o.w."""
        if PSSearch._pstype_2_psnames_dict is None:
            PSSearch._reload_pstype_2_psnames_dict()
        psnames = PSSearch._pstype_2_psnames_dict[pstype]
        for psname in psnames:
            if ':PU' in psname:
                return True
        return False

    @staticmethod
    def get_pstype_2_psnames_dict():
        """Return dictionary of power supply type and power supply names."""
        if PSSearch._pstype_2_psnames_dict is None:
            PSSearch._reload_pstype_2_psnames_dict()
        return _copy.deepcopy(PSSearch._pstype_2_psnames_dict)

    @staticmethod
    def get_pstype_2_splims_dict():
        """Return a dictionary of power supply type and setpoint limits."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return _copy.deepcopy(PSSearch._pstype_2_splims_dict)

    @staticmethod
    def get_splims_unit(ispulsed):
        """Return SP limits unit."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        if ispulsed is True:
            return PSSearch._splims_pu_unit
        elif ispulsed is False:
            return PSSearch._splims_ps_unit
        else:
            raise ValueError

    @staticmethod
    def get_splims_labels():
        """Return labels in SP limits dictionary."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        return PSSearch._splims_labels

    # --- private methods ---

    @staticmethod
    def _reload_pstype_dict():
        """Reload power supply type dictionary from web server."""
        if _web.server_online():
            text = _web.ps_pstypes_names_read()
            data, params_dict = _util.read_text_data(text)
            PSSearch._pstype_dict = {}
            for datum in data:
                name, polarity, magfunc = datum[0], datum[1], datum[2]
                PSSearch._pstype_dict[name] = (polarity, magfunc)
        else:
            raise Exception('could not read pstypes from web server!')

    @staticmethod
    def _reload_pstype_2_psnames_dict():
        """Reload power supply type to power supply names dictionary."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        pstypes = sorted(set(PSSearch._pstype_dict.keys()))
        PSSearch._pstype_2_psnames_dict = {}
        PSSearch._psnames_list = []
        for pstype in pstypes:
            text = _web.ps_pstype_data_read(pstype + '.txt')
            data, param_dict = _util.read_text_data(text)
            psnames = [_SiriusPVName(datum[0]) for datum in data]
            PSSearch._pstype_2_psnames_dict[pstype] = psnames
            PSSearch._psnames_list += psnames
        PSSearch._psnames_list = sorted(PSSearch._psnames_list)

    @staticmethod
    def _reload_pstype_2_splims_dict():
        """Reload pstype to splims dictionary."""
        # ps data
        text = _web.ps_pstype_setpoint_limits()
        ps_data, ps_param_dict = _util.read_text_data(text)
        # pu data
        text = _web.pu_pstype_setpoint_limits()
        pu_data, pu_param_dict = _util.read_text_data(text)

        # checks consistency between PS and PU static tables.
        # this should be implemented elsewhere, not in PSSearch!
        if sorted(ps_param_dict['power_supply_type']) != \
                sorted(pu_param_dict['power_supply_type']):
            raise ValueError(('Inconsistent limit labels between PS '
                              'and PU static tables!'))

        PSSearch._splims_ps_unit = ps_param_dict['unit']
        PSSearch._splims_pu_unit = pu_param_dict['unit']
        PSSearch._splims_labels = ps_param_dict['power_supply_type']

        PSSearch._pstype_2_splims_dict = {}
        data = ps_data + pu_data
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
    def _reload_psname_2_psmodel_dict():
        """Load psmodels by psname to a dict."""
        if _web.server_online():
            ps_data, _ = _util.read_text_data(_web.ps_psmodels_read())
            pu_data, _ = _util.read_text_data(_web.ps_pumodels_read())
            data = ps_data + pu_data
            PSSearch._psname_2_psmodel_dict = dict()
            for d in data:
                psname, psmodel = d
                PSSearch._psname_2_psmodel_dict[psname] = psmodel
        else:
            raise Exception('could not read psmodels from web server')


class MASearch:
    """MA and PM Magnet Search class."""

    _manames_list = None
    _maname_2_splims_dict = None  # magnets-stpoint-limits file
    _maname_2_psnames_dict = None  # magnet-excitation-ps file
    _maname_2_trim_dict = None
    _splims_labels = None
    _splims_unit = None

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

    @staticmethod
    def get_splims_unit(ispulsed):
        """Get unit of SP limits."""
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        if ispulsed:
            return MASearch._splims_pm_unit
        else:
            return MASearch._splims_ma_unit

    @staticmethod
    def get_splims(maname, label):
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
    def check_maname_ispulsed(maname):
        """Return True if psname is a pulsed power supply, False otherwise."""
        devname = _SiriusPVName(maname)
        if devname.dis == 'PM':
            return True
        elif devname.dis == 'MA':
            return False
        else:
            raise KeyError('Invalid maname "' + maname + '"!')

    @staticmethod
    def get_maname_2_splims_dict():
        """Return a dictionary of power supply magnet and setpoint limits."""
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        return _copy.deepcopy(MASearch._maname_2_splims_dict)

    # Private methods
    @staticmethod
    def _reload_maname_2_splims_dict():
        """Build dict with limits for each magnet."""
        if _web.server_online():
            # MA data
            text = _web.magnets_setpoint_limits()
            ma_data, ma_param_dict = _util.read_text_data(text)
            # PM data
            text = _web.pulsed_magnets_setpoint_limits()
            pm_data, pm_param_dict = _util.read_text_data(text)

            # units = [ma_param_dict['unit'], pm_param_dict['unit']]
            types = ma_param_dict['power_supply_type']
            data = ma_data + pm_data

            # MASearch._splims_unit = tuple(units)
            MASearch._splims_ma_unit = ma_param_dict['unit']
            MASearch._splims_pm_unit = pm_param_dict['unit']
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
            text = _web.magnets_excitation_ps_read()
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
                        famname.sub, 'Fam').replace('MA-', 'PS-')
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
