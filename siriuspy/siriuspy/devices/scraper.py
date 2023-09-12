"""Storage Ring Scrapers."""

from .device import Device as _Device
import time as _time


class _ScraperDev(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        H = 'SI-01SA:DI-ScrapH'
        V = 'SI-01SA:DI-ScrapV'
        ALL = (H, V)

    PROPERTIES_DEFAULT = (
        'Home-Cmd', 'ForceComplete-Mon', 'CoordConvErr-Mon',
        'EnblBacklashComp-Sel', 'EnblBacklashComp-Sts'
        )

    def __init__(self, devname, props2init='all'):
        """."""
        # check if device exists
        if devname not in _ScraperDev.DEVICES.ALL:
            raise NotImplementedError(devname)

        super().__init__(devname, props2init=props2init)

    @property
    def is_force_cmd_complete(self):
        """."""
        return self['ForceComplete-Mon']

    @property
    def is_coordinate_convertion_ok(self):
        """."""
        return not self['CoordConvErr-Mon']

    @property
    def is_backlash_compensation_enabled(self):
        """."""
        return self['EnblBacklashComp-Sts']

    def enable_backlash_compensation(self):
        """."""
        self['EnblBacklashComp-Sel'] = 1

    def disable_backlash_compensation(self):
        """."""
        self['EnblBacklashComp-Sel'] = 0

    def cmd_go_max_aperture(self):
        """Go to maximum slit aperture."""
        self['Home-Cmd'] = 1

    def _wait_finish_moving(self, pv_names, timeout=10):
        """."""
        t0 = _time.time()
        ret1 = self._wait(propty=pv_names[0], value=1, timeout=timeout)
        if not ret1:
            return ret1
        timeout -= _time.time() - t0
        ret2 = self._wait(propty=pv_names[1], value=1, timeout=timeout)
        return ret2

    @staticmethod
    def _check_limits(lims, is_negative=False):
        dlim = lims[1] - lims[0]
        if (dlim == 0) or ((dlim < 0) ^ is_negative):
            stg = 'greater' if is_negative else 'smaller'
            raise ValueError(f'Inner limit must be {stg:s} than outer limit.')


class ScraperH(_ScraperDev):
    """."""

    PROPERTIES_DEFAULT = _ScraperDev.PROPERTIES_DEFAULT + (
        'LeftSlitPos-SP', 'LeftSlitPos-RB',
        'RightSlitPos-SP', 'RightSlitPos-RB',
        'RightDoneMov-Mon', 'LeftDoneMov-Mon',
        'LeftSlitInnerLim-SP', 'LeftSlitInnerLim-RB',
        'LeftSlitOuterLim-SP', 'LeftSlitOuterLim-RB',
        'LeftSlitBacklashDist-SP', 'LeftSlitBacklashDist-RB',
        'LeftMotionCtrl-Cte', 'ForceLeftSlitPos-Cmd',
        'RightSlitInnerLim-SP', 'RightSlitInnerLim-RB',
        'RightSlitOuterLim-SP', 'RightSlitOuterLim-RB',
        'RightSlitBacklashDist-SP', 'RightSlitBacklashDist-RB',
        'RightMotionCtrl-Cte', 'ForceRightSlitPos-Cmd',
        )

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = _ScraperDev.DEVICES.H
        super().__init__(devname, props2init=props2init)

    @property
    def left_slit_pos(self):
        """Left slit position [mm]."""
        return self['LeftSlitPos-RB']

    @property
    def right_slit_pos(self):
        """Right slit position [mm]."""
        return self['RightSlitPos-RB']

    @property
    def is_left_slit_moving(self):
        """."""
        return not self['LeftDoneMov-Mon']

    @property
    def is_right_slit_moving(self):
        """."""
        return not self['RightDoneMov-Mon']

    @property
    def left_slit_limits(self):
        """Limits for left slit."""
        return [self['LeftSlitInnerLim-RB'], self['LeftSlitOuterLim-RB']]

    @left_slit_limits.setter
    def left_slit_limits(self, lims):
        """Set left slit limits."""
        _ScraperDev._check_limits(lims, is_negative=False)
        self['LeftSlitInnerLim-SP'] = lims[0]
        self['LeftSlitOuterLim-SP'] = lims[1]

    @property
    def right_slit_limits(self):
        """Limits for right slit."""
        return [self['RightSlitInnerLim-RB'], self['RightSlitOuterLim-RB']]

    @right_slit_limits.setter
    def right_slit_limits(self, lims):
        """Set right slit limits."""
        _ScraperDev._check_limits(lims, is_negative=True)
        self['RightSlitInnerLim-SP'] = lims[0]
        self['RightSlitOuterLim-SP'] = lims[1]

    @property
    def left_slit_control_prefix(self):
        """."""
        return self['LeftMotionCtrl-Cte']

    @property
    def right_slit_control_prefix(self):
        """."""
        return self['RightMotionCtrl-Cte']

    def wait_slits_finish_moving(self, timeout=10):
        """."""
        names = [slit + 'DoneMov-Mon' for slit in ('Left', 'Right')]
        return self._wait_finish_moving(pv_names=names, timeout=timeout)

    def move_left_slit(self, value):
        """Move left slit to given position [mm]."""
        self['LeftSlitPos-SP'] = value

    def move_right_slit(self, value):
        """Move right slit to given position [mm]."""
        self['RightSlitPos-SP'] = value

    def cmd_force_left_slit(self):
        """Force left slit position."""
        self['ForceLeftSlitPos-Cmd'] = 1
        return self._wait(propty='ForceComplete-Mon', value=1, timeout=10)

    def cmd_force_right_slit(self):
        """Force right slit position."""
        self['ForceRightSlitPos-Cmd'] = 1
        return self._wait(propty='ForceComplete-Mon', value=1, timeout=10)


class ScraperV(_ScraperDev):
    """."""

    PROPERTIES_DEFAULT = _ScraperDev.PROPERTIES_DEFAULT + (
        'TopSlitPos-SP', 'TopSlitPos-RB',
        'BottomSlitPos-SP', 'BottomSlitPos-RB',
        'BottomDoneMov-Mon', 'TopDoneMov-Mon',
        'TopSlitInnerLim-SP', 'TopSlitInnerLim-RB',
        'TopSlitOuterLim-SP', 'TopSlitOuterLim-RB',
        'TopMotionCtrl-Cte', 'ForceTopSlitPos-Cmd',
        'BottomSlitInnerLim-SP', 'BottomSlitInnerLim-RB',
        'BottomSlitOuterLim-SP', 'BottomSlitOuterLim-RB',
        'BottomMotionCtrl-Cte', 'ForceBottomSlitPos-Cmd',
        )

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = _ScraperDev.DEVICES.V
        super().__init__(devname, props2init=props2init)

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
    def top_slit_limits(self):
        """Set top slit limits."""
        return [self['TopSlitInnerLim-RB'], self['TopSlitOuterLim-RB']]

    @top_slit_limits.setter
    def top_slit_limits(self, lims):
        """Set top slit limits."""
        _ScraperDev._check_limits(lims, is_negative=False)
        self['TopSlitInnerLim-SP'] = lims[0]
        self['TopSlitOuterLim-SP'] = lims[1]

    @property
    def bottom_slit_limits(self):
        """Set bottom slit limits."""
        return [self['BottomSlitInnerLim-RB'], self['BottomSlitOuterLim-RB']]

    @bottom_slit_limits.setter
    def bottom_slit_limits(self, lims):
        """Set bottom slit limits."""
        _ScraperDev._check_limits(lims, is_negative=True)
        self['BottomSlitInnerLim-SP'] = lims[0]
        self['BottomSlitOuterLim-SP'] = lims[1]

    @property
    def bottom_slit_control_prefix(self):
        """."""
        return self['BottomMotionCtrl-Cte']

    @property
    def top_slit_control_prefix(self):
        """."""
        return self['TopMotionCtrl-Cte']

    def wait_slits_finish_moving(self, timeout=10):
        """."""
        names = [slit + 'DoneMov-Mon' for slit in ('Top', 'Bottom')]
        return self._wait_finish_moving(pv_names=names, timeout=timeout)

    def move_top_slit(self, value):
        """Change top slit position [mm]."""
        self['TopSlitPos-SP'] = value

    def move_bottom_slit(self, value):
        """Change bottom slit position [mm]."""
        self['BottomSlitPos-SP'] = value

    def cmd_force_top_slit(self):
        """Force top slit position."""
        self['ForceTopSlitPos-Cmd'] = 1
        return self._wait(propty='ForceComplete-Mon', value=1, timeout=10)

    def cmd_force_bottom_slit(self):
        """Force bottom slit position."""
        self['ForceBottomSlitPos-Cmd'] = 1
        return self._wait(propty='ForceComplete-Mon', value=1, timeout=10)
