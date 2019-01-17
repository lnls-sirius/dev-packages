from siriuspy.callbacks import Callback


class Base(Callback):

    @staticmethod
    def _iswritepv(pvname):
        return Base._issppv(pvname) or Base._iscmdpv(pvname)

    @staticmethod
    def _issppv(pvname):
        return pvname.endswith(('-Sel', '-SP'))

    @staticmethod
    def _iscmdpv(pvname):
        return pvname.endswith('-Cmd')

    @staticmethod
    def _isctepv(pvname):
        return pvname.endswith('-Cte')

    @staticmethod
    def _isrbpv(pvname):
        return pvname.endswith(('-Sts', '-RB'))

    @staticmethod
    def _fromsp2rb(pvname):
        return pvname.replace('-SP', '-RB').replace('-Sel', '-Sts')

    @staticmethod
    def _fromrb2sp(pvname):
        return pvname.replace('-RB', '-SP').replace('-Sts', '-Sel')
