"""Storage Ring Scrapers."""

from .device import Device as _Device


class _ScraperDev(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        H = 'SI-01SA:DI-ScrapH'
        V = 'SI-01SA:DI-ScrapV'
        ALL = (H, V, )

    _properties = (
        'Home-Cmd', 'ForceComplete-Mon', 'CoordConvErr-Mon',
        'EnblBacklashComp-Sel', 'EnblBacklashComp-Sts'
    )

    def __init__(self, devname, properties=None):
        """."""
        # check if device exists
        if devname not in _ScraperDev.DEVICES.ALL:
            raise NotImplementedError(devname)

        if properties is None:
            properties = _ScraperDev._properties

        super().__init__(devname, properties)

    @property
    def is_force_cmd_complete(self):
        """."""
        return self['ForceComplete-Mon']

    @property
    def is_coordinate_convertion_ok(self):
        """."""
        return self['CoordConvErr-Mon']

    @property
    def is_backlash_compensation_enabled(self):
        """."""
        return self['EnblBacklashComp-Sts']

    def cmd_enable_backlash_compensation(self):
        """."""
        self['EnblBacklashComp-Sel'] = 1

    def cmd_disable_backlash_compensation(self):
        """."""
        self['EnblBacklashComp-Sel'] = 0

    def cmd_go_max_aperture(self):
        """Go to maximum slit aperture."""
        self['Home-Cmd'] = 1


class ScraperH(_ScraperDev):
    """."""

    _properties = (
        'OuterSlitPos-SP', 'OuterSlitPos-RB',
        'InnerSlitPos-SP', 'InnerSlitPos-RB',
        'InnerDoneMov-Mon', 'OuterDoneMov-Mon',
        'OuterSlitInnerLim-SP', 'OuterSlitInnerLim-RB',
        'OuterSlitOuterLim-SP', 'OuterSlitOuterLim-RB',
        'OuterSlitBacklashDist-SP', 'OuterSlitBacklashDist-RB',
        'OuterMotionCtrl-Cte', 'ForceOuterSlitPos-Cmd',
        'InnerSlitInnerLim-SP', 'InnerSlitInnerLim-RB',
        'InnerSlitOuterLim-SP', 'InnerSlitOuterLim-RB',
        'InnerSlitBacklashDist-SP', 'InnerSlitBacklashDist-RB',
        'InnerMotionCtrl-Cte', 'ForceInnerSlitPos-Cmd',
        )

    def __init__(self):
        """."""
        # call base class constructor
        _all_properties = _ScraperDev._properties + ScraperH._properties
        super().__init__(
            devname=_ScraperDev.DEVICES.H, properties=_all_properties)

    @property
    def left_slit_pos(self):
        """Left slit position [mm]."""
        return self['OuterSlitPos-RB']

    @property
    def right_slit_pos(self):
        """Right slit position [mm]."""
        return self['InnerSlitPos-RB']

    @property
    def is_left_slit_moving(self):
        """."""
        return not self['OuterDoneMov-Mon']

    @property
    def is_right_slit_moving(self):
        """."""
        return not self['InnerDoneMov-Mon']

    @property
    def left_slit_limits(self):
        """Limits for left slit.

        Left Slit (x>0)             Right Slit (x<0)
        [Outer, Inner] | (x=0) | [Inner, Outer]
        """
        return [self['OuterSlitOuterLim-RB'], self['OuterSlitInnerLim-RB']]

    @left_slit_limits.setter
    def left_slit_limits(self, limits):
        """Set left slit limits.

        Left Slit (x>0)             Right Slit (x<0)
        [Outer, Inner] | (x=0) | [Inner, Outer]
        """
        self['OuterSlitInnerLim-SP'] = limits[0]
        self['OuterSlitOuterLim-SP'] = limits[1]

    @property
    def right_slit_limits(self):
        """Limits for right slit.

        Left Slit (x>0)             Right Slit (x<0)
        [Outer, Inner] | (x=0) | [Inner, Outer]
        """
        return [self['InnerSlitInnerLim-RB'], self['InnerSlitOuterLim-RB']]

    @right_slit_limits.setter
    def right_slit_limits(self, limits):
        """Set right slit limits.

        Left Slit (x>0)             Right Slit (x<0)
        [Outer, Inner] | (x=0) | [Inner, Outer]
        """
        self['InnerSlitInnerLim-SP'] = limits[0]
        self['InnerSlitOuterLim-SP'] = limits[1]

    @property
    def left_slit_control_prefix(self):
        """."""
        return self['OuterMotionCtrl-Cte']

    @property
    def right_slit_control_prefix(self):
        """."""
        return self['InnerMotionCtrl-Cte']

    def move_left_slit(self, value):
        """Change outer slit to position [mm]."""
        self['OuterSlitPos-SP'] = value

    def move_right_slit(self, value):
        """Change inner slit to position [mm]."""
        self['InnerSlitPos-SP'] = value

    def cmd_force_left_slit(self):
        """Force left slit position."""
        self['ForceOuterSlitPos-Cmd'] = 1

    def cmd_force_right_slit(self):
        """Force right slit position."""
        self['ForceInnerSlitPos-Cmd'] = 1


class ScraperV(_ScraperDev):
    """."""

    _properties = (
        'TopSlitPos-SP', 'TopSlitPos-RB',
        'BottomSlitPos-SP', 'BottomSlitPos-RB',
        'BottomDoneMov-Mon', 'TopDoneMov-Mon',
        'TopSlitInnerLim-SP', 'TopSlitInnerLim-RB',
        'TopSlitOuterLim-SP', 'TopSlitOuterLim-RB',
        'TopMotionCtrl-Cte', 'ForceTopSlitPos-Cmd'
        'BottomSlitInnerLim-SP', 'BottomSlitInnerLim-RB',
        'BottomSlitOuterLim-SP', 'BottomSlitOuterLim-RB',
        'BottomMotionCtrl-Cte', 'ForceBottomSlitPos-Cmd',
        )

    def __init__(self):
        """."""
        # call base class constructor
        _all_properties = _ScraperDev._properties + ScraperV._properties
        super().__init__(
            devname=_ScraperDev.DEVICES.V, properties=_all_properties)

    @property
    def top_slit_pos(self):
        """Top slit position [mm]."""
        return self['TopSlitPos-RB']

    @property
    def bottom_slit_pos(self):
        """Bottom slit position [mm]."""
        return self['BottomSlitPos-RB']

    @property
    def is_top_slit_moving(self):
        """."""
        return not self['TopDoneMov-Mon']

    @property
    def is_bottom_slit_moving(self):
        """."""
        return not self['BottomDoneMov-Mon']

    @property
    def is_force_cmd_complete(self):
        """."""
        return self['ForceComplete-Mon']

    @property
    def is_coordinate_convertion_ok(self):
        """."""
        return self['CoordConvErr-Mon']

    @property
    def top_slit_limits(self):
        """Set top slit limits.

        Top Slit (y>0)
            [Outer,
             Inner]
               ---
              (y=0)
               ---
            [Inner,
             Outer]
        Bottom Slit (y<0)
        """
        return [self['TopSlitOuterLim-RB'], self['TopSlitInnerLim-RB']]

    @top_slit_limits.setter
    def top_slit_limits(self, limits):
        """Set top slit limits.

        Top Slit (y>0)
            [Outer,
             Inner]
               ---
              (y=0)
               ---
            [Inner,
             Outer]
        Bottom Slit (y<0)
        """
        self['TopSlitOuterLim-SP'] = limits[0]
        self['TopSlitInnerLim-SP'] = limits[1]

    @property
    def bottom_slit_limits(self):
        """Set bottom slit limits.

        Top Slit (y>0)
            [Outer,
             Inner]
               ---
              (y=0)
               ---
            [Inner,
             Outer]
        Bottom Slit (y<0)
        """
        return [self['BottomSlitInnerLim-RB'], self['BottomSlitOuterLim-RB']]

    @bottom_slit_limits.setter
    def bottom_slit_limits(self, limits):
        """Set bottom slit limits.

        Top Slit (y>0)
            [Outer,
             Inner]
               ---
              (y=0)
               ---
            [Inner,
             Outer]
        Bottom Slit (y<0)
        """
        self['BottomSlitInnerLim-SP'] = limits[0]
        self['BottomSlitOuterLim-SP'] = limits[1]

    @property
    def bottom_slit_control_prefix(self):
        """."""
        return self['BottomMotionCtrl-Cte']

    @property
    def top_slit_control_prefix(self):
        """."""
        return self['TopMotionCtrl-Cte']

    def move_top_slit(self, value):
        """Change top slit position [mm]."""
        self['TopSlitPos-SP'] = value

    def move_bottom_slit(self, value):
        """Change bottom slit position [mm]."""
        self['BottomSlitPos-SP'] = value

    def cmd_force_top_slit(self):
        """Force top slit position."""
        self['ForceTopSlitPos-Cmd'] = 1

    def cmd_force_bottom_slit(self):
        """Force bottom slit position."""
        self['ForceBottomSlitPos-Cmd'] = 1
