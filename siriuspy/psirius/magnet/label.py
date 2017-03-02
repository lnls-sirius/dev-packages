import psirius.web as _web


class ExcData:

    _fnames = None

    @staticmethod
    def _update_fnames(timeout=1):

        _fnames = _web.magnets_excitation_data_get_filenames_list(timeout=timeout)

    @staticmethod
    def get_fnames_all(update=False, timeout=1):

        if update or not _fnames: ExcData._update_fnames(timeout=timeout)
        return ExcData._fnames

    @staticmethod
    def get_fnames_regexp(regexp):
        pass

    @staticmethod
    def get_fnames_startswith(substring, with_or=None, without_and=None, update=False, timeout=1):

        if isinstance(with_or,str): with_or = (with_or,)
        if isinstance(without_and,str): without_and = (without_and,)

        all_fnames = ExcData.get_fnames_all(update=update, timeout=timeout)
        fnames = []
        for fname in all_fnames:
            if fname.startswith(substring):
                flag = False
                for st in with_or:
                    if st in fname:
                        flag = True
                        break
                for st in without_and:
                    if st in fname:
                        flag = False
                        break
                if flag: fnames.append(fname)
        return fnames


class Family:

    @staticmethod
    def si_quadrupoles():
        return ('QFA','QDA', 'Q1', 'Q2', 'Q3', 'Q4', 'QDB1', 'QFB', 'QDB2', 'QDP1', 'QFP', 'QDP2')
