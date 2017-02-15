
import pcaspy


class PCASDriver(pcaspy.Driver):
    
    def __init__(self):
        super().__init__()
        
    def read(self, reason):
        return super().read(reason)
         
    def write(self, reason, value):
        return super().write(reason, value)
