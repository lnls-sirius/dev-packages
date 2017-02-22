
import pcaspy
import utils


class PCASDriver(pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app

    def read(self, reason):
        self.app.read(self,reason)
        value = super().read(reason)
        return value

    def write(self, reason, value):
        status = self.app.write(self,reason,value)
        if status: return super().write(reason, value)
        return status
