"""PulsedPS definition."""


class PulsedPS:
    """Pulsed Power Supply."""

    def __init__(self, data):
        """Get PS data."""
        self.name = data.psname
        self.database = data.propty_database

    def set_pwrstate(self, value):
        """Set pwrstate."""
        old_value = self._get('PwrState-Sts')
        if value != old_value:
            if value == 0:
                self.set_voltage(0)
            elif value == 1:
                self.set_voltage(0)
            else:
                return

            self._set('PwrState-Sts', value)
        return True

    def set_voltage(self, value):
        """Set voltage."""
        if self._is_on():
            value = max(self.database['Voltage-SP']['lolim'], value)
            value = min(self.database['Voltage-SP']['hilim'], value)
            self._set('Voltage-RB', value)
            self._set('Voltage-Mon', value)
        return True

    def set_pulsed(self, value):
        """Set pulsed enabled/disabled."""
        if self._is_on():
            if value in (0, 1):
                self._set('Pulse-Sts', value)
        return True

    def reset(self):
        """Reset PS."""
        if self._is_on():
            self.set_voltage(0)
            self.set_pulsed(0)
        return True

    def read_all(self):
        """Return fields values."""
        values = {}
        for field in ('PwrState-Sts', 'Voltage-RB',
                      'Voltage-Mon', 'Pulse-Sts'):
            values[self.name + ':' + field] = self._get(field)
        return values

    def _is_on(self):
        return (self._get('PwrState-Sts') == 1)

    def _get(self, field):
        return self.database[field]['value']

    def _set(self, field, value):
        self.database[field]['value'] = value
