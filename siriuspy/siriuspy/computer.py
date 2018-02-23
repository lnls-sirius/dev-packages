"""Computer interface Class."""


class Computer:
    """Computer class.

    Computer interface class.
    """

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Return dict with updated values.

        Update of property values in returned dict are triggered by
        'update_pv_name'.
        """
        raise NotImplementedError

    def compute_put(self, computed_pv, value):
        """Put value to all associated PVs."""
        raise NotImplementedError

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Compute limits of associated PVs."""
        raise NotImplementedError
