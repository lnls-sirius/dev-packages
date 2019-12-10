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

from .. import util as _util
from ..search import PSSearch as _PSSearch
from ..thread import DequeThread as _DequeThread
from ..pwrsupply.data import PSData as _PSData
from .pru import PRU as _PRU
from .pru import PRUSim as _PRUSim
from .prucontroller import PRUController as _PRUController
from .fields import Constant as _Constant
from .fields import Setpoint as _Setpoint
from .psmodel import PSModelFactory as _PSModelFactory
from .maepics import SConvEpics as _SConvEpics


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

        # strength name
        self._strenames = self._get_strength_name()

        # create device_name to scan interval dict
        self._create_dev2interval_dict()

        # init mirror variables and last update timestamp dicts
        self._create_dev2mirr_dev2timestamp_dict()

        # create strength conv epics objects
        self._streconvs, self._streconnected = \
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

    def write(self, device_name, field, value):
        """Write to device."""
        if field in {'Energy-SP', 'Kick-SP', 'KL-SP', 'SL-SP'}:
            streconv = self._streconvs[device_name]
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
        for psname in self.psnames:
            strec[psname] = False
            # NOTE: use 'Ref-Mon' proptype for all
            if 'DCLink' not in psname:
                streconvs[psname] = _SConvEpics(psname, 'Ref-Mon')
        return streconvs, strec

    def _update_strengths(self, psname):
        # t0 = _time.time()
        if 'DCLink' in psname:
            return
        streconv = self._streconvs[psname]
        mirror = self._dev2mirror[psname]
        curr0 = mirror[psname + ':Current-SP']
        curr1 = mirror[psname + ':Current-RB']
        curr2 = mirror[psname + ':CurrentRef-Mon']
        curr3 = mirror[psname + ':Current-Mon']
        currs = (curr0, curr1, curr2, curr3)
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
        # t1 = _time.time()
        # print('update_strengths: {:.3f}'.format(1000*(t1-t0)))


class BBBFactory:
    """Build BeagleBones."""

    @staticmethod
    def create(bbbname=None, simulate=False):
        """Return BBB object."""
        # get current timestamp
        timestamp = _time.time()

        # create PRU
        if simulate:
            pru = _PRUSim()
        else:
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

        has_bo_qs = False
        has_ts_cv1 = False

        for psmodel_name in psmodels_dict:

            psmodel = psmodels_dict[psmodel_name]
            devices = devices_dict[psmodel_name]

            if ('BO-02D:PS-QS', 3) in devices:
                has_bo_qs = True
                devices = devices[:2]
            if ('TS-02:PS-CV-0', 11) in devices:
                has_ts_cv1 = True
                devices = [('TB-01:PS-QD1', 1), ('TB-01:PS-QF1', 2), ('TB-02:PS-QD2A', 3),
                           ('TB-02:PS-QF2A', 4), ('TB-02:PS-QD2B', 5), ('TB-02:PS-QF2B', 6),
                           ('TB-03:PS-QD3', 7), ('TB-03:PS-QF3', 8), ('TB-04:PS-QD4', 9), ('TB-04:PS-QF4', 10)]

            # get model database
            database = _PSData(devices[0][0]).propty_database

            # check if IOC is already running
            BBBFactory._check_ioc_online(devices[0][0], database)

            # create pru controller for devices
            freq = freqs_dict[psmodel_name]
            freq = None if freq == 0 else freq
            pru_controller = _PRUController(pru, prucqueue,
                                            psmodel, devices,
                                            processing=False,
                                            scanning=False,
                                            freq=freq)

            # set bootime in epics database
            database['TimestampBoot-Cte']['value'] = timestamp

            # build setpoints
            setpoints = BBBFactory._build_setpoints_dict(devices, database)

            # build fields and functions dicts
            fields, functions = BBBFactory._build_fields_functions_dict(
                dbase, psmodel, setpoints,
                devices, database, pru_controller)

            # build connections and device_ids dicts
            connections, devices_ids = dict(), dict()
            for dev_name, dev_id in devices:
                devices_ids[dev_name] = dev_id
                connections[dev_name] = Connection(dev_id, pru_controller)

            # build controller
            controller = psmodel.controller(
                fields, functions, connections, pru_controller, devices_ids)
            for dev_name, dev_id in devices:
                controllers[dev_name] = controller
                databases[dev_name] = database

        # TODO: clean this work-around!!!
        if has_bo_qs:
            BBBFactory._insert_exception(
                'FBP', [('BO-02D:PS-QS', 3), ],
                pru, prucqueue, timestamp,
                dbase, controllers, databases,
                psmodels_dict, freqs_dict)
        if has_ts_cv1:
            BBBFactory._insert_exception(
                'FBP', [('TS-01:PS-CV-1E2', 11), ('TS-02:PS-CV-0', 12)],
                pru, prucqueue, timestamp,
                dbase, controllers, databases,
                psmodels_dict, freqs_dict)

        return BeagleBone(controllers, databases), dbase

    @staticmethod
    def _insert_exception(
            psmodel_name, devices,
            pru, prucqueue, timestamp,
            dbase, controllers, databases,
            psmodels_dict, freqs_dict):

        psmodel = psmodels_dict[psmodel_name]

        # get model database
        database = _PSData(devices[0][0]).propty_database

        # check if IOC is already running
        BBBFactory._check_ioc_online(devices[0][0], database)

        # create pru controller for devices
        freq = freqs_dict[psmodel_name]
        freq = None if freq == 0 else freq
        pru_controller = _PRUController(pru, prucqueue,
                                        psmodel, devices,
                                        processing=False,
                                        scanning=False,
                                        freq=freq)

        # set bootime in epics database
        database['TimestampBoot-Cte']['value'] = timestamp

        # build setpoints
        setpoints = BBBFactory._build_setpoints_dict(devices, database)

        # build fields and functions dicts
        fields, functions = BBBFactory._build_fields_functions_dict(
            dbase, psmodel, setpoints,
            devices, database, pru_controller)

        # build connections and device_ids dicts
        connections, devices_ids = dict(), dict()
        for dev_name, dev_id in devices:
            devices_ids[dev_name] = dev_id
            connections[dev_name] = Connection(dev_id, pru_controller)

        # build controller
        controller = psmodel.controller(
            fields, functions, connections, pru_controller, devices_ids)
        for dev_name, dev_id in devices:
            controllers[dev_name] = controller
            databases[dev_name] = database

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
            elif _Constant.match(field) and field != 'Version-Cte' and \
                    not field.startswith('Param'):
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

    @staticmethod
    def _check_ioc_online(psname, database):
        propty = next(iter(database))
        pvname = psname + ':' + propty
        running = _util.check_pv_online(
            pvname=pvname, use_prefix=False, timeout=0.5)
        if running:
            raise ValueError('Another IOC is already running !')


class Connection:
    """Object that checks if a device is connected."""

    def __init__(self, device_id, pru_controller):
        """Init."""
        self._device_id = device_id
        self._pru_controller = pru_controller

    def connected(self):
        """Return wether device is connected."""
        return self._pru_controller.check_connected(self._device_id)
