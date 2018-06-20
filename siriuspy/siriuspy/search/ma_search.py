"""Search module."""

import copy as _copy
from siriuspy import util as _util
from siriuspy.namesys import Filter as _Filter
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy import servweb as _web
from .ps_search import PSSearch as _PSSearch
from siriuspy.magnet import util as _mutil


class MASearch:
    """MA and PM Magnet Search class."""

    _psnames_list = None
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
    def get_splims_unit(psmodel):
        """Get unit of SP limits."""
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        if psmodel in ('FBP', 'FAC_DCDC', 'FAP_DCDC', 'FAC_2S_DCDC',
                       'FAC_2P4S_DCDC', 'FAC_2P4S_DCDC'):
            return MASearch._splims_ma_unit
        else:
            raise ValueError('units not def for ' + psmodel)
            # return MASearch._splims_pm_unit

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
        """Convert maname powersupply to its trims."""
        if MASearch._maname_2_trim_dict is None:
            MASearch._reload_maname_2_psnames_dict()
        return MASearch._maname_2_trim_dict.get(maname, None)

    @staticmethod
    def conv_maname_2_magfunc(maname):
        """Return a dict mapping ps to magnet functions for given magnet ps."""
        if MASearch._maname_2_psnames_dict is None:
            MASearch._reload_maname_2_psnames_dict()
        ps = MASearch._maname_2_psnames_dict[maname]
        ps_types = tuple(map(_PSSearch.conv_psname_2_pstype, ps))
        ma_func = tuple(map(_PSSearch.conv_pstype_2_magfunc, ps_types))

        ret = dict()
        for i, psname in enumerate(ps):
            ret[psname] = ma_func[i]

        return ret

    @staticmethod
    def conv_maname_2_splims(maname):
        """Convert maname powersupply to a dict with its setpoint limits."""
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
    def conv_psmaname_2_psnames(maname):
        """Return list of power supplies associated with a given magnet ps."""
        maname = _SiriusPVName(maname)
        ma_class = _mutil.magnet_class(maname)
        if 'dipole' == ma_class:
            if 'SI' == maname.sec:
                return ['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
            elif 'BO' == maname.sec:
                return ['BO-Fam:PS-B-1', 'BO-Fam:PS-B-2']
        elif 'pulsed' == ma_class:
            return [maname.replace(':PM', ':PU')]
        return [maname.replace(':MA', ':PS')]

    @staticmethod
    def conv_psname_2_maname(psname):
        """Return maname for a given psname.

            The maname returned is the name of the magnet or magnet family
        whose magnet instances has/have coil(s) excited by the given power
        supply name. For SI and BO dipoles are exceptions.
        """
        manames = MASearch.get_manames()
        for maname in manames:
            if psname in MASearch._maname_2_psnames_dict[maname]:
                return maname
        return None

    @staticmethod
    def conv_psname_2_maname_pwrsupply(psname):
        """Return power supply maname for a given psname."""
        if MASearch._psnames_list is None:
            MASearch._reload_maname_2_psnames_dict()
        if psname not in MASearch._psnames_list:
            return None
        if 'PS-B1B2' in psname:
            return 'SI-Fam:MA-B1B2'
        elif 'BO-Fam:PS-B' in psname:
            return 'BO-Fam:MA-B'
        else:
            return psname.replace('PS', 'MA').replace('PU', 'PM')

    # @staticmethod
    # def check_maname_ispulsed(maname):
    #     """Return True if psname is a pulsed power supply, False otherwise."""
    #     devname = _SiriusPVName(maname)
    #     if devname.dis == 'PM':
    #         return True
    #     elif devname.dis == 'MA':
    #         return False
    #     else:
    #         raise KeyError('Invalid maname "' + maname + '"!')

    @staticmethod
    def get_maname_2_splims_dict():
        """Return a dictionary of power supply magnet and setpoint limits."""
        if MASearch._maname_2_splims_dict is None:
            MASearch._reload_maname_2_splims_dict()
        return _copy.deepcopy(MASearch._maname_2_splims_dict)

    # --- private methods ---

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
                magnet, *psnames = datum
                MASearch._manames_list.append(magnet)
                MASearch._maname_2_psnames_dict[magnet] = tuple(psnames)
                if 'Fam' not in magnet:
                    famname = _SiriusPVName(magnet)
                    famname = famname.replace(
                        famname.sub, 'Fam').replace('MA-', 'PS-')
                    if '-Fam:PS-Q' in famname and famname in psnames:
                        psnames.remove(famname)
                        maname = famname.replace('PS-', 'MA-')
                        if maname not in MASearch._maname_2_trim_dict:
                            MASearch._maname_2_trim_dict[maname] = \
                                tuple(psnames)
                        else:
                            MASearch._maname_2_trim_dict[maname] += \
                                tuple(psnames)
            MASearch._psnames_list = _PSSearch.get_psnames()
        else:
            raise Exception(
                'could not read magnet-excitation-ps from web server!')
