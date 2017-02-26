

class MagnetExcitation:

    def __init__(self, excdata_list, labels=None):

        if not labels:
            labels = [excdata.label for excdata in excdata_list]

        init_curr = 0.0
        self.coil = {}
        for i in range(len(labels)):
            self.coil[labels[i].lower().replace('.txt','')] = (init_curr,excdata_list[i])

    @property
    def coil_labels(self):
        return list(self.coil.keys())

    def get_coil_exci_data(self, label):
        return self.coil[label][1]

    def get_coil_curr(self, label):
        return self.coil[label][0]

    def set_coil_curr(self, label, value):
        self.coil[label][0] = value

    def get_coil_mult(self, label):
        curr = self.coil[label][0]
        exci = self.coil[label][1]
        multi = exci.interp_curr2mult(curr)

    @property
    def multipoles(self):
        coil_mult = [self.get_coil_mult(label) for label in self.coil.keys()]
        mult = coil_mult[0]
        for i in range(1,len(coil_mult)):
            for h in coil_mult[i].keys():
                m0 = mult['normal'][h] if h in multi['normal'] else 0.0
                mult['normal'][h] = m0 + coil_multi[i][h]
                m0 = mult['skew'][h] if h in multi['skew'] else 0.0
                mult['skew'][h] = m0 + coil_multi[i][h]
        return mult
