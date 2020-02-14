"""Define PS Conv Epics Class."""

from epics import PV as _PV

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.factory import NormalizerFactory as _NormalizerFactory
from siriuspy.namesys import SiriusPVName as _SiriusPVName


class PSEpicsConn:
    """Power Supply Epics Connector."""

    CONNECTION_TIMEOUT = 0.010  # [s]
    PROPNAME = 'Current'
    PROPTYPES = {'-SP', '-RB', 'Ref-Mon', '-Mon'}

    _dips2 = {'BO-Fam:PS-B-1', 'BO-Fam:PS-B-2',
              'SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2'}
    _prefix = _VACA_PREFIX

    def __init__(self, psname, proptype,
                 propname=PROPNAME,
                 connection_timeout=CONNECTION_TIMEOUT):
        """."""
        self._psname = self._check_psname(psname)
        self._connection_timeout = connection_timeout
        self._propname = propname
        self._proptype = self._check_proptype(proptype)
        self._pvs = self._create_pvs()

    @property
    def psname(self):
        """Return psname."""
        return self._psname

    @property
    def proptype(self):
        """Return proptype."""
        return self._proptype

    @property
    def connected(self):
        """Return connected state."""
        for pvobj in self._pvs:
            if not pvobj.connected:
                return False
        return True

    @property
    def value(self):
        """Return value."""
        if self._psname in PSEpicsConn._dips2:
            value1 = self._pvs[0].value
            value2 = self._pvs[1].value
            if None in (value1, value2):
                return None
            # return average
            return (value1 + value2) / 2
        else:
            value1 = self._pvs[0].value
            return value1

    @value.setter
    def value(self, current):
        """Set current."""
        for pvobj in self._pvs:
            pvobj.value = current

    @property
    def limits(self):
        """Return PV limits."""
        limits = (
            self._pvs[0].lower_alarm_limit,
            self._pvs[0].lower_warning_limit,
            self._pvs[0].lower_disp_limit,
            self._pvs[0].upper_disp_limit,
            self._pvs[0].upper_warning_limit,
            self._pvs[0].upper_alarm_limit)
        return limits

    def _check_psname(self, psname):
        psname = _SiriusPVName(psname)
        return psname

    def _check_proptype(self, proptype):
        if proptype not in PSEpicsConn.PROPTYPES:
            raise ValueError('Invalid proptype')
        return proptype

    def _create_pvs(self):

        psname = self._psname
        pvs = list()
        if psname in PSEpicsConn._dips2:
            # dipoles with two power supplies.
            psname = psname.replace('-1', '').replace('-2', '')
            pvname = psname + '-1:' + self._propname + self._proptype
            pvobj = _PV(self._prefix + pvname,
                        connection_timeout=self._connection_timeout)
            pvs.append(pvobj)
            pvname = psname + '-2:' + self._propname + self._proptype
            pvobj = _PV(self._prefix + pvname,
                        connection_timeout=self._connection_timeout)
            pvs.append(pvobj)
        else:
            pvname = psname + ':' + self._propname + self._proptype
            pvobj = _PV(self._prefix + pvname,
                        connection_timeout=self._connection_timeout)
            pvs.append(pvobj)
        return pvs


class PUEpicsConn(PSEpicsConn):
    """Pulsed Power Supply Epics Connector."""

    CONNECTION_TIMEOUT = 0.010  # [s]
    PROPNAME = 'Voltage'

    def __init__(self, psname, proptype,
                 propname=PROPNAME,
                 connection_timeout=CONNECTION_TIMEOUT):
        """."""
        super().__init__(
            psname, proptype,
            PUEpicsConn.PROPNAME, connection_timeout)


