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

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.thread import DequeThread as _DequeThread
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
from siriuspy.pwrsupply.fields import Constant as _Constant
from siriuspy.pwrsupply.fields import Setpoint as _Setpoint
from siriuspy.pwrsupply.fields import Setpoints as _Setpoints
from siriuspy.pwrsupply.psmodel import PSModelFactory as _PSModelFactory


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

        # create device_name to scan interval dict
        self._create_dev2interval_dict()

        # init mirror variables and last update timestamp dicts
        self._create_dev2mirr_dev2timestamp_dict()

        # TODO: remove this once machine-application PR is merged!
        self.start()

    @property
    def psnames(self):
        """PS names."""
        return list(self._controllers.keys())

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
            self._dev2timestamp[device_name] = now
        else:
            updated = False

        if field is None:
            return self._dev2mirror[device_name], updated
        else:
            return \
                self._dev2mirror[device_name][device_name+':'+field], updated

    def write(self, device_name, field, value):
        """Write to device."""
        self._controllers[device_name].write(device_name, field, value)

    def check_connected(self, device_name):
        """Check wether device is connected."""
        return self._controllers[device_name].check_connected(device_name)

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


class BBBFactory:
    """Build BeagleBones."""

    @staticmethod
    def create(bbbname=None, simulate=False, eth=False):
        """Return BBB object."""
        # get current timestamp
        timestamp = _time.time()

        # create PRU
        if eth:
            pru = _PRU(bbbname=bbbname)
        else:
            pru = _PRUSim() if simulate else _PRU()

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

            # Create pru controller for devices
            freq = freqs_dict[psmodel_name]
            freq = None if freq == 0 else freq
            pru_controller = _PRUController(pru, prucqueue,
                                            psmodel, devices,
                                            processing=False,
                                            scanning=False,
                                            freq=freq)

            # Get model database
            database = _PSData(devices[0][0]).propty_database

            # set bootime in epics database
            database['TimestampBoot-Cte']['value'] = timestamp

            # Build setpoints
            setpoints = BBBFactory._build_setpoints_dict(devices, database)

            # Build fields and functions dicts
            fields, functions = BBBFactory._build_fields_functions_dict(
                dbase, psmodel, setpoints,
                devices, database, pru_controller)

            # Build connections and device_ids dicts
            connections, devices_ids = dict(), dict()
            for dev_name, dev_id in devices:
                devices_ids[dev_name] = dev_id
                connections[dev_name] = Connection(dev_id, pru_controller)

            # Build controller
            controller = psmodel.controller(
                fields, functions, connections, pru_controller, devices_ids)
            for dev_name, dev_id in devices:
                controllers[dev_name] = controller
                databases[dev_name] = database

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
        functions = dict()
        fields = dict()
        for field in database:
            if _Setpoint.match(field):
                functions.update(BBBFactory._get_functions(
                    model, field, devices, setpoints, pru_controller))
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    dbase[pvname] = _deepcopy(database[field])
                    fields[pvname] = setpoints[pvname]
            elif _Constant.match(field) and field != 'Version-Cte':
                for dev_name, dev_id in devices:
                    name = dev_name + ':' + field
                    dbase[name] = _deepcopy(database[field])
                    fields[name] = _Constant(database[field]['value'])
            else:
                for dev_name, dev_id in devices:
                    name = dev_name + ':' + field
                    dbase[name] = _deepcopy(database[field])
                    fields[name] = model.field(
                        dev_id, field, pru_controller)
        return fields, functions

    @staticmethod
    def _get_functions(model, field, devices,
                       setpoints, pru_controller):
        if field in ('CycleType-Sel', 'CycleNrCycles-SP',
                     'CycleFreq-SP', 'CycleAmpl-SP',
                     'CycleOffset-SP', 'CycleAuxParam-SP'):
            # Make one object for all devices (UDC-shared)
            ids, sps = list(), list()
            for dev_name, dev_id in devices:
                pvname = dev_name + ':' + field
                ids.append(dev_id)
                sps.append(setpoints[pvname])
            function = model.function(
                ids, field, pru_controller, _Setpoints(sps))
            return {device[0] + ':' + field: function
                    for device in devices}

        funcs = dict()
        for dev_name, dev_id in devices:
            setpoint = setpoints[dev_name + ':' + field]
            funcs[dev_name + ':' + field] = model.function(
                [dev_id], field, pru_controller, setpoint)
        return funcs


class Connection:
    """Object that checks if a device is connected."""

    def __init__(self, device_id, pru_controller):
        """Init."""
        self._device_id = device_id
        self._pru_controller = pru_controller

    def connected(self):
        """Return wether device is connected."""
        return self._pru_controller.check_connected(self._device_id)
