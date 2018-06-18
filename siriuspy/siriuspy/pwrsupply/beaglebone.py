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

from copy import deepcopy as _deepcopy
# from siriuspy.pwrsupply.beaglebone import _E2SController
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.e2scontroller import \
    PSController as _PSController
from siriuspy.pwrsupply.e2scontroller import \
    StandardPSController as _StdPSController
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.prucontroller import PRUCQueue as _PRUCQueue
from siriuspy.pwrsupply.prucontroller import \
    PRUController as _PRUController
from siriuspy.pwrsupply.fields import Constant as _Constant
from siriuspy.pwrsupply.fields import Setpoint as _Setpoint
from siriuspy.pwrsupply.fields import Setpoints as _Setpoints
from siriuspy.pwrsupply.fields import \
    VariableFactory as _VariableFactory
from siriuspy.pwrsupply.functions import \
    FunctionFactory as _FunctionFactory


class BeagleBone:
    """BeagleBone is a set of PSControllers.

    This class simply redirects read, write connected requests to the
    aproppriate controller.
    """

    def __init__(self, controllers):
        """Init object.

        controllers is a list of PSController
        """
        self._controllers = controllers

    @property
    def psnames(self):
        """PS names."""
        return list(self._controllers.keys())

    def read(self, device_name, field=None):
        """Read from device."""
        if field is None:
            return self._controllers[device_name].read_all_fields(device_name)
        return self._controllers[device_name].read(device_name, field)

    def write(self, device_name, field, value):
        """Write to device."""
        self._controllers[device_name].write(device_name, field, value)

    def check_connected(self, device_name):
        """Check wether device is connected."""
        return self._controllers[device_name].check_connected(device_name)


class BBBFactory:
    """Build BeagleBones."""

    @staticmethod
    def get(bbbname=None, devices=None, simulate=False):
        """Return BBB object."""
        # Create PRU and PRUCQueue
        pru = _PRUSim() if simulate else _PRU()
        prucqueue = _PRUCQueue()
        db = dict()

        # if bbbname == 'BO-01:CO-PSCtrl-1':
        #     devices = (('BO-01U:PS-CH', 1), ('BO-01U:PS-CV', 2))
        # else:
        if bbbname is not None:
            devices = _PSSearch.conv_bbbname_2_bsmps(bbbname)
        elif devices is not None:
            devices = devices
        else:
            raise ValueError

        # Get devices by model
        models = dict()
        for device in devices:
            psname = device[0]
            model = _PSData(psname).psmodel
            if model not in models:
                models[model] = list()
            models[model].append(device)

        # Get controllers
        controllers = {}
        for model, devices in models.items():
            ids = [device[1] for device in devices]
            pru_controller = _PRUController(pru, prucqueue, model, ids)
            database = _PSData(devices[0][0]).propty_database
            setpoints = {}
            fields = {}
            writers = {}
            connections = {}
            devices_ids = {}

            # Build setpoints
            for field in database:
                for device in devices:
                    dev_name = device[0]
                    if _Setpoint.match(field):
                        setpoints[dev_name + ':' + field] = \
                            _Setpoint(field, database[field])

            # Build fields and writers
            for field in database:
                if _Setpoint.match(field):
                    writers.update(BBBFactory._get_writers(
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
                        fields[name] = _VariableFactory.get(
                            model, dev_id, field, pru_controller)

            for dev_name, dev_id in devices:
                devices_ids[dev_name] = dev_id
                connections[dev_name] = Connection(dev_id, pru_controller)

            # Build controllers dict
            print(model)
            if model in ('FBP'):
                controller = _StdPSController(
                    fields, writers, connections, devices_ids, pru_controller)
            elif model in ('FBP_DCLink'):
                controller = _PSController(
                    fields, writers, connections)
            for dev_name, dev_id in devices:
                controllers[dev_name] = controller

        return BeagleBone(controllers), db

    @staticmethod
    def _get_writers(model, field, devices, setpoints, pru_controller):
        if model == 'FBP':
            if field in ('OpMode-Sel', 'CycleType-Sel', 'CycleNrCycles-SP',
                         'CycleFreq-SP', 'CycleAmpl-SP',
                         'CycleOffset-SP', 'CycleAuxParam-SP'):
                # Make one onject for all devices
                ids, sps = list(), list()
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    ids.append(dev_id)
                    sps.append(setpoints[pvname])
                function = _FunctionFactory.get(
                    model, field, ids, pru_controller, _Setpoints(sps))
                return {device[0] + ':' + field: function
                        for device in devices}
        elif model == 'FBP_DCLINK':
            pass

        funcs = dict()
        for dev_name, dev_id in devices:
            setpoint = setpoints[dev_name + ':' + field]
            funcs[dev_name + ':' + field] = _FunctionFactory.get(
                model, field, [dev_id], pru_controller, setpoint)
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
