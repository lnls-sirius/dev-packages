"""Optics correction utilities module."""
import os as _os


class HandleConfigNameFile:
    """Class to handle config_name file."""

    def __init__(self, acc, opticsparam):
        """Init."""
        if not (acc in ['BO', 'SI']):
            raise ValueError("'acc' must be 'BO' or 'SI' instance.")
        if not (opticsparam in ['tune', 'chrom']):
            raise ValueError(
                "'opticsparam' must be 'tune' or 'chrom' instance.")
        self.acc = acc.lower()
        self.opticsparam = opticsparam
        self.fpath = '/home/sirius/iocs-log/' + self.acc + '-ap-' + \
            opticsparam+'corr/'
        self.fname = self.fpath + self.acc + '-' + opticsparam + 'corr.txt'

    def get_config_name(self):
        """Get the configuration name in file."""
        if _os.path.isfile(self.fname):
            with open(self.fname, 'r') as fil:
                config_name = fil.read().strip('\n')
        else:
            _os.makedirs(self.fpath, exist_ok=True)
            config_name = get_default_config_name(self.acc, self.opticsparam)
            with open(self.fname, 'w+') as fil:
                fil.write(config_name)
        return config_name

    def set_config_name(self, config_name):
        """Set the configuration name in file."""
        if not isinstance(config_name, str):
            raise TypeError("'config_name' must be a string.")
        with open(self.fname, 'w+') as fil:
            fil.write(config_name)


def get_default_config_name(acc, opticsparam):
    """Get default config name."""
    if opticsparam == 'tune':
        if acc.upper() == 'BO':
            return 'BO.V05.04.M0'
        else:
            return 'SI.V24.04_S05.01'
    elif opticsparam == 'chrom':
        if acc.upper() == 'BO':
            return 'BO.V05.04.M0'
        else:
            return 'SI.V24.04_S05.01'
