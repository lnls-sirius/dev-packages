"""Search module."""

import copy as _copy
from siriuspy import util as _util
from siriuspy.namesys import Filter as _Filter
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy import servweb as _web
from siriuspy.pwrsupply.siggen import SignalFactory as _SignalFactory
from siriuspy.magnet.excdata import ExcitationData as _ExcitationData


class PSSearch:
    """PS and PU Power Supply Search Class."""

    _pstype_dict = None
    _splims_labels = None
    _splims_ps_unit = None
    _splims_pu_unit = None
    _psnames_list = None
    _bbbnames_list = None
    _pstype_2_psnames_dict = None
    _pstype_2_splims_dict = None
    _pstype_2_excdat_dict = dict()
    _psname_2_psmodel_dict = None
    _psname_2_siggen_dict = None
    # _psname_2_bbbname_dict = None
    # _bbbname_2_psnames_dict = None

    _bbbname_2_bsmps_dict = None
    _bsmps_2_bbbname_dict = None

    @staticmethod
    def get_psnames(filters=None):
        """Return a sorted and filtered list of all power supply names."""
        if PSSearch._pstype_2_psnames_dict is None:
            PSSearch._reload_pstype_2_psnames_dict()
        return sorted(_Filter.process_filters(PSSearch._psnames_list,
                                              filters=filters))

    @staticmethod
    def get_pstype_names():
        """Return sorted list of power supply types."""
        if PSSearch._pstype_dict is None:
            PSSearch._reload_pstype_dict()
        return sorted(set(PSSearch._pstype_dict.keys()))

    @staticmethod
    def get_bbbnames(filters=None):
        """Return a sorted and filtered list of all beaglebone names."""
        if PSSearch._bbbname_2_bsmps_dict is None:
            PSSearch._reload_bbb_2_bsmps_dict()
        # if PSSearch._psname_2_bbbname_dict is None:
        #     PSSearch._reload_bbb_2_psname_dict()
        bbname_list = tuple(PSSearch._bbbname_2_bsmps_dict.keys())
        return sorted(_Filter.process_filters(bbname_list, filters=filters))

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

    # @staticmethod
    # def get_bbbname_dict():
    #     """Return bbbname dictionary.
    #
    #     With key,value pairs of bbbname and corresponding power supplies.
    #     """
    #     if PSSearch._bbbname_2_psnames_dict is None:
    #         PSSearch._reload_bbb_2_psname_dict()
    #     return _copy.deepcopy(PSSearch._bbbname_2_psnames_dict)

    @staticmethod
    def get_bbbname_dict():
        """Return bbbname dictionary.

        With key,value pairs of bbbname and corresponding power supplies.
        """
        if PSSearch._bbbname_2_bsmps_dict is None:
            PSSearch._reload_bbb_2_bsmps_dict()
        return _copy.deepcopy(PSSearch._bbbname_2_bsmps_dict)

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

    # @staticmethod
    # def check_psname_ispulsed(psname):
    #     """Return True if psname is a pulsed power supply, False otherwise."""
    #     spvname = _SiriusPVName(psname)
    #     if spvname.dis == 'PU':
    #         return True
    #     elif spvname.dis == 'PS':
    #         return False
    #     else:
    #         raise KeyError('Invalid psname "' + psname + '"!')

    @staticmethod
    def conv_psname_2_psmodel(psname):
        """Convert psname to psmodel."""
        if PSSearch._psname_2_psmodel_dict is None:
            PSSearch._reload_psname_2_psmodel_dict()
        return PSSearch._psname_2_psmodel_dict[psname]

    @staticmethod
    def conv_psname_2_siggenconf(psname):
        """Convert psname to corresponding SigGenConf object."""
        if PSSearch._psname_2_siggen_dict is None:
            PSSearch._reload_psname_2_siggen_dict()
        return PSSearch._psname_2_siggen_dict[psname]

    # @staticmethod
    # def check_pstype_ispulsed(pstype):
    #     """Return True if pstype is of a pulsed pwrsupply type, False o.w."""
    #     if PSSearch._pstype_2_psnames_dict is None:
    #         PSSearch._reload_pstype_2_psnames_dict()
    #     psnames = PSSearch._pstype_2_psnames_dict[pstype]
    #     for psname in psnames:
    #         if ':PU' in psname:
    #             return True
    #     return False

    # @staticmethod
    # def conv_psname_2_bbbname(psname):
    #     """Given psname return the bbb name."""
    #     if PSSearch._psname_2_bbbname_dict is None:
    #         PSSearch._reload_bbb_2_psname_dict()
    #     return PSSearch._psname_2_bbbname_dict[psname]

    @staticmethod
    def conv_psname_2_bbbname(psname):
        """Given psname return the bbb name."""
        if PSSearch._bsmps_2_bbbname_dict is None:
            PSSearch._reload_bbb_2_bsmps_dict()
        return PSSearch._bsmps_2_bbbname_dict[psname]

    # @staticmethod
    # def conv_bbbname_2_psnames(bbbname):
    #     """Given bbb name return the psnames."""
    #     if PSSearch._bbbname_2_psnames_dict is None:
    #         PSSearch._reload_bbb_2_psname_dict()
    #     return PSSearch._bbbname_2_psnames_dict[bbbname]

    @staticmethod
    def conv_bbbname_2_psnames(bbbname):
        """Given bbb name return the psnames."""
        if PSSearch._bbbname_2_bsmps_dict is None:
            PSSearch._reload_bbb_2_bsmps_dict()
        return PSSearch._bbbname_2_bsmps_dict[bbbname]

    @staticmethod
    def conv_bbbname_2_bsmps(bbbname):
        """Given bbb name return bsmps."""
        if PSSearch._bbbname_2_bsmps_dict is None:
            PSSearch._reload_bbb_2_bsmps_dict()
        return PSSearch._bbbname_2_bsmps_dict[bbbname]

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
    def get_splims_unit(psmodel):
        """Return SP limits unit."""
        if PSSearch._pstype_2_splims_dict is None:
            PSSearch._reload_pstype_2_splims_dict()
        if psmodel in ('FBP', 'FAC', 'FAP', 'FAC_2S', 'FAC_2P4S',
                       'FAC_2P4S_DCDC'):
            return PSSearch._splims_ps_unit
        else:
            raise ValueError(psmodel)

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
            pu_data, _ = _util.read_text_data(_web.pu_psmodels_read())
            data = ps_data + pu_data
            PSSearch._psname_2_psmodel_dict = dict()
            for d in data:
                psname, psmodel = d
                PSSearch._psname_2_psmodel_dict[psname] = psmodel
        else:
            raise Exception('could not read psmodels from web server')

    @staticmethod
    def _reload_psname_2_siggen_dict():
        """Load siggen config by psname to a dict."""
        if _web.server_online():
            text = _web.ps_siggen_configuration_read()
            data, _ = _util.read_text_data(text)
            PSSearch._psname_2_siggen_dict = dict()
            for datum in data:
                psname, *siggen_data = datum
                signal = _SignalFactory.factory(data=siggen_data)
                PSSearch._psname_2_siggen_dict[psname] = signal
        else:
            raise Exception('could not read siggen config from web server')

    @staticmethod
    def _reload_bbb_2_bsmps_dict():
        """Test."""
        data, _ = \
            _util.read_text_data(_web.beaglebone_bsmp_mapping())
        PSSearch._bbbname_2_bsmps_dict = dict()
        PSSearch._bsmps_2_bbbname_dict = dict()
        for line in data:
            bbbname, *bsmps = line
            PSSearch._bbbname_2_bsmps_dict[bbbname] = list()
            for i in range(len(bsmps)//2):
                bsmp_name, bsmp_id = bsmps[2*i+0], int(bsmps[2*i+1])
                bsmp = (bsmp_name, bsmp_id)
                PSSearch._bbbname_2_bsmps_dict[bbbname].append(bsmp)
                PSSearch._bsmps_2_bbbname_dict[bsmp_name] = bbbname

    # @staticmethod
    # def _reload_bbb_2_psname_dict():
    #     """Load psnames mapped to BBB names and vice versa."""
    #     PSSearch._psname_2_bbbname_dict = dict()
    #     PSSearch._bbbname_2_psnames_dict = dict()
    #     data, _ = \
    #         _util.read_text_data(_web.beaglebone_power_supplies_mapping())
    #
    #     PSSearch._bbbnames_list = []
    #     for d in data:
    #         bbbname = d[0]
    #         psnames = d[1:]
    #         PSSearch._bbbnames_list.append(bbbname)
    #         # bbb -> ps
    #         if bbbname in PSSearch._bbbname_2_psnames_dict:
    #             PSSearch._bbbname_2_psnames_dict[bbbname] += psnames
    #         else:
    #             PSSearch._bbbname_2_psnames_dict[bbbname] = psnames
    #         # ps -> bbb
    #         for psname in psnames:
    #             if psname in PSSearch._psname_2_bbbname_dict:
    #                 raise ValueError("Repeated power supply {}".format(psname))
    #             PSSearch._psname_2_bbbname_dict[psname] = bbbname
    #         PSSearch._bbbnames_list = sorted(set(PSSearch._bbbnames_list))
