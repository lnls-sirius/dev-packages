"""."""
import time as _time

from epics.ca import CAThread as _Thread
import numpy as _np
import GPy as gpy

from ..epics import PV as _PV

from .csdev import Const as _Const

_np_poly = _np.polynomial.polynomial


class BiasFeedback():
    """."""

    def __init__(self, injctrl):
        """."""
        self._injctrl = injctrl
        self.loop_state = False
        self.already_set = False

        self.min_bias_voltage = -52  # [V]
        self.max_bias_voltage = -40  # [V]
        self.linmodel_angcoeff = 10  # [V/mA]
        self.model_type = _Const.BiasFBModelTypes.GaussianProcess
        self.model_max_num_points = 20
        self.model_opt_each_pts = 10

        self._num_points_after_opt = 0

        self.bias_data = None
        self.dcur_data = None
        self.gpmodel = None
        self.initialize_models()

        self.do_update_models = False
        self.curr3gev_pv = _PV(
            'BO-Glob:AP-CurrInfo:Current3GeV-Mon', auto_monitor=True,
            callback=self._callback_to_thread)

    @property
    def model_type_str(self):
        """."""
        return _Const.BiasFBModelTypes._fields[self.model_type]

    @property
    def use_gaussproc_model(self):
        """."""
        return self.model_type == _Const.BiasFBModelTypes.GaussianProcess

    @property
    def linmodel_coeffs(self):
        """."""
        ang = self.linmodel_angcoeff
        off = self.min_bias_voltage
        return (off, ang)

    def initialize_models(self):
        """."""
        self.bias_data = _np.linspace(
            self.min_bias_voltage,
            self.max_bias_voltage,
            self.model_max_num_points)

        off, ang = self.linmodel_coeffs
        self.dcur_data = _np_poly.polyval(self.bias_data, (-off/ang, 1/ang))

        y = self.bias_data[:, None].copy()
        x = self.dcur_data[:, None].copy()

        kernel = gpy.kern.RBF(input_dim=1)
        self.gpmodel = gpy.models.GPRegression(x, y, kernel)

    def get_delta_current_per_pulse(
            self, per=1, nrpul=1, curr_avg=100, curr_now=99.5, ltime=17*3600):
        """."""
        ltime = max(self._MINIMUM_LIFETIME, ltime)
        curr_tar = curr_avg / (1 - per*60/2/ltime)
        dcurr = (curr_tar - curr_now) / nrpul
        return dcurr

    def get_bias_voltage(self, dcurr):
        """."""
        if self.use_gaussproc_model:
            return self._get_bias_voltage_gpmodel(dcurr)
        return self._get_bias_voltage_linear_model(dcurr)

    # ############ Auxiliary Methods ############
    def _run(self):
        """."""
        print('Starting measurement:')
        if self._stopevt.is_set():
            return
        egun = self.devices['egun']
        injctrl = self.devices['injctrl']
        currinfo = self.devices['currinfo']

        self.data['dcurr'] = []
        self.data['bias'] = []

        pvo = currinfo.bo.pv_object('Current3GeV-Mon')
        pvo.auto_monitor = True
        cbv = pvo.add_callback(self._callback_to_thread)

        self.already_set = False
        while not self._stopevt.is_set():
            if injctrl.topup_state == injctrl.TopUpSts.Off:
                print('Topup is Off. Exiting...')
                break
            _time.sleep(2)
            next_inj = injctrl.topup_nextinj_timestamp
            dtim = next_inj - _time.time()
            if self.already_set or dtim > self.ahead_set_time:
                continue
            dcurr = self.get_delta_current_per_pulse()
            bias = self.get_bias_voltage(dcurr)
            egun.bias.set_voltage(bias)
            print(f'dcurr = {dcurr:.3f}, bias = {bias:.2f}')
            self.already_set = True
        pvo.remove_callback(cbv)
        print('Finished!')

    def _callback_to_thread(self, **kwgs):
        if not self.do_update_models:
            return
        _Thread(target=self._update_models, kwargs=kwgs, daemon=True).start()

    def _update_models(self, **kwgs):
        _time.sleep(0.3)

        bias = self._injctrl.egun_dev.bias.voltage
        dcurr = self._injctrl.currinfo_dev.injcurr
        if None in {bias, dcurr}:
            return

        self.bias_data = _np.r_[self.bias_data, bias]
        self.dcur_data = _np.r_[self.dcur_data, dcurr]
        self.bias_data = self.bias_data[-self.model_max_num_points:]
        self.dcur_data = self.dcur_data[-self.model_max_num_points:]

        # Do not overload data with repeated points:
        xun, cnts = _np.unique(self.bias_data, return_counts=True)
        if bias in xun:
            idx = (xun == bias).nonzero()[0][0]
            if cnts[idx] >= max(2, self.bias_data.size // 5):
                return
        self._num_points_after_opt += 1

        opt = self.model_opt_each_pts
        do_opt = opt and not (self._num_points_after_opt % opt)

        # Optimize Linear Model
        if do_opt and not self.use_gaussproc_model:
            self.linmodel_angcoeff = _np_poly.polyfit(
                self.dcur_data, self.bias_data - self.min_bias_voltage,
                deg=[1, ])[1]
            self._num_points_after_opt = 0

        # update Gaussian Process Model data
        x = self.bias_data.copy()
        y = self.dcur_data.copy()
        x = _np.r_[x, self.min_bias_voltage]
        y = _np.r_[y, 0]
        x.shape = (x.size, 1)
        y.shape = (y.size, 1)
        self.gpmodel.set_XY(x, y)

        # Optimize Gaussian Process Model
        if do_opt and self.use_gaussproc_model:
            self.gpmodel.optimize_restarts(num_restarts=2, verbose=False)
            self._num_points_after_opt = 0

        self.already_set = False

    def _get_bias_voltage_gpmodel(self, dcurr):
        bias = self._gpmodel_infer_newx(_np.array(dcurr, ndmin=1))
        bias = _np.minimum(bias, self.max_bias_voltage)
        bias = _np.maximum(bias, self.min_bias_voltage)
        return bias if bias.size > 1 else bias[0]

    def _get_bias_voltage_linear_model(self, dcurr):
        bias = _np_poly.polyval(dcurr, self.linmodel_coeffs)
        bias = _np.minimum(bias, self.max_bias_voltage)
        bias = _np.maximum(bias, self.min_bias_voltage)
        bias = _np.array([bias]).ravel()
        return bias if bias.size > 1 else bias[0]

    def _gpmodel_infer_newx(self, y):
        """Infer x given y for current GP model.

        The GP model object has its own infer_newX method, but it is slow and
        didn't give good results in my tests. So I decided to implement this
        simpler version, which works well.

        Args:
            y (numpy.ndarray, (N,)): y's for which we want to infer x.

        Returns:
            x: infered x's.

        """
        x = _np.linspace(self.min_bias_voltage, self.max_bias_voltage, 100)
        ys, _ = self._gpmodel_predict(x)
        idx = _np.argmin(_np.abs(ys - y[None, :]), axis=0)
        return x[idx, 0]

    def _gpmodel_predict(self, x):
        """Get the GP model prediction of the injected current.

        Args:
            x (numpy.ndarray): bias voltage.

        Returns:
            numpy.ndarray: predicted injected current.

        """
        x.shape = (x.size, 1)
        return self.gpmodel.predict(x)
