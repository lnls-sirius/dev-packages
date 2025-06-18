"""Carcara beamline control.

    * Beamline commissionning:
    https://cnpemcamp.sharepoint.com/:p:/s/lnls/groups/opt/EZB-ePPBFvRPqi5IM1fjTsoB7uwtUhUrw3inlGnRfDm1KA?e=4lP3Bi&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzI0MDYyNzI0ODE0In0%3D
"""

import inspect as _inspect
import time as _time

from .device import Device as _Device
from .dvf import DVFImgProc

class _Suffix:
    """Class to change pv dynamically."""

    def __init__(self, add_suffix, remove_suffix):
        self.suffix = add_suffix
        self.target = remove_suffix

    def __radd__(self, other: str) -> str:
        """Function will be called when the normal sum fails."""
        cleaned = other.replace(f':{self.target}', '')
        return cleaned + self.suffix

    def __repr__(self):
        """Representation function."""
        return self.suffix
    

class _ParamPVs:
    
    # SLITS
    # --- TOP ---
    TOP_PARAM_SP = None
    TOP_PARAM_RB = None
    TOP_PARAM_MON = None
    TOP_PARAM_STOP = None

    # --- BOTTOM ---
    BOTTOM_PARAM_SP = None
    BOTTOM_PARAM_RB = None
    BOTTOM_PARAM_MON = None
    BOTTOM_PARAM_STOP = None

    # --- LEFT ---
    LEFT_PARAM_SP = None
    LEFT_PARAM_RB = None
    LEFT_PARAM_MON = None
    LEFT_PARAM_STOP = None

    # --- RIGHT ---
    RIGHT_PARAM_SP = None
    RIGHT_PARAM_RB = None
    RIGHT_PARAM_MON = None
    RIGHT_PARAM_STOP = None

    # MIRROR
    # --- ROTY ---
    ROTY_PARAM_SP = None
    ROTY_PARAM_RB = None
    ROTY_PARAM_MON = None
    ROTY_PARAM_STOP = None

    # --- Tx ---
    TX_PARAM_SP = None
    TX_PARAM_RB = None
    TX_PARAM_MON = None
    TX_PARAM_STOP = None

    # --- Y1 ---
    Y1_PARAM_SP = None
    Y1_PARAM_RB = None
    Y1_PARAM_MON = None
    Y1_PARAM_STOP = None

    # --- Y2 ---
    Y2_PARAM_SP = None
    Y2_PARAM_RB = None
    Y2_PARAM_MON = None
    Y2_PARAM_STOP = None

    # --- Y3 ---
    Y3_PARAM_SP = None
    Y3_PARAM_RB = None
    Y3_PARAM_MON = None
    Y3_PARAM_STOP = None

    # MIRROR SENSORS
    # --- PHOTOCOLLECTOR ---
    PHOTOCOLLECTOR = None

    # --- TEMPERATURES ---
    TEMP_SP = None
    TEMP_RB = None
    TEMP0_MON = None
    TEMP1_MON = None
    TEMP2_MON = None
    TEMP3_MON = None
    TEMP4_MON = None

    # DVF
    # --- DVF Z POSITION ---
    DVF_Z_SP = None
    DVF_Z_RB = None
    DVF_Z_MON = None
    DVF_Z_STOP = None

    # --- DVF LENS POSITION ---
    DVF_LENS_SP = None
    DVF_LENS_RB = None
    DVF_LENS_MON = None
    DVF_LENS_STOP = None


