"""Insertion Device Configurations."""


class _IDConfig:
    """."""

    __POL_STATE_SEL_STR = None
    __POL_STATE_MON_STR = None

    @classmethod
    def get_polarization_state_sel_str(cls):
        """."""
        if cls.__POL_STATE_SEL_STR is None:
            pol_phases = cls.POL_STATE_SEL_PHASES
            cls.__POL_STATE_SEL_STR = \
                [pol_phases[idx][0] for idx in range(len(pol_phases))]
        return cls.__POL_STATE_SEL_STR
    
    @classmethod
    def get_polarization_state_mon_str(cls):
        if cls.__POL_STATE_MON_STR is None:
            cls.__POL_STATE_MON_STR = \
                cls.get_polarization_state_sel_str() + \
                [cls.POL_NONE_PHASE[0], cls.POL_UNDEF_PHASE[0]]
        return cls.__POL_STATE_MON_STR
    
    @classmethod
    def get_polarization_phase(cls, pol_idx):
        """Return phase corresponding to a particular polarization index."""
        return cls.POL_STATE_SEL_PHASES[pol_idx][1]

    @classmethod
    def get_polarization_state(cls, pparameter, kparameter):
        """Return polarization index for given pparameter and kparameter."""
        phase = pparameter
        gap = kparameter

        # check if polarization is defined
        for pol_idx, pol in cls.POL_STATE_SEL_PHASES.items():
            _, pol_phase = pol
            if abs(phase - pol_phase) <= cls.PPARAM_TOL:
                return pol_idx

        pol_state_mon_str = cls.get_polarization_state_mon_str()

        # checking if changing polarization
        if abs(gap - cls.PARKED_GAP) <= cls.KPARAM_TOL:
            pol_idx = pol_state_mon_str.index(cls.POL_NONE_PHASE[0])
            return pol_idx

        # at this point the configuration must be undefined
        pol_idx = pol_state_mon_str.index(cls.POL_UNDEF_PHASE[0])
        return pol_idx


class IDConfigEPU50(_IDConfig):
    """."""
    PPARAM_TOL: float = 0.5  # [mm] (phase)
    KPARAM_TOL: float = 0.1  # [mm] (gap)

    PERIOD_LENGTH: float = 50  # [mm]
    MINIMUM_GAP: float = +22  # [mm]
    MAXIMUM_GAP: float = +300  # [mm]
    PARKED_GAP: float = 300  # [mm]
    MINIMUM_PHASE: float = -25  # [mm]
    MAXIMUM_PHASE: float = +25  # [mm]
    PARKED_PHASE: float = 0  # [mm]
    POL_CHANGE_GAP: float = PARKED_GAP

    POL_CIRCULARN_PHASE: tuple = ('circularn', -16.36)  # [mm]
    POL_HORIZONTAL_PHASE: tuple = ('horizontal', 0.00)  # [mm]
    POL_CIRCULARP_PHASE: tuple = ('circularn', 16.36)  # [mm]
    POL_VERTICAL_PHASE: tuple = ('vertical', 25.00)  # [mm]
    POL_NONE_PHASE: tuple = ('none', None)
    POL_UNDEF_PHASE: tuple = ('undef', None)

    POL_STATE_SEL_PHASES: dict = {
        0: POL_CIRCULARN_PHASE,
        1: POL_HORIZONTAL_PHASE,
        2: POL_CIRCULARP_PHASE,
        3: POL_VERTICAL_PHASE}


