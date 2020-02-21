"""."""

from .client import ClientArchiver as _ClientArchiver


class PVDetails:
    """PV Arch Details."""

    def __init__(self, pvname, connector=None):
        """."""
        self.pvname = pvname
        self.connector = connector
        self.is_scalar = None
        self.nelms = None
        self.units = None
        self.is_paused = None
        self.host_name = None
        self.connected = None
        self.avg_bytes_per_event = None
        self.estimated_storage_rate_kb_hour = None
        self.estimated_storage_rate_mb_day = None
        self.estimated_storage_rate_gb_year = None

    @property
    def request_url(self):
        """."""
        url = self.connector.getPVDetails(self.pvname, get_request_url=True)
        return url

    @property
    def archived(self):
        """."""
        self.connect()
        data = self.connector.getPVDetails(self.pvname)
        if not data:
            return False
        return True

    def connect(self):
        """."""
        if self.connector is None:
            self.connector = _ClientArchiver()

    def update(self):
        """."""
        self.connect()
        data = self.connector.getPVDetails(self.pvname)
        if not data:
            return False
        for datum in data:
            # print(datum)
            field, value = datum['name'], datum['value']
            if field == 'Is this a scalar:':
                self.is_scalar = (value.lower() == 'yes')
            elif field == 'Number of elements:':
                self.nelms = int(value)
            elif field == 'Units:':
                self.units = value
            elif field == 'Is this PV paused:':
                self.is_paused = (value.lower() == 'yes')
            elif field == 'Host name':
                self.host_name = value
            elif field == 'Host name':
                self.host_name = value
            elif field == 'Is this PV currently connected?':
                self.connected = (value.lower() == 'yes')
            elif field == 'Average bytes per event':
                self.avg_bytes_per_event = float(value)
            elif field == 'Estimated storage rate (KB/hour)':
                self.estimated_storage_rate_kb_hour = float(value)
            elif field == 'Estimated storage rate (MB/day)':
                self.estimated_storage_rate_mb_day = float(value)
            elif field == 'Estimated storage rate (GB/year)':
                self.estimated_storage_rate_gb_year = float(value)
        return True

    def __str__(self):
        """."""
        rst = ''
        rst += '{:<30s}: {:}\n'.format('pvname', self.pvname)
        rst += '{:<30s}: {:}\n'.format('is_scalar', self.is_scalar)
        rst += '{:<30s}: {:}\n'.format('nelms', self.nelms)
        rst += '{:<30s}: {:}\n'.format('units', self.units)
        rst += '{:<30s}: {:}\n'.format('is_paused', self.is_paused)
        rst += '{:<30s}: {:}\n'.format('host_name', self.host_name)
        rst += '{:<30s}: {:}\n'.format('connected', self.connected)
        rst += '{:<30s}: {:}\n'.format(
            'avg_bytes_per_event', self.avg_bytes_per_event)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_kb_hour',
            self.estimated_storage_rate_kb_hour)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_mb_day',
            self.estimated_storage_rate_mb_day)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_gb_year',
            self.estimated_storage_rate_gb_year)
        return rst


class PVData:
    """PV Arch Details."""

    def __init__(self, pvname, connector=None):
        """."""
        self.pvname = pvname
        self.connector = connector
        self.timestamp_start = None
        self.timestamp_stop = None
        self.timestamp = None
        self.value = None
        self.status = None
        self.severity = None

    @property
    def request_url(self):
        """."""
        url = self.connector.getData(
            self.pvname, self.timestamp_start, self.timestamp_stop)
        return url

    @property
    def archived(self):
        """."""
        self.connect()
        req = self.connector.getPVDetails(self.pvname)
        if not req.ok:
            return False
        return True

    def connect(self):
        """."""
        if self.connector is None:
            self.connector = _ClientArchiver()

    def update(self):
        """."""
        self.connect()
        data = self.connector.getData(
            self.pvname, self.timestamp_start, self.timestamp_stop)
        if not data:
            return None
        self.timestamp, self.value, self.status, self.severity = data


class PV:
    """PV."""

    def __init__(self, pvname, connector=None):
        """."""
        self.pvname = pvname
        self.connector = connector
        self.details = PVDetails(self.pvname, self.connector)
        self.data = PVData(self.pvname, self.connector)

    def login(self, **kwargs):
        """."""
        self.connect()
        self.connector.login(**kwargs)

    def connect(self):
        """."""
        if self.connector is None:
            self.connector = _ClientArchiver()
            self.details = PVDetails(self.pvname, self.connector)
            self.data = PVData(self.pvname, self.connector)

    def update(self):
        """."""
        self.connect()
        self.details.update()
        self.data.update()

    def update_details(self):
        """."""
        self.connect()
        self.details.update()

    def update_data(self):
        """."""
        self.connect()
        self.data.update()

    def __str__(self):
        """."""
        rst = ''
        rst += '{:<30s}: {:}\n'.format('pvname', self.pvname)
        rst += '{:<30s}: {:}\n'.format('is_scalar', self.is_scalar)
        rst += '{:<30s}: {:}\n'.format('nelms', self.nelms)
        rst += '{:<30s}: {:}\n'.format('units', self.units)
        rst += '{:<30s}: {:}\n'.format('is_paused', self.is_paused)
        rst += '{:<30s}: {:}\n'.format('host_name', self.host_name)
        rst += '{:<30s}: {:}\n'.format('connected', self.connected)
        rst += '{:<30s}: {:}\n'.format(
            'avg_bytes_per_event', self.avg_bytes_per_event)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_kb_hour', self.estimated_storage_rate_kb_hour)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_mb_day', self.estimated_storage_rate_mb_day)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_gb_year', self.estimated_storage_rate_gb_year)
        return rst