class Slit(_Device):
    """Slit device."""

    class DEVICES:
        """Devices names."""

        SLIT1 = "CAX:A:PP02" # WBS1
        SLIT2 = "CAX:B:PP01" # WBS2

        ALL = (
            SLIT1, SLIT2,
        )

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]
    _THRESHOLD = 0.01 # [mm]
    _COUNT_LIM = 8
    _DELAY = 4 # [s]
    _TRIALS = 3

    # --- PARAM_PVS ---
    PARAM_PVS = _ParamPVs()

    PARAM_PVS.TOP_PARAM_SP = "A.VAL"
    PARAM_PVS.TOP_PARAM_RB = "A.VAL" # That doesn't have a RB PV
    PARAM_PVS.TOP_PARAM_MON = "A.RBV" # RBV is not the pv of readback
    PARAM_PVS.TOP_PARAM_STOP = "A.STOP"

    PARAM_PVS.BOTTOM_PARAM_SP = "B.VAL"
    PARAM_PVS.BOTTOM_PARAM_RB = "B.VAL" # That doesn't have a RB PV
    PARAM_PVS.BOTTOM_PARAM_MON = "B.RBV" # RBV is not the pv of readback
    PARAM_PVS.BOTTOM_PARAM_STOP = "B.STOP"

    PARAM_PVS.LEFT_PARAM_SP = "C.VAL"
    PARAM_PVS.LEFT_PARAM_RB = "C.VAL" # That doesn't have a RB PV
    PARAM_PVS.LEFT_PARAM_MON = "C.RBV" # RBV is not the pv of readback
    PARAM_PVS.LEFT_PARAM_STOP = "C.STOP"

    PARAM_PVS.RIGHT_PARAM_SP = "D.VAL"
    PARAM_PVS.RIGHT_PARAM_RB = "D.VAL" # That doesn't have a RB PV
    PARAM_PVS.RIGHT_PARAM_MON = "D.RBV" # RBV is not the pv of readback
    PARAM_PVS.RIGHT_PARAM_STOP = "D.STOP"

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)
    
    @property
    def top_pos(self):
        """Return slit top position [mm]."""
        return self[self.PARAM_PVS.TOP_PARAM_MON]

    @top_pos.setter
    def top_pos(self, value):
        """Set slit top position [mm]."""
        self[self.PARAM_PVS.TOP_PARAM_SP] = value

    @property
    def bottom_pos(self):
        """Return slit bottom position [mm]."""
        return self[self.PARAM_PVS.BOTTOM_PARAM_MON]

    @bottom_pos.setter
    def bottom_pos(self, value):
        """Set slit bottom position [mm]."""
        self[self.PARAM_PVS.BOTTOM_PARAM_SP] = value
    
    @property
    def left_pos(self):
        """Return slit left position [mm]."""
        return self[self.PARAM_PVS.LEFT_PARAM_MON]

    @left_pos.setter
    def left_pos(self, value):
        """Set slit left position [mm]."""
        self[self.PARAM_PVS.LEFT_PARAM_SP] = value
    
    @property
    def right_pos(self):
        """Return slit right position [mm]."""
        return self[self.PARAM_PVS.RIGHT_PARAM_MON]

    @right_pos.setter
    def right_pos(self, value):
        """Set slit right position [mm]."""
        self[self.PARAM_PVS.RIGHT_PARAM_SP] = value

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def _move_slit(self, side, value, threshold, max_count, delay):
        """ Moves the slit indicated by 'side' ('left', 'right', 'top', 'bottom')
            to the given value, returning True if reached, False on timeout.
        """

        if side not in ('left', 'right', 'top', 'bottom'):
            raise ValueError(f"Invalid dide: {side}")

        attr_name = "{}_pos".format(side)

        try:
            setattr(self, attr_name, value)
        except Exception as err:
            current = getattr(self, attr_name)
            raise IOError("PUT error: pv, pos = ({})\n{}".format(current, err))

        # Check for acknowledgement. Avoid endless loop if command is not properly received.
        icount = 0
        current_value = getattr(self, attr_name)
        while abs(current_value - value) > threshold:
            _time.sleep(delay)
            current_value = getattr(self, attr_name)
            print("Slit is Moving... | New pos: {:} | Curr: {:.2f} | Dif: {:}".format(value, current_value, abs(current_value - value)), end='\r')
            if icount >= max_count:
                print("\nWARNING: a lâmina '{:}' não se moveu.\nPosição atual: {:.4f}".format(side, current_value))
                return False
            icount += 1

        return True

    def _move_robust_slit(self, side, value, threshold, max_count, delay, trials):
        """
            Tries to move the blade indicated by `side` up to `value`, repeating
            up to `trials` times if it fails, and returns True on success.
        
        Args:
            side : 'top', 'bottom', 'left' or 'right'
            value : target position
            threshold, max_count, delay : parameters for move_*_slit
            trials : how many times to restart the movement if it fails
        
        Return: 
            bool : True or False
        """
        if side not in ('top', 'bottom', 'left', 'right'):
            raise ValueError("Invalid side: {}".format(side))

        method_name = "move_{}".format(side)
        move_method = getattr(self, method_name)
        if not callable(move_method):
            raise AttributeError("Method {} not exist.".format(method_name))
        
        ctrials = 0
        status = False
        try:
            while ctrials < trials and not status:
                status = move_method(
                    value=value,
                    threshold=threshold,
                    max_count=max_count,
                    delay=delay,
                )
                ctrials += 1
            current_value = getattr(self, "{}_pos".format(side))
            if not status:
                raise Exception('WARNING: maximum number of trials to move {} slit reached.\nCurrent position:'.format(side, current_value))
            print('Done!')
            return True
        except Exception:
            print('Not moved!')
            return False

    def cmd_top_stop(self, timeout=None):
        """Stop Slit top motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.TOP_PARAM_STOP, timeout)

    def cmd_bottom_stop(self, timeout=None):
        """Stop Slit bottom motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.BOTTOM_PARAM_STOP, timeout)

    def cmd_left_stop(self, timeout=None):
        """Stop Slit left motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.LEFT_PARAM_STOP, timeout)

    def cmd_right_stop(self, timeout=None):
        """Stop Slit right motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.RIGHT_PARAM_STOP, timeout)

    def move_top(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY):
        return self._move_slit(side='top', value=value, threshold=threshold, max_count=max_count, delay=delay)

    def move_bottom(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY):
        return self._move_slit(side='bottom', value=value, threshold=threshold, max_count=max_count, delay=delay)

    def move_left(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY):
        return self._move_slit(side='left', value=value, threshold=threshold, max_count=max_count, delay=delay)

    def move_right(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY):
        return self._move_slit(side='right', value=value, threshold=threshold, max_count=max_count, delay=delay)

    def move_robust_top(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY, trials=_TRIALS):
        return self._move_robust_slit(side='top', value=value, threshold=threshold, max_count=max_count, delay=delay, trials=trials)

    def move_robust_bottom(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY, trials=_TRIALS):
        return self._move_robust_slit(side='bottom', value=value, threshold=threshold, max_count=max_count, delay=delay, trials=trials)

    def move_robust_left(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY, trials=_TRIALS):
        return self._move_robust_slit(side='left', value=value, threshold=threshold, max_count=max_count, delay=delay, trials=trials)

    def move_robust_right(self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY, trials=_TRIALS):
        return self._move_robust_slit(side='right', value=value, threshold=threshold, max_count=max_count, delay=delay, trials=trials)


