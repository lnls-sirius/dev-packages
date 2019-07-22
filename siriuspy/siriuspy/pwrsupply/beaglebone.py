"""Beagle Bone implementation module."""
# NOTE on current behaviour of BeagleBone:
#
# 01. While in RmpWfm, MigWfm or SlowRefSync, the PS_I_LOAD variable read from
#     power supplies after setting the last curve point may not be the
#     final value given by PS_REFERENCE. This is due to the fact that the
#     power supply control loop takes some time to converge and the PRU may
#     block serial comm. before it. This is evident in SlowRefSync mode, where
#     reference values may change considerably between two setpoints.
#     (see identical note in PRUController)

# TODO: improve code
#
# 01. try to optimize it. At this point it is taking up 80% of BBB1 CPU time.
#     from which ~20% comes from PRController. I think we could keep some kind
#     of device state mirror in E2SController such that it does not have to
#     invoke PRUController read at every device field update. This mirror state
#     could be updated in one go.

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
from siriuspy.pwrsupply.model_factory import ModelFactory as _ModelFactory


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

        # init mirror variables and last update timestamp dicts
        self._init_mirror_and_timestamp()

    @property
    def psnames(self):
        """PS names."""
        return list(self._controllers.keys())

    def update_interval(self, device_name=None):
        """Update interval, as defined in PRUcontrollers."""
        if device_name is not None:
            pruc = self._controllers[device_name].pru_controller
            f_max = max(pruc.params.FREQ_SCAN, pruc.params.FREQ_RAMP)
        else:
            f_ramp = tuple(c.pru_controller.params.FREQ_RAMP for c in
                           self._controllers.values())
            f_scan = tuple(c.pru_controller.params.FREQ_SCAN for c in
                           self._controllers.values())
            f_max = max(f_ramp + f_scan)
        return 1.0 / f_max

    def read(self, device_name, field=None):
        """Read from device."""
        now = _time.time()
        last = self._timestamps[device_name]
        interval = self.update_interval(device_name)

        # reads, if updating is needed
        if last is None or now - last > interval:
            updated = True
            self._mirror[device_name] = \
                self._controllers[device_name].read_all_fields(device_name)
            self._timestamps[device_name] = now
        else:
            updated = False

        if field is None:
            return self._mirror[device_name], updated
        else:
            return self._mirror[device_name][device_name+':'+field], updated

    def write(self, device_name, field, value):
        """Write to device."""
        self._controllers[device_name].write(device_name, field, value)

    def check_connected(self, device_name):
        """Check wether device is connected."""
        return self._controllers[device_name].check_connected(device_name)

    def database(self, device_name):
        """Device database."""
        return self._databases[device_name]

    def _init_mirror_and_timestamp(self):
        self._timestamps = dict()
        self._mirror = dict()
        for device_name in self._controllers:
            self._timestamps[device_name] = None
            self._mirror[device_name] = dict()


class BBBFactory:
    """Build BeagleBones."""

    @staticmethod
    def create(bbbname=None, simulate=False, eth=False):
        """Return BBB object."""
        # Create PRU
        if eth:
            pru = _PRU(bbbname=bbbname)
        else:
            pru = _PRUSim() if simulate else _PRU()

        # create DequeThread
        prucqueue = _DequeThread()

        db = dict()
        controllers = dict()  # 1 controller per UDC
        databases = dict()

        # bypass SCAN and RAMP frequencies.
        try:
            freqs = _PSSearch.conv_bbbname_2_freqs(bbbname)
        except KeyError:
            freqs = None

        udc_list = _PSSearch.conv_bbbname_2_udc(bbbname)
        for udc in udc_list:

            # UDC-specific frequencies
            try:
                freqs = _PSSearch.conv_bbbname_2_freqs(udc)
            except KeyError:
                pass

            devices = _PSSearch.conv_udc_2_bsmps(udc)

            # Check if there is only one psmodel
            psmodel = BBBFactory.check_ps_models(devices)

            # Get out model object
            model = _ModelFactory.create(psmodel)

            # Create pru controller for devices
            ids = [device[1] for device in devices]
            pru_controller = _PRUController(pru, prucqueue, model, ids,
                                            freqs=freqs)

            # Get model database
            database = _PSData(devices[0][0]).propty_database

            # Build setpoints
            setpoints = BBBFactory._build_setpoints_dict(devices, database)

            # Build fields and functions dicts
            fields, functions = BBBFactory._build_fields_functions_dict(
                db, model, setpoints,
                devices, database, pru_controller)

            # Build connections and device_ids dicts
            connections, devices_ids = dict(), dict()
            for dev_name, dev_id in devices:
                devices_ids[dev_name] = dev_id
                connections[dev_name] = Connection(dev_id, pru_controller)

            # Build controller
            controller = model.controller(
                fields, functions, connections, pru_controller, devices_ids)
            for dev_name, dev_id in devices:
                controllers[dev_name] = controller
                databases[dev_name] = database

        return BeagleBone(controllers, databases), db

    @staticmethod
    def check_ps_models(devices):
        """Check number of ps models.

        Raise exception in case the given devices have more than on psmodel
        type.
        """
        psmodels = {_PSData(psname).psmodel for psname, bsmp_id in devices}
        if len(psmodels) > 1:
            raise ValueError('Too many psmodels')
        return psmodels.pop()

    @staticmethod
    def _build_psmodels_dict(devices):
        # Build psmodels dict with bsmp devices
        psmodels = dict()
        for device in devices:
            psname = device[0]
            psmodel = _PSData(psname).psmodel
            if psmodel not in psmodels:
                psmodels[psmodel] = list()
            psmodels[psmodel].append(device)
        return psmodels

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
    def _build_fields_functions_dict(db, model, setpoints, devices,
                                     database, pru_controller):
        functions = dict()
        fields = dict()
        for field in database:
            if _Setpoint.match(field):
                functions.update(BBBFactory._get_functions(
                    model, field, devices, setpoints, pru_controller))
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    db[pvname] = _deepcopy(database[field])
                    fields[pvname] = setpoints[pvname]
            elif _Constant.match(field) and field != 'Version-Cte':
                for dev_name, dev_id in devices:
                    name = dev_name + ':' + field
                    db[name] = _deepcopy(database[field])
                    fields[name] = _Constant(database[field]['value'])
            else:
                for dev_name, dev_id in devices:
                    name = dev_name + ':' + field
                    db[name] = _deepcopy(database[field])
                    fields[name] = model.field(
                        dev_id, field, pru_controller)
        return fields, functions

    @staticmethod
    def _get_functions(model, field, devices,
                       setpoints, pru_controller):
        # if isinstance(model, (FBPFactory, FACFactory, FAPFactory)):
        if field in ('OpMode-Sel', 'CycleType-Sel', 'CycleNrCycles-SP',
                     'CycleFreq-SP', 'CycleAmpl-SP',
                     'CycleOffset-SP', 'CycleAuxParam-SP'):
            # Make one object for all devices
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
