"""BeagleBone Implementation Module."""
# NOTE on current behaviour of BeagleBone:
#
# 01. While in RmpWfm, MigWfm or SlowRefSync, the PS_I_LOAD variable read from
#     power supplies after setting the last curve point may not be the
#     final value given by PS_REFERENCE. This is due to the fact that the
#     power supply control loop takes some time to converge and the PRU may
#     block serial comm. before it. This is evident in SlowRefSync mode, where
#     reference values may change considerably between two setpoints.
#     (see identical note in PRUController)

import time as _time
from copy import deepcopy as _deepcopy

from ..search import PSSearch as _PSSearch
from ..thread import DequeThread as _DequeThread
from ..devices import StrengthConv as _StrengthConv

from .data import PSData as _PSData
from .pru import PRU as _PRU
from .prucontroller import PRUController as _PRUController
from .pscreaders import Constant as _Constant
from .pscreaders import Setpoint as _Setpoint
from .psmodel import PSModelFactory as _PSModelFactory


class BeagleBone:
    """BeagleBone is a set of PSControllers.

    This class simply redirects read, write connected requests to the
    aproppriate controller.
    """

    def __init__(self, controllers, databases):
        """Init object.

        controllers is a list of PSController
        """
        self._controllers = controllers
        self._databases = databases

        # psnames
        self._psnames = tuple(self._controllers.keys())

        # strength property name
        self._strenames = self._get_strength_name()

        # create device_name to scan interval dict
        self._create_dev2interval_dict()

        # init mirror variables and last update timestamp dicts
        self._create_dev2mirr_dev2timestamp_dict()

        # create strength conv epics objects
        self._streconv, self._streconnected, self._strelims = \
            self._create_streconvs()

    @property
    def psnames(self):
        """PS names."""
        return self._psnames

    def update_interval(self, device_name=None):
        """Update interval, as defined in PRUcontrollers."""
        if device_name is not None:
            return self._dev2interval[device_name]
        intervals = tuple(self._dev2interval.values())
        return min(intervals)

    def read(self, device_name, field=None, force_update=False):
        """Read from device."""
        now = _time.time()
        last = self._dev2timestamp[device_name]

        # NOTE: update frequency with which class updates state mirror of
        # power supply.
        interval = self._dev2interval[device_name]

        # reads, if updating is needed
        if force_update or last is None or now - last > interval:
            updated = True
            self._dev2mirror[device_name] = \
                self._controllers[device_name].read_all_fields(device_name)
            self._update_strengths(device_name)
            self._dev2timestamp[device_name] = now
        else:
            updated = False

        if field is None:
            return self._dev2mirror[device_name], updated
        else:
            pvname = device_name + ':' + field
            return self._dev2mirror[device_name][pvname], updated

    def get_strength_limits(self, device_name):
        """Return strength lower and upper limits."""
        return self._strelims[device_name]

    def write(self, device_name, field, value):
        """Write to device."""
        if field in {'Energy-SP', 'Kick-SP', 'KL-SP', 'SL-SP'}:
            streconv = self._streconv[device_name]
            curr = streconv.conv_strength_2_current(value)
            self._controllers[device_name].write(
                device_name, 'Current-SP', curr)
        else:
            self._controllers[device_name].write(device_name, field, value)

    def check_connected(self, device_name):
        """Check wether device is connected."""
        return self._controllers[device_name].check_connected(device_name)

    def check_connected_strength(self, device_name):
        """Check connection with PVs for strength calc."""
        return self._streconnected[device_name]

    def strength_name(self, device_name):
        """Return strength name."""
        return self._strenames[device_name]

    def strength_limits(self, device_name):
        """Return strength limits."""
        return self._strelims[device_name]

    def database(self, device_name):
        """Device database."""
        return self._databases[device_name]

    def start(self):
        """Start processing and scanning threads in controllers."""
        # turn PRUcontroller processing on.
        for controller in self._controllers.values():
            controller.pru_controller.processing = True
        # turn PRUcontroller scanning on.
        for controller in self._controllers.values():
            controller.pru_controller.scanning = True

    def _get_strength_name(self):
        strenames = dict()
        for psname, dbase in self._databases.items():
            if 'Energy-SP' in dbase:
                strenames[psname] = 'Energy'
            elif 'Kick-SP' in dbase:
                strenames[psname] = 'Kick'
            elif 'KL-SP' in dbase:
                strenames[psname] = 'KL'
            elif 'SL-SP' in dbase:
                strenames[psname] = 'SL'
            else:
                strenames[psname] = None
        return strenames

    def _create_dev2mirr_dev2timestamp_dict(self):
        self._dev2timestamp = dict()
        self._dev2mirror = dict()
        for device_name in self._controllers:
            self._dev2timestamp[device_name] = None
            self._dev2mirror[device_name] = dict()

    def _create_dev2interval_dict(self):
        self._dev2interval = dict()
        for devname, controller in self._controllers.items():
            pruc = controller.pru_controller
            self._dev2interval[devname] = 1.0/pruc.params.FREQ_SCAN

    def _create_streconvs(self):
        streconvs = dict()
        strec = dict()
        strelims = dict()
        for psname in self.psnames:
            if 'DCLink' in psname:
                strec[psname] = True
            else:
                # NOTE: use 'Ref-Mon' proptype for all
                strec[psname] = False
                streconvs[psname] = _StrengthConv(psname, 'Ref-Mon')
                strelims[psname] = [None, None]
        return streconvs, strec, strelims

    def _update_strengths(self, psname):
        # time0 = _time.time()
        if 'DCLink' in psname:
            return
        streconv = self._streconv[psname]
        strelims = self._strelims[psname]
        mirror = self._dev2mirror[psname]
        dbase = self._databases[psname]
        curr0 = mirror[psname + ':Current-SP']
        curr1 = mirror[psname + ':Current-RB']
        curr2 = mirror[psname + ':CurrentRef-Mon']
        curr3 = mirror[psname + ':Current-Mon']
        curr4 = dbase['Current-SP']['lolo']
        curr5 = dbase['Current-SP']['hihi']
        currs = (curr0, curr1, curr2, curr3, curr4, curr5)
        strengths = streconv.conv_current_2_strength(currents=currs)
        if strengths is None or None in strengths:
            self._streconnected[psname] = False
        else:
            self._streconnected[psname] = True
            propname = psname + ':' + self._strenames[psname]
            mirror[propname + '-SP'] = strengths[0]
            mirror[propname + '-RB'] = strengths[1]
            mirror[propname + 'Ref-Mon'] = strengths[2]
            mirror[propname + '-Mon'] = strengths[3]
            # update strength limits
            strelims[0] = strengths[4]
            strelims[1] = strengths[5]
        # time1 = _time.time()
        # print('update_strengths: {:.3f}'.format(1000*(time1-time0)))


