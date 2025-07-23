"""."""

from . import commands as _cmd_bsmp


class PSBSMPFactory:
    """."""

    psname_2_psbsmp = {
        'FBP': _cmd_bsmp.FBP,
        'FBP_DCLink': _cmd_bsmp.FBP_DCLink,
        'FAC_DCDC': _cmd_bsmp.FAC_DCDC,
        'FAC_2S_DCDC': _cmd_bsmp.FAC_2S_DCDC,
        'FAC_2S_ACDC': _cmd_bsmp.FAC_2S_ACDC,
        'FAC_2P4S_DCDC': _cmd_bsmp.FAC_2P4S_DCDC,
        'FAC_2P4S_ACDC': _cmd_bsmp.FAC_2P4S_ACDC,
        'FAP': _cmd_bsmp.FAP,
        'FAP_2P2S': _cmd_bsmp.FAP_2P2S,
        'FAP_4P': _cmd_bsmp.FAP_4P,
    }

    @staticmethod
    def create(psmodel, *args, **kwargs):
        """Return PSModel object."""
        if psmodel in PSBSMPFactory.psname_2_psbsmp:
            factory = PSBSMPFactory.psname_2_psbsmp[psmodel]
            return factory(*args, **kwargs)

        raise ValueError('PS Model "{}" not defined'.format(psmodel))