class SConvEpics:
    """Strength Converter."""

    def __init__(self, psname, proptype,
                 connection_timeout=PSEpicsConn.CONNECTION_TIMEOUT):
        """."""
        self._psname = _SiriusPVName(psname)
        self._norm_mag = self._create_normalizer()
        self._conn_dip, self._conn_fam = \
            self._create_connectors(proptype, connection_timeout)

    @property
    def psname(self):
        """Return psname."""
        return self._psname

    @property
    def connected(self):
        """Return connected state."""
        if self._conn_dip:
            if not self._conn_dip.connected:
                return False
        if self._conn_fam:
            if not self._conn_fam.connected:
                return False
        return True

    @property
    def dipole_strength(self):
        """Return dipole strength."""
        if self._conn_dip:
            return self._conn_dip.value
        return None

    @property
    def family_strength(self):
        """Return family strength."""
        if self._conn_fam:
            return self._conn_fam.value
        return None

    def conv_current_2_strength(self, currents,
                                strengths_dipole=None,
                                strengths_family=None):
        """Convert currents to strengths."""
        norm = self._norm_mag
        kwargs = self._get_kwargs(strengths_dipole, strengths_family)
        if kwargs is None:
            return None
        strengths = \
            norm.conv_current_2_strength(currents=currents, **kwargs)
        return strengths

    def conv_strength_2_current(self, strengths,
                                strengths_dipole=None,
                                strengths_family=None):
        """Convert strengths to currents."""
        norm = self._norm_mag
        kwargs = self._get_kwargs(strengths_dipole, strengths_family)
        if kwargs is None:
            return None
        currents = \
            norm.conv_strength_2_current(strengths=strengths, **kwargs)
        return currents

    def _create_normalizer(self):
        if self._psname.sec == 'TB' and self._psname.dev == 'B':
            norm_mag = _NormalizerFactory.create('TB-Fam:MA-B')
        elif self._psname.sec == 'BO' and self._psname.dev == 'B':
            norm_mag = _NormalizerFactory.create('BO-Fam:MA-B')
        elif self._psname.sec == 'TS' and self._psname.dev == 'B':
            norm_mag = _NormalizerFactory.create('TS-Fam:MA-B')
        elif self._psname.sec == 'SI' and self._psname.dev == 'B1B2':
            norm_mag = _NormalizerFactory.create('SI-Fam:MA-B1B2')
        else:
            maname = self._psname.replace(':PS', ':MA').replace(':PU', ':PM')
            norm_mag = _NormalizerFactory.create(maname)
        return norm_mag

    @staticmethod
    def _is_trim(psname):
        check = (psname.sec == 'SI')
        check &= (psname.sub != 'Fam')
        check &= 'QS' not in psname.dev
        check &= 'Q' in psname.dev
        return check

    def _create_connectors(self, proptype, connection_timeout):
        conn_dip, conn_fam = None, None
        sub, dev = self._psname.sub, self._psname.dev
        if dev in {'B', 'B1B2'}:
            # dipoles need no connectors
            pass
        elif self._is_trim(self._psname):
            # trims need dipole and family connectors
            conn_dip = PSEpicsConn(
                'SI-Fam:PS-B1B2-1', proptype, 'Energy', connection_timeout)
            psname = self._psname.replace(sub, 'Fam')
            conn_fam = PSEpicsConn(psname, proptype, 'KL', connection_timeout)
        elif self._psname.startswith('LI'):
            conn_dip = PSEpicsConn(
                'TB-Fam:PS-B', proptype, 'Energy', connection_timeout)
        elif self._psname.startswith('TB'):
            # all TB ps other than dipoles need dipole connectors
            conn_dip = PSEpicsConn(
                'TB-Fam:PS-B', proptype, 'Energy', connection_timeout)
        elif self._psname.startswith('BO'):
            if dev == 'InjKckr':
                # BO injection kicker uses TB dipole normalizer
                conn_dip = PSEpicsConn(
                    'TB-Fam:PS-B', proptype, 'Energy', connection_timeout)
            elif dev == 'EjeKckr':
                # BO ejection kicker uses TS dipole normalizer
                conn_dip = PSEpicsConn(
                    'TS-Fam:PS-B', proptype, 'Energy', connection_timeout)
            else:
                # other BO ps use BO dipoles as normalizer
                conn_dip = PSEpicsConn(
                    'BO-Fam:PS-B-1', proptype, 'Energy', connection_timeout)
        elif self._psname.startswith('TS'):
            # all TS ps use TS dipole
            conn_dip = PSEpicsConn(
                'TS-Fam:PS-B', proptype, 'Energy', connection_timeout)
        elif self._psname.startswith('SI'):
            if dev in {'InjDpKckr', 'InjNLKckr'}:
                # SI injection ps use TS dipole
                conn_dip = PSEpicsConn(
                    'TS-Fam:PS-B', proptype, 'Energy', connection_timeout)
            else:
                # other SI ps use SI dipole
                conn_dip = PSEpicsConn(
                    'SI-Fam:PS-B1B2-1', proptype, 'Energy', connection_timeout)
        return conn_dip, conn_fam

    def _get_kwargs(self,
                    strengths_dipole=None,
                    strengths_family=None):
        if not self._conn_dip:
            # is a dipole
            kwargs = dict()
            return kwargs
        if not self._conn_fam:
            # is not a trim
            if strengths_dipole is None:
                strengths_dipole = self._conn_dip.value
                if strengths_dipole is None:
                    return None
            kwargs = {'strengths_dipole': strengths_dipole}
            return kwargs
        # is a trim
        if strengths_dipole is None:
            strengths_dipole = self._conn_dip.value
            if strengths_dipole is None:
                return None
        if strengths_family is None:
            strengths_family = self._conn_fam.value
            if strengths_family is None:
                return None
        kwargs = {
            'strengths_dipole': strengths_dipole,
            'strengths_family': strengths_family}
        return kwargs