class BBBFactory:
    """Build BeagleBones."""

    @staticmethod
    def create(bbbname=None):
        """Return BBB object."""
        # get current timestamp
        timestamp = _time.time()

        # create PRU
        pru = _PRU(bbbname=bbbname)

        # create DequeThread
        prucqueue = _DequeThread()

        # build dicts for grouped udc.
        print('BEAGLEBONE: {}'.format(bbbname))
        udc_list = _PSSearch.conv_bbbname_2_udc(bbbname)
        psmodels_dict, devices_dict, freqs_dict = \
            BBBFactory._build_udcgrouped_dicts(bbbname, udc_list)

        dbase = dict()
        controllers = dict()  # 1 controller per UDC class
        databases = dict()

        for psmodel_name in psmodels_dict:

            psmodel = psmodels_dict[psmodel_name]
            devices = devices_dict[psmodel_name]

            # create pru controller for devices
            freq = freqs_dict[psmodel_name]
            freq = None if freq == 0 else freq
            pru_controller = _PRUController(pru, prucqueue,
                                            psmodel, devices,
                                            processing=False,
                                            scanning=False,
                                            freq=freq,
                                            init=False)

            # init bsmp comunication and class attributes
            pru_controller.bsmp_init_communication()

            psname2dev = dict()
            readers, writers = dict(), dict()

            for device in devices:

                # psname and bsmp device id
                psname, dev_id = device

                # get model database
                database = _PSData(psname).propty_database

                # set bootime in epics database
                database['TimestampBoot-Cte']['value'] = timestamp

                # build setpoints
                setpoints = BBBFactory._build_setpoints_dict(
                    (device, ), database)

                # build readers and writers dicts
                _readers, _writers = BBBFactory._build_fields_functions_dict(
                    dbase, psmodel, setpoints, (device, ), database,
                    pru_controller)
                readers.update(_readers)
                writers.update(_writers)

                # build device_ids dict
                psname2dev[psname] = dev_id

                # add database to dictionary
                databases[psname] = database

            # build controller
            controller = psmodel.controller(
                readers, writers, pru_controller, psname2dev)

            # add controller to dictionary
            for device in devices:
                psname, dev_id = device
                controllers[psname] = controller

        return BeagleBone(controllers, databases), dbase

    @staticmethod
    def _build_udcgrouped_dicts(bbbname, udc_list):
        psmodels_dict = dict()
        devices_dict = dict()
        freqs_dict = dict()
        for udc in udc_list:

            # add devices
            devices = _PSSearch.conv_udc_2_bsmps(udc)
            print('UDC: ', udc, ', DEVICES: ', devices)
            psmodel_name = BBBFactory.check_ps_models(devices)
            if psmodel_name in psmodels_dict:
                devices_dict[psmodel_name].extend(devices)
            else:
                devices_dict[psmodel_name] = devices

            # add psmodel
            psmodel = _PSModelFactory.create(psmodel_name)
            psmodels_dict[psmodel_name] = psmodel

            # add freqs
            try:
                freq = _PSSearch.conv_bbbname_2_freq(udc)
            except KeyError:
                try:
                    freq = _PSSearch.conv_bbbname_2_freq(bbbname)
                except KeyError:
                    freq = 0.0
            if psmodel_name not in freqs_dict:
                freqs_dict[psmodel_name] = freq
            else:
                freqs_dict[psmodel_name] = max(freqs_dict[psmodel_name], freq)
        return psmodels_dict, devices_dict, freqs_dict

    @staticmethod
    def check_ps_models(devices):
        """Check number of ps models.

        Raise exception in case the given devices have more than on psmodel
        type.
        """
        psmodels = {_PSData(psname).psmodel for psname, bsmp_id in devices}
        if len(psmodels) > 1:
            raise ValueError('Different psmodels in the same UDC')
        return psmodels.pop()

    @staticmethod
    def _build_setpoints_dict(devices, database):
        # Build setpoints
        setpoints = {}
        for field in database:
            for device in devices:
                dev_name = device[0]
                if _Setpoint.match(field):
                    setpoints[dev_name + ':' + field] = \
                        _Setpoint(field, database[field])
        return setpoints

    @staticmethod
    def _build_fields_functions_dict(dbase, model, setpoints, devices,
                                     database, pru_controller):
        writers = dict()
        readers = dict()
        for field in database:
            if _Setpoint.match(field):
                writers.update(BBBFactory._get_functions(
                    model, field, devices, setpoints, pru_controller))
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    dbase[pvname] = _deepcopy(database[field])
                    readers[pvname] = setpoints[pvname]
            elif _Constant.match(field) and field != 'Version-Cte' and \
                    not field.startswith('Param'):
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    dbase[pvname] = _deepcopy(database[field])
                    readers[pvname] = _Constant(database[field]['value'])
            else:
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    dbase[pvname] = _deepcopy(database[field])
                    readers[pvname] = model.field(
                        dev_id, field, pru_controller)
        return readers, writers

    @staticmethod
    def _get_functions(model, field, devices,
                       setpoints, pru_controller):
        # NOTE: Each pwrsupply should have all variables independent
        #       in the near future.
        # if field in ('CycleType-Sel', 'CycleNrCycles-SP',
        #              'CycleFreq-SP', 'CycleAmpl-SP',
        #              'CycleOffset-SP', 'CycleAuxParam-SP'):
        #     # Make one object for all devices (UDC-shared)
        #     ids, sps = list(), list()
        #     for dev_name, dev_id in devices:
        #         pvname = dev_name + ':' + field
        #         ids.append(dev_id)
        #         sps.append(setpoints[pvname])
        #     function = model.function(
        #         ids, field, pru_controller, _Setpoints(sps))
        #     return {device[0] + ':' + field: function
        #             for device in devices}
        funcs = dict()
        for dev_name, dev_id in devices:
            setpoint = setpoints[dev_name + ':' + field]
            funcs[dev_name + ':' + field] = model.function(
                [dev_id], field, pru_controller, setpoint)
        return funcs
