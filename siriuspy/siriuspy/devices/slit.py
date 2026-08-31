"""."""

import time as _time

from siriuspy.devices import Device as _Device


class Slit(_Device):
    """."""

    class DEVICES:
        """Device names."""

        H = 'TB-01:DI-SlitH'
        V = 'TB-01:DI-SlitV'
        ALL = (H, V)

    PROPERTIES_DEFAULT = (
        # General commands and monitors
        'Home-Cmd',
        'CoordConvErr-Mon',
        # Global slit parameters
        'Center-RB',
        'Center-SP',
        'Width-RB',
        'Width-SP',
        # Negative edge
        'NegativeEdgePos-RB',
        'NegativeEdgePos-SP',
        'NegativeEdgeCenter-RB',
        'NegativeEdgeCenter-SP',
        'NegativeDoneMov-Mon',
        # Positive edge
        'PositiveEdgePos-RB',
        'PositiveEdgePos-SP',
        'PositiveEdgeCenter-RB',
        'PositiveEdgeCenter-SP',
        'PositiveDoneMov-Mon',
    )

    def __init__(self, devname, props2init='all'):
        """Initialize slit device."""
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        super().__init__(devname, props2init=props2init)

    # ------------------------------------------------------------------
    # General status
    # ------------------------------------------------------------------

    @property
    def is_coordinate_conversion_ok(self):
        """Return whether coordinate conversion is valid."""
        return not bool(self['CoordConvErr-Mon'])

    @property
    def is_negative_edge_moving(self):
        """Return whether the negative edge is moving."""
        return not bool(self['NegativeDoneMov-Mon'])

    @property
    def is_positive_edge_moving(self):
        """Return whether the positive edge is moving."""
        return not bool(self['PositiveDoneMov-Mon'])

    @property
    def is_moving(self):
        """Return whether at least one slit edge is moving."""
        return self.is_negative_edge_moving or self.is_positive_edge_moving

    # ------------------------------------------------------------------
    # Center and width [mm]
    # ------------------------------------------------------------------

    @property
    def center(self):
        """."""
        return self['Center-RB']

    @center.setter
    def center(self, value):
        """."""
        self['Center-SP'] = value

    @property
    def center_setpoint(self):
        """."""
        return self['Center-SP']

    @property
    def width(self):
        """."""
        return self['Width-RB']

    @width.setter
    def width(self, value):
        """."""
        self['Width-SP'] = value

    @property
    def width_setpoint(self):
        """."""
        return self['Width-SP']

    # ------------------------------------------------------------------
    # Edge positions [mm]
    # ------------------------------------------------------------------

    @property
    def negative_edge_position(self):
        """."""
        return self['NegativeEdgePos-RB']

    @negative_edge_position.setter
    def negative_edge_position(self, value):
        """."""
        self['NegativeEdgePos-SP'] = value

    @property
    def negative_edge_position_setpoint(self):
        """."""
        return self['NegativeEdgePos-SP']

    @property
    def positive_edge_position(self):
        """."""
        return self['PositiveEdgePos-RB']

    @positive_edge_position.setter
    def positive_edge_position(self, value):
        """."""
        self['PositiveEdgePos-SP'] = value

    @property
    def positive_edge_position_setpoint(self):
        """."""
        return self['PositiveEdgePos-SP']

    def move_negative_edge(self, value):
        """."""
        self.negative_edge_position = value

    def move_positive_edge(self, value):
        """."""
        self.positive_edge_position = value

    def move_center(self, value):
        """."""
        self.center = value

    def move_width(self, value):
        """."""
        self.width = value

    def move(self, center=None, width=None):
        """Set center and/or width.

        When both values are supplied, center is written before width.
        This method does not wait for completion.
        """
        if center is None and width is None:
            raise ValueError(
                'At least one of center or width must be provided.'
            )

        if center is not None:
            self.center = center

        if width is not None:
            self.width = width

    # ------------------------------------------------------------------
    # Edge center properties [mm]
    # ------------------------------------------------------------------

    @property
    def negative_edge_center(self):
        """."""
        return self['NegativeEdgeCenter-RB']

    @negative_edge_center.setter
    def negative_edge_center(self, value):
        """."""
        self['NegativeEdgeCenter-SP'] = value

    @property
    def positive_edge_center(self):
        """."""
        return self['PositiveEdgeCenter-RB']

    @positive_edge_center.setter
    def positive_edge_center(self, value):
        """."""
        self['PositiveEdgeCenter-SP'] = value

    # ------------------------------------------------------------------
    # Home and motion synchronization
    # ------------------------------------------------------------------

    def cmd_home(self):
        """."""
        self['Home-Cmd'] = 1

    def cmd_go_max_aperture(self):
        """Execute home, assumed to correspond to maximum aperture."""
        self.cmd_home()

    def wait_negative_edge_finish_moving(self, timeout=60):
        """."""
        return self.wait(
            propty='NegativeDoneMov-Mon', value=1, timeout=timeout
        )

    def wait_positive_edge_finish_moving(self, timeout=60):
        """."""
        return self.wait(
            propty='PositiveDoneMov-Mon', value=1, timeout=timeout
        )

    def wait_finish_moving(self, timeout=60):
        """Wait for both slit edges to finish moving."""
        pv_names = ('NegativeDoneMov-Mon', 'PositiveDoneMov-Mon')

        start_time = _time.time()

        for pv_name in pv_names:
            elapsed = _time.time() - start_time
            remaining_timeout = timeout - elapsed

            if remaining_timeout <= 0:
                return False

            completed = self.wait(
                propty=pv_name, value=1, timeout=remaining_timeout
            )

            if not completed:
                return False

        return True

    def move_and_wait(self, center=None, width=None, timeout=60):
        """Set center and/or width and wait for motion completion."""
        self.move(center=center, width=width)
        return self.wait_finish_moving(timeout=timeout)


class SlitH(Slit):
    """Horizontal slit."""

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = self.DEVICES.H

        super().__init__(devname, props2init=props2init)


class SlitV(Slit):
    """Vertical slit."""

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = self.DEVICES.V

        super().__init__(devname, props2init=props2init)
