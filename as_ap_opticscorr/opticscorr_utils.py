"""Optics correction utilities module."""


def get_config_name(acc, opticsparam):
    """Get the configuration name in file."""
    if not (acc in ['bo', 'si']):
        raise ValueError("'acc' must be 'bo' or 'si' instance.")
    if not (opticsparam in ['tune', 'chrom']):
        raise ValueError("'opticsparam' must be 'tune' or 'chrom' instance.")

    try:
        f = open('/home/sirius/iocs-log/'+acc+'-ap-'+opticsparam+'corr/' +
                 acc+'-'+opticsparam+'corr.txt', 'r')
        config_name = f.read().strip('\n')
        f.close()
    except Exception:
        f = open('/home/sirius/iocs-log/'+acc+'-ap-'+opticsparam+'corr/' +
                 acc+'-'+opticsparam+'corr.txt', 'w+')
        config_name = 'Default'
        f.write(config_name)
        f.close()
    return config_name


def set_config_name(acc, opticsparam, config_name):
    """Set the configuration name in file."""
    if not (acc in ['bo', 'si']):
        raise ValueError("'acc' must be 'bo' or 'si' instance.")
    if not (opticsparam in ['tune', 'chrom']):
        raise ValueError("'opticsparam' must be 'tune' or 'chrom' instance.")
    if not isinstance(config_name, str):
        raise TypeError("'config_name' must be a string.")

    f = open('/home/sirius/iocs-log/'+acc+'-ap-'+opticsparam+'corr/' +
             acc+'-'+opticsparam+'corr.txt', 'w+')
    f.write(config_name)
    f.close()