class Mirror(_Device):
    """Mirror device.
    
    * M1 online autodesk drawing:
    https://drive.autodesk.com/de29ccb7d/shares/SH9285eQTcf875d3c5396deb53e725438482
    """

    class DEVICES:
        """Devices names."""

        MIRROR1 = "CAX:A"

        ALL = (
            MIRROR1,
        )
    
    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

    # --- PARAM_PVS ---
    PARAM_PVS = _ParamPVs()

    # MIRROR CONTROL
    PARAM_PVS.ROTY_PARAM_SP = "PP01:A.VAL"
    PARAM_PVS.ROTY_PARAM_RB = "PP01:A.VAL" # That doesn't have a RB PV
    PARAM_PVS.ROTY_PARAM_MON = "PP01:A.RBV" # RBV is not the pv of readback
    PARAM_PVS.ROTY_PARAM_STOP = "PP01:A.STOP"

    PARAM_PVS.TX_PARAM_SP = "PP01:B.VAL"
    PARAM_PVS.TX_PARAM_RB = "PP01:B.VAL" # That doesn't have a RB PV
    PARAM_PVS.TX_PARAM_MON = "PP01:B.RBV" # RBV is not the pv of readback
    PARAM_PVS.TX_PARAM_STOP = "PP01:B.STOP"

    PARAM_PVS.Y1_PARAM_SP = "PP01:C.VAL"
    PARAM_PVS.Y1_PARAM_RB = "PP01:C.VAL" # That doesn't have a RB PV
    PARAM_PVS.Y1_PARAM_MON = "PP01:C.RBV" # RBV is not the pv of readback
    PARAM_PVS.Y1_PARAM_STOP = "PP01:C.STOP"

    PARAM_PVS.Y2_PARAM_SP = "PP01:D.VAL"
    PARAM_PVS.Y2_PARAM_RB = "PP01:D.VAL" # That doesn't have a RB PV
    PARAM_PVS.Y2_PARAM_MON = "PP01:D.RBV" # RBV is not the pv of readback
    PARAM_PVS.Y2_PARAM_STOP = "PP01:D.STOP"

    PARAM_PVS.Y3_PARAM_SP = "PP01:E.VAL"
    PARAM_PVS.Y3_PARAM_RB = "PP01:E.VAL" # That doesn't have a RB PV
    PARAM_PVS.Y3_PARAM_MON = "PP01:E.RBV" # RBV is not the pv of readback
    PARAM_PVS.Y3_PARAM_STOP = "PP01:E.STOP"

    # SENSORS
    PARAM_PVS.PHOTOCOLLECTOR = 'RIO01:9215A:ai0'

    PARAM_PVS.TEMP0_MON = 'RIO01:9226B:temp0'
    PARAM_PVS.TEMP1_MON = 'RIO01:9226B:temp1'
    PARAM_PVS.TEMP2_MON = 'RIO01:9226B:temp2'
    PARAM_PVS.TEMP3_MON = 'RIO01:9226B:temp3'
    PARAM_PVS.TEMP4_MON = 'RIO01:9226B:temp4'
    PARAM_PVS.TEMP_SP = 'RIO01:M1_CtrltempSp'
    PARAM_PVS.TEMP_RB = 'RIO01:M1_CtrltempSp' # That doesn't have a RB PV

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def roty_pos(self):
        """Return the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        return self[self.PARAM_PVS.ROTY_PARAM_MON]

    @property
    def tx_pos(self):
        """Return the linear actuator pos related to Tx translation [mm].

        This linear actuator translates directly to the horizontal
        transverse position of the mirror.
        """
        return self[self.PARAM_PVS.TX_PARAM_MON]

    @property
    def y1_pos(self):
        """Return the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in oposite horizontal ends.
        """
        return self[self.PARAM_PVS.Y1_PARAM_MON]

    @property
    def y2_pos(self):
        """Return the second linear vertical actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self[self.PARAM_PVS.Y2_PARAM_MON]

    @property
    def y3_pos(self):
        """Return the third linear actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self[self.PARAM_PVS.Y3_PARAM_MON]

    @property
    def photocurrent_signal(self):
        """Return induced voltage in the mirror photocollector [V]."""
        return self[self.PARAM_PVS.PHOTOCOLLECTOR]

    @property
    def temperature_0(self):
        """Return M1 temperature sensor 0 [°C]."""
        return self[self.PARAM_PVS.TEMP0_MON]

    @property
    def temperature_1(self):
        """Return M1 temperature sensor 1 [°C]."""
        return self[self.PARAM_PVS.TEMP1_MON]

    @property
    def temperature_2(self):
        """Return M1 temperature sensor 2 [°C]."""
        return self[self.PARAM_PVS.TEMP2_MON]

    @property
    def temperature_3(self):
        """Return M1 temperature sensor 3 [°C]."""
        return self[self.PARAM_PVS.TEMP3_MON]

    @property
    def temperature_4(self):
        """Return M1 temperature sensor 4 [°C]."""
        return self[self.PARAM_PVS.TEMP4_MON]

    @property
    def temperature_ref(self):
        """Return M1 temperature reference setpoint [°C]."""
        return self[self.PARAM_PVS.TEMP_RB]

    @roty_pos.setter
    def roty_pos(self, value):
        """Set the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        self[self.PARAM_PVS.ROTY_PARAM_SP] = value

    @tx_pos.setter
    def tx_pos(self, value):
        """Set the linear actuator pos related to Tx translation [mm].

        This linear actuator is directly related to the horizontal
        transverse position of the mirror.
        """
        self[self.PARAM_PVS.TX_PARAM_SP] = value
    
    @y1_pos.setter
    def y1_pos(self, value):
        """Set the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PARAM_PVS.Y1_PARAM_SP] = value

    @y2_pos.setter
    def y2_pos(self, value):
        """Set the second linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PARAM_PVS.Y2_PARAM_SP] = value

    @temperature_ref.setter
    def temperature_ref(self, value):
        """Set M1 temperature reference [°C]."""
        self[self.PARAM_PVS.TEMP_SP] = value

    @y3_pos.setter
    def y3_pos(self, value):
        """Set the third linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PARAM_PVS.Y3_PARAM_SP] = value

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def cmd_roty_stop(self, timeout=None):
        """Stop linear actuator for RotY rotation."""
        return self._cmd_motor_stop(self.PARAM_PVS.ROTY_PARAM_STOP, timeout)

    def cmd_tx_stop(self, timeout=None):
        """Stop linear actuator for Tx translation."""
        return self._cmd_motor_stop(self.PARAM_PVS.TX_PARAM_STOP, timeout)

    def cmd_y1_stop(self, timeout=None):
        """Stop linear actuator Y1."""
        return self._cmd_motor_stop(self.PARAM_PVS.Y1_PARAM_STOP, timeout)

    def cmd_y2_stop(self, timeout=None):
        """Stop linear actuator Y2."""
        return self._cmd_motor_stop(self.PARAM_PVS.Y2_PARAM_STOP, timeout)

    def cmd_y3_stop(self, timeout=None):
        """Stop linear actuator Y3."""
        return self._cmd_motor_stop(self.PARAM_PVS.Y3_PARAM_STOP, timeout)


class DVF(DVFImgProc):
    """."""

    class DEVICES:
        """Devices names."""

        CAX_DVF1 = 'CAX:A:BASLER01'
        CAX_DVF2 = 'CAX:B:BASLER01'
        ALL = (CAX_DVF1, CAX_DVF2)

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

    _DVF_WITH_CONTROLS = (DEVICES.CAX_DVF2,)

    # --- PARAM_PVS ---
    PARAM_PVS = _ParamPVs()

    def __init__(self, devname, props2init='all', **kwargs):
        """."""
        super().__init__(
            devname=devname,
            props2init=props2init,
            **kwargs
        )
        
        if devname in self._DVF_WITH_CONTROLS:
            self._set_motors_ctrl()
    
    @property
    def dvf_z_pos(self):
        """Return DVF base motor longitudinal position [mm]."""
        return self[self.PARAM_PVS.DVF_Z_MON]

    @dvf_z_pos.setter
    def dvf_z_pos(self, value):
        """Set DVF base motor longitudinal position [mm]."""
        self[self.PARAM_PVS.DVF_Z_SP] = value

    @property
    def dvf_lens_pos(self):
        """Return DVF lens position [mm]."""
        return self[self.PARAM_PVS.DVF_LENS_MON]

    @dvf_lens_pos.setter
    def dvf_lens_pos(self, value):
        """Set DVF lens position [mm]."""
        self[self.PARAM_PVS.DVF_LENS_SP] = value

    def _set_motors_ctrl(self):
        remove_suffix='BASLER01'

        self.PARAM_PVS.DVF_Z_SP = _Suffix(add_suffix='PP01:E.VAL', remove_suffix=remove_suffix)
        self.PARAM_PVS.DVF_Z_RB = _Suffix(add_suffix='PP01:E.VAL', remove_suffix=remove_suffix)
        self.PARAM_PVS.DVF_Z_MON = _Suffix(add_suffix='PP01:E.RBV', remove_suffix=remove_suffix)
        self.PARAM_PVS.DVF_Z_STOP = _Suffix(add_suffix='PP01:E.STOP', remove_suffix=remove_suffix)

        self.PARAM_PVS.DVF_LENS_SP = _Suffix(add_suffix='PP01:F.VAL', remove_suffix=remove_suffix)
        self.PARAM_PVS.DVF_LENS_RB = _Suffix(add_suffix='PP01:F.VAL', remove_suffix=remove_suffix)
        self.PARAM_PVS.DVF_LENS_MON = _Suffix(add_suffix='PP01:F.RBV', remove_suffix=remove_suffix)
        self.PARAM_PVS.DVF_LENS_STOP = _Suffix(add_suffix='PP01:F.STOP', remove_suffix=remove_suffix)

        self.PROPERTIES_DEFAULT += \
        tuple(set(
            value for key, value in _inspect.getmembers(self.PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def cmd_dvf_z_stop(self, timeout=None):
        """Stop DVF base motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.DVF_Z_STOP, timeout)

    def cmd_dvf_lens_stop(self, timeout=None):
        """Stop DVF lens motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.DVF_LENS_STOP, timeout)