"""PosAng utilities."""
import os as _os


class HandleConfigNameFile:
    """Class to handle config_name file."""

    def __init__(self, tl, corrs_type):
        """Init."""
        if not (tl in ['TB', 'TS']):
            raise ValueError("'acc' must be 'TB' or 'TS' instance.")
        if not (corrs_type in ['ch-sept', 'sept-sept']):
            raise ValueError(
                "'opticsparam' must be 'ch-sept' or 'sept-sept' instance.")
        self.tl = tl.lower()
        self.corrs_type = corrs_type
        self.fpath = '/home/sirius/iocs-log/' + self.tl + '-ap-posang/'
        self.fname = self.fpath + self.tl + '-posang.txt'

    def get_config_name(self):
        """Get config name from file."""
        if _os.path.isfile(self.fname):
            with open(self.fname, 'r') as fil:
                config_name = fil.read().strip('\n')
        else:
            _os.makedirs(self.fpath, exist_ok=True)
            config_name = get_default_config_name(self.tl, self.corrs_type)
            with open(self.fname, 'w+') as fil:
                fil.write(config_name)
        return config_name

    def set_config_name(self, config_name):
        """Set config name in file."""
        if not isinstance(config_name, str):
            raise TypeError("'config_name' must be a string.")
        with open(self.fname, 'w+') as fil:
            fil.write(config_name)


def get_default_config_name(tl, corrs_type):
    """Get default config name."""
    if tl.upper() == 'TB':
        return 'Default_CHSept'
    else:
        if corrs_type == 'sept-sept':
            return 'TS.V04.01-M1.SeptSept.4CVs'
        else:
            return 'TS.V04.01-M1.CHSept.4CVs'
