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
import re as _re
from copy import deepcopy as _deepcopy

from ..search import PSSearch as _PSSearch
from ..thread import DequeThread as _DequeThread
from ..devices import StrengthConv as _StrengthConv

from .csdev import get_ps_propty_database as _get_ps_propty_database
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

        Parameters:
        controllers : list of PSController objectsused to communicate with
                      BSMP devices.
        databases   : corresponding controllers databases.

        """
        # ps controllers.
        self._controllers = controllers

        # ps cpntrollers databases
        self._databases = databases

        # psnames
        self._psnames = tuple(self._controllers.keys())

        # strength property names
        self._strenames = self._get_strength_names()

        # create devname to scan interval dict
        self._create_dev2interval_dict()

        # init mirror variables and last update timestamp dicts
        self._create_dev2mirr_dev2timestamp_dict()

        # create strength conv epics objects
        self._streconv, self._streconnected, self._strelims = \
            self._create_streconvs()

        # initialized state
        self._initialized = False

    @property
    def controllers(self):
        """Return beaglebone power supply controllers."""
        return self._controllers

    @property
    def psnames(self):
        """PS names."""
        return self._psnames

    def update_interval(self, devname=None):
        """Update interval, as defined in PRUcontrollers."""
        if devname is not None:
            return self._dev2interval[devname]
        intervals = tuple(self._dev2interval.values())
        return min(intervals)

    def read(self, devname, field=None, force_update=False):
        """Read from device."""
        # if not initialized, return None
        if not self._initialized:
            return None, False

        now = _time.time()
        last = self._dev2timestamp[devname]

        # NOTE: update frequency with which class updates state mirror of
        # power supply.
        interval = self._dev2interval[devname]

        # reads, if updating is needed
        if force_update or last is None or now - last > interval:
            updated = True
            self._dev2mirror[devname] = \
                self._controllers[devname].read_all_fields(devname)
            self._update_strengths(devname)
            self._dev2timestamp[devname] = now
        else:
            updated = False

        if field is None:
            return self._dev2mirror[devname], updated
        else:
            pvname = devname + ':' + field
            return self._dev2mirror[devname][pvname], updated

    def write(self, devname, field, value):
        """Write value to a device field.

        Return pvname-value dictionary of priority PVs.
        """
        # if not initialized, return None
        if not self._initialized:
            return None

        if field in {'Energy-SP', 'Kick-SP', 'KL-SP', 'SL-SP'}:
            streconv = self._streconv[devname]
            curr = streconv.conv_strength_2_current(value)
            priority_pvs = self._controllers[devname].write(
                devname, 'Current-SP', curr)
        else:
            priority_pvs = self._controllers[devname].write(
                devname, field, value)
        return priority_pvs

    def get_strength_limits(self, devname):
        """Return strength lower and upper limits."""
        return self._strelims[devname]

    def check_connected(self, devname):
        """Check wether device is connected."""
        return self._controllers[devname].check_connected(devname)

    def check_connected_strength(self, devname):
        """Check connection with PVs for strength calc."""
        return self._streconnected[devname]

    def strength_name(self, devname):
        """Return strength name."""
        return self._strenames[devname]

    def strength_limits(self, devname):
        """Return strength limits."""
        return self._strelims[devname]

    def database(self, devname):
        """Return device database."""
        return self._databases[devname]

    def init(self):
        """Initialize controllers."""
        # return  # allow for IOC initialization without HW comm.

        # initialize controller communication and setpoint fields
        pruc_initialized = set()
        psc_initialized = set()
        for controller in self._controllers.values():
            pruc = controller.pru_controller
            if pruc not in pruc_initialized:
                pruc.bsmp_init_communication()
                pruc.processing = True
                pruc.scanning = True
                pruc_initialized.add(pruc)
            if controller not in psc_initialized:
                controller.init_setpoints()
                psc_initialized.add(controller)
        self._initialized = True

    # --- private methods ---

    def _get_strength_names(self):
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
        for devname in self._controllers:
            self._dev2timestamp[devname] = None
            self._dev2mirror[devname] = dict()

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
        # t0_ = _time.time()
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
        # t1_ = _time.time()
        # print('update_strengths: {:.3f}'.format(1000*(t1_-t0_)))


class BBBFactory:
    """BeagleBone factory."""

    # regexp of constant PVs whose initializations require bsmp communications.
    _regexp_constant_bsmp_init = _re.compile('^(Param|Version).*-Cte$')

    @staticmethod
    def create(bbbname=None):
        """Return BBB object."""
        # create timestamp used in all TimestampBoot-Cte PVs
        timestamp = _time.time()

        # create PRU used for low-level communication
        pru = _PRU(bbbname=bbbname)

        # create DequeThread that queue all serial operations
        prucqueue = _DequeThread()

        # build dicts for grouped udc.
        psmodels, devices, freqs = \
            BBBFactory._build_udcgrouped(bbbname)

        # power supply controllers and databases
        # dbase: a pvname-epicsdbase dictionary containing all
        # beaglebone PVs. the epics server database is initialized
        # using this dictionary.
        controllers, databases, dbase = \
            BBBFactory._build_controllers(
                timestamp, pru, prucqueue, psmodels, devices, freqs)

        return BeagleBone(controllers, databases), dbase

    # --- private methods ---

    @staticmethod
    def _build_controllers(
            timestamp, pru, prucqueue, psmodels, devices, freqs):

        # dbase is a pvname to epics dbase dictionary will all PVs
        dbase = dict()
        controllers = dict()  # one controller per psmodel
        databases = dict()  # controllers databases

        for psmodel_name, psmodel in psmodels.items():

            # devices of that ps model
            devs = devices[psmodel_name]

            # create pru controller for devices
            freq = freqs[psmodel_name]
            freq = None if freq == 0 else freq
            pru_controller = _PRUController(pru, prucqueue,
                                            psmodel, devs,
                                            processing=False,
                                            scanning=False,
                                            freq=freq,
                                            init=False)

            devname2devid = dict()
            readers, writers = dict(), dict()

            for device in devs:

                # psname and bsmp device id
                psname, devid = device

                # get model database
                pstype = _PSSearch.conv_psname_2_pstype(psname)
                database = _get_ps_propty_database(psmodel_name, pstype)

                # build setpoints
                setpoints = BBBFactory._build_setpoints(
                    (device, ), database)

                # build readers and writers and add them to dicts
                _readers, _writers = BBBFactory._build_readers_writers(
                    timestamp, dbase, psmodel, setpoints, (device, ), database,
                    pru_controller)
                _ = readers.update(_readers), writers.update(_writers)

                # build device_ids dict
                devname2devid[psname] = devid

                # add database to dictionary
                databases[psname] = database

            # build controller
            controller = psmodel.controller(
                readers, writers, pru_controller, devname2devid)

            # add controller to dictionary
            for device in devs:
                psname, devid = device
                controllers[psname] = controller

        return controllers, databases, dbase

    @staticmethod
    def _build_udcgrouped(bbbname):

        # get names of all udcs under a beaglebone
        udcs = _PSSearch.conv_bbbname_2_udc(bbbname)

        psmodels, devices, freqs = dict(), dict(), dict()
        for udc in udcs:

            # add udc devices
            devs = _PSSearch.conv_udc_2_bsmps(udc)
            print('UDC: ', udc, ', DEVICES: ', devs)
            psmodel_name = BBBFactory._check_psmodels(devs)
            if psmodel_name in psmodels:
                devices[psmodel_name].extend(devs)
            else:
                devices[psmodel_name] = devs

            # add udc psmodel
            psmodel = _PSModelFactory.create(psmodel_name)
            psmodels[psmodel_name] = psmodel

            # add udc/bbb freqs
            try:
                freq = _PSSearch.conv_bbbname_2_freq(udc)
            except KeyError:
                try:
                    freq = _PSSearch.conv_bbbname_2_freq(bbbname)
                except KeyError:
                    freq = 0.0
            if psmodel_name not in freqs:
                freqs[psmodel_name] = freq
            else:
                freqs[psmodel_name] = max(freqs[psmodel_name], freq)

        return psmodels, devices, freqs

    @staticmethod
    def _build_setpoints(devices, database):
        # Build pvname-setpoints dictionary
        setpoints = dict()
        for field in database:
            for device in devices:
                devname = device[0]
                if _Setpoint.match(field):
                    setpoints[devname + ':' + field] = \
                        _Setpoint(field, database[field])
        return setpoints

    @staticmethod
    def _build_readers_writers(
            timestamp, dbase, model, setpoints, devices, database,
            pru_controller):

        readers, writers = dict(), dict()

        for field in database:
            if _Setpoint.match(field):
                # writers for setpoint field
                field_writers = \
                    BBBFactory._get_writers(
                        model, field, devices, setpoints, pru_controller)
                writers.update(field_writers)
                # corresponding readers
                for devname, devid in devices:
                    pvname = devname + ':' + field
                    dbase[pvname] = _deepcopy(database[field])
                    readers[pvname] = setpoints[pvname]
            elif _Constant.match(field) and \
                    not BBBFactory._regexp_constant_bsmp_init.match(field):
                # readers for const fields whose initializations
                # do not require bsmp communication
                for devname, devid in devices:
                    if field == 'TimestampBoot-Cte':
                        # update bootime in epics database with timestamp
                        database[field]['value'] = timestamp
                    pvname = devname + ':' + field
                    readers[pvname] = _Constant(database[field]['value'])
                    dbase[pvname] = _deepcopy(database[field])
            else:
                # readers for other fields
                for devname, devid in devices:
                    pvname = devname + ':' + field
                    dbase[pvname] = _deepcopy(database[field])
                    readers[pvname] = model.field(
                        devid, field, pru_controller)
        return readers, writers

    @staticmethod
    def _check_psmodels(devices):
        """Check number of ps models.

        Raise exception in case the given devices have more than on psmodel
        type.
        """
        name2model = _PSSearch.conv_psname_2_psmodel
        psmodels = {name2model(psname) for psname, bsmp_id in devices}
        if len(psmodels) > 1:
            raise ValueError('Different psmodels in the same UDC')
        return psmodels.pop()

    @staticmethod
    def _get_writers(
            model, field, devices, setpoints, pru_controller):
        # NOTE: Each pwrsupply should have all variables independent
        #       in the near future.
        # if field in ('CycleType-Sel', 'CycleNrCycles-SP',
        #              'CycleFreq-SP', 'CycleAmpl-SP',
        #              'CycleOffset-SP', 'CycleAuxParam-SP'):
        #     # Make one object for all devices (UDC-shared)
        #     ids, sps = list(), list()
        #     for devname, devid in devices:
        #         pvname = devname + ':' + field
        #         ids.append(devid)
        #         sps.append(setpoints[pvname])
        #     function = model.function(
        #         ids, field, pru_controller, _Setpoints(sps))
        #     return {device[0] + ':' + field: function
        #             for device in devices}
        writers = dict()
        for devname, devid in devices:
            setpoint = setpoints[devname + ':' + field]
            writers[devname + ':' + field] = model.function(
                [devid], field, pru_controller, setpoint)
        return writers
