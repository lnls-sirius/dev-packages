"""PosAng utilities."""


def get_config_name(tl, corrs_type):
    fname = './' + tl + '-posang.txt'
    try:
        f = open(fname, 'r')
        config_name = f.read().strip('\n')
        f.close()
    except Exception:
        f = open(fname, 'w+')
        config_name = get_default_config_name(tl, corrs_type)
        f.write(config_name)
        f.close()
    return config_name


def set_config_name(tl, config_name):
    f = open('/home/sirius/iocs-log/' + tl + '-ap-posang/' +
             tl + '-posang.txt', 'w+')
    f.write(config_name)
    f.close()


def get_default_config_name(tl, corrs_type):
    if tl == 'TB':
        return 'Default_CHSept'
    else:
        if corrs_type == 'sept-sept':
            return 'TS.V04.01-M1.SeptSept'
        else:
            return 'TS.V04.01-M1'
