"""PosAng utilities."""


class HandleConfigNameFile:
    """Class to handle config_name file."""

    def __init__(self, tl, corrs_type):
        """Init."""
        self.tl = tl.lower()
        self.corrs_type = corrs_type
        self.fpath = '/home/sirius/iocs-log/' + self.tl + '-ap-posang/'
        self.fname = self.fpath + self.tl + '-posang.txt'

    def get_config_name(self):
        """Get config name from file."""
        try:
            fil = open(self.fname, 'r')
            config_name = fil.read().strip('\n')
            fil.close()
        except Exception:
            fil = open(self.fname, 'w+')
            config_name = get_default_config_name(self.tl, self.corrs_type)
            fil.write(config_name)
            fil.close()
        return config_name

    def set_config_name(self, config_name):
        """Set config name in file."""
        fil = open(self.fname, 'w+')
        fil.write(config_name)
        fil.close()


def get_default_config_name(tl, corrs_type):
    """Get default config name."""
    if tl == 'TB':
        return 'Default_CHSept'
    else:
        if corrs_type == 'sept-sept':
            return 'TS.V04.01-M1.SeptSept'
        else:
            return 'TS.V04.01-M1'
