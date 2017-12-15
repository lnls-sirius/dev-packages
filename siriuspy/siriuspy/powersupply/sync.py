"""Sync computer objects definition."""
from numpy import ndarray as _ndarray


class SyncWrite:
    """Class that sync all pvs."""

    # Computer Interface
    def compute_update(self, computed_pv, updated_pv_name, value):
        """Force value to not change."""
        if computed_pv.upper_disp_limit is None:
            self.compute_limits(computed_pv)

        kwargs = {}
        kwargs["value"] = value

        if "Cmd" in updated_pv_name:
            return kwargs  # issue callback

        # Init pvs
        if computed_pv.value is None:
            computed_pv.put(value)
            kwargs = {}
            kwargs["value"] = value
            return kwargs  # issue calback
        else:  # Lock
            if isinstance(value, _ndarray):
                changed = (computed_pv.value != value).any()
            else:
                changed = (computed_pv.value != value)

            if changed:
                computed_pv.put(computed_pv.value)
                return None

        return kwargs  # issue callback

    def compute_put(self, computed_pv, value):
        """Write to all pvs."""
        for pv in computed_pv.pvs:
            pv.put(value)

    def compute_limits(self, computed_pv):
        """Compute limits from real pvs."""
        computed_pv.upper_warning_limit = \
            computed_pv.pvs[0].upper_warning_limit
        computed_pv.lower_warning_limit = \
            computed_pv.pvs[0].lower_warning_limit
        computed_pv.upper_alarm_limit = computed_pv.pvs[0].upper_alarm_limit
        computed_pv.lower_alarm_limit = computed_pv.pvs[0].lower_alarm_limit
        computed_pv.upper_disp_limit = computed_pv.pvs[0].upper_disp_limit
        computed_pv.lower_disp_limit = computed_pv.pvs[0].lower_disp_limit


class SyncRead:
    """Class that sync all pvs."""

    # Computer Interface
    def compute_update(self, computed_pv, update_pv_name, value):
        """Do not update."""
        if computed_pv.upper_disp_limit is None:
            self.compute_limits(computed_pv)

        kwargs = {}
        kwargs["value"] = value
        return kwargs

    def compute_put(self, computed_pv, value):
        """Write to all pvs."""
        pass

    def compute_limits(self, computed_pv):
        """Compute limits from real pvs."""
        computed_pv.upper_warning_limit = \
            computed_pv.pvs[0].upper_warning_limit
        computed_pv.lower_warning_limit = \
            computed_pv.pvs[0].lower_warning_limit
        computed_pv.upper_alarm_limit = computed_pv.pvs[0].upper_alarm_limit
        computed_pv.lower_alarm_limit = computed_pv.pvs[0].lower_alarm_limit
        computed_pv.upper_disp_limit = computed_pv.pvs[0].upper_disp_limit
        computed_pv.lower_disp_limit = computed_pv.pvs[0].lower_disp_limit
