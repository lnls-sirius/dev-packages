"""."""
import logging as _log

import GPy as gpy
import numpy as _np
from epics.ca import CAThread as _Thread
from numpy.polynomial import polynomial as _np_poly

from .csdev import Const as _Const, get_biasfb_database as _get_database


class BiasFeedback:
    """."""

    def __init__(self, injctrl):
        """."""
        db_ = _get_database()
        self.database = db_
        self._injctrl = injctrl
        self.loop_state = db_["BiasFBLoopState-Sel"]["value"]
        self.already_set = False

        self.min_bias_voltage = db_["BiasFBMinVoltage-SP"]["value"]  # [V]
        self.max_bias_voltage = db_["BiasFBMaxVoltage-SP"]["value"]  # [V]

        self.model_type = db_["BiasFBModelType-Sel"]["value"]
        self.model_max_num_points = db_["BiasFBModelMaxNrPts-SP"]["value"]
        self.model_auto_fit_rate = db_["BiasFBModelAutoFitEveryNrPts-SP"][
            "value"
        ]
        self.model_auto_fit = db_["BiasFBModelAutoFitParams-Sel"]["value"]
        self.model_update_data = db_["BiasFBModelUpdateData-Sel"]["value"]

        # [V/mA]:
        self.linmodel_angcoeff = db_["BiasFBLinModAngCoeff-SP"]["value"]
        self.linmodel_offcoeff = db_["BiasFBLinModOffCoeff-SP"]["value"]  # [V]

        self._npts_after_fit = 0

        self.bias_data = _np.array(
            db_["BiasFBModelDataBias-Mon"]["value"], dtype=float
        )
        self.injc_data = _np.array(
            db_["BiasFBModelDataInjCurr-Mon"]["value"], dtype=float
        )
        self.gpmodel = None
        self._initialize_models()

        self.do_update_models = False
        pv_ = self._injctrl.currinfo_dev.pv_object("InjCurr-Mon")
        pv_.auto_monitor = True
        pv_.add_callback(self._callback_to_thread)

        # pvname to write method map
        self.map_pv2write = {
            "LoopState-Sel": self.set_loop_state,
            "MinVoltage-SP": self.set_min_voltage,
            "MaxVoltage-SP": self.set_max_voltage,
            "ModelType-Sel": self.set_model_type,
            "ModelMaxNrPts-SP": self.set_max_num_pts,
            "ModelFitParamsNow-Cmd": self.cmd_fit_params,
            "ModelAutoFitParams-Sel": self.set_auto_fit,
            "ModelAutoFitEveryNrPts-SP": self.set_auto_fit_rate,
            "ModelUpdateData-Sel": self.set_update_data,
            "ModelDataBias-SP": self.set_data_bias,
            "ModelDataInjCurr-SP": self.set_data_injcurr,
            "LinModAngCoeff-SP": self.set_lin_ang_coeff,
            "LinModOffCoeff-SP": self.set_lin_off_coeff,
            "GPModNoiseStd-SP": self.set_gp_noise_std,
            "GPModKernStd-SP": self.set_gp_kern_std,
            "GPModKernLenScl-SP": self.set_gp_kern_leng,
            "GPModNoiseStdFit-Sel": self.set_gp_noise_std_fit,
            "GPModKernStdFit-Sel": self.set_gp_kern_std_fit,
            "GPModKernLenSclFit-Sel": self.set_gp_kern_leng_fit,
        }

    def init_database(self):
        """Set initial PV values."""
        for key, pvdbase in self.database.items():
            pvname = key.split(_Const.BIASFB_PROPTY_PREFIX)[1]
            self.run_callbacks(pvname, pvdbase["value"])

    @property
    def use_gpmodel(self):
        """."""
        return self.model_type == _Const.BiasFBModelTypes.GaussianProcess

    @property
    def linmodel_coeffs(self):
        """."""
        ang = self.linmodel_angcoeff
        off = self.linmodel_offcoeff
        return (off, ang)

    @property
    def linmodel_coeffs_inverse(self):
        """."""
        ang = self.linmodel_angcoeff
        off = self.linmodel_offcoeff
        return (-off / ang, 1 / ang)

    def get_delta_current_per_pulse(
        self, per=1, nrpul=1, curr_avg=100, curr_now=99.5, ltime=17 * 3600
    ):
        """."""
        ltime = max(_Const.BIASFB_MINIMUM_LIFETIME, ltime)
        curr_tar = curr_avg / (1 - per / 2 / ltime)
        dcurr = (curr_tar - curr_now) / nrpul
        return dcurr

    def get_bias_voltage(self, dcurr):
        """."""
        dcurr = max(0, dcurr)
        if self.use_gpmodel:
            return self._get_bias_voltage_gpmodel(dcurr)
        return self._get_bias_voltage_linear_model(dcurr)

    def run_callbacks(self, name, *args, **kwd):
        """."""
        name = _Const.BIASFB_PROPTY_PREFIX + name
        if self._injctrl.has_callbacks:
            self._injctrl.run_callbacks(name, *args, **kwd)
            return
        self.database[name]["value"] = args[0]

    def update_log(self, msg):
        """."""
        self._injctrl.run_callbacks("Log-Mon", msg)

    # ###################### Setter methods for IOC ######################
    def set_loop_state(self, value):
        """."""
        self.loop_state = bool(value)
        self.run_callbacks("LoopState-Sts", value)
        return True

    def set_min_voltage(self, value):
        """."""
        self.min_bias_voltage = value
        self._update_models()
        self.run_callbacks("MinVoltage-RB", value)
        return True

    def set_max_voltage(self, value):
        """."""
        self.max_bias_voltage = value
        self._update_models()
        self.run_callbacks("MaxVoltage-RB", value)
        return True

    def set_model_type(self, value):
        """."""
        self.model_type = value
        self.run_callbacks("ModelType-Sts", value)
        return True

    def set_max_num_pts(self, value):
        """."""
        self.model_max_num_points = int(value)
        self._update_models()
        self.run_callbacks("ModelMaxNrPts-RB", value)
        return True

    def cmd_fit_params(self, value):
        """."""
        _ = value
        self._update_models(force_optimize=True)
        return True

    def set_auto_fit(self, value):
        """."""
        self.model_auto_fit = bool(value)
        self.run_callbacks("ModelAutoFitParams-Sts", value)
        return True

    def set_auto_fit_rate(self, value):
        """."""
        self.model_auto_fit_rate = int(value)
        self.run_callbacks("ModelAutoFitEveryNrPts-RB", value)
        return True

    def set_update_data(self, value):
        """."""
        self.model_update_data = bool(value)
        self.run_callbacks("ModelUpdateData-Sts", value)
        return True

    def set_data_bias(self, value):
        """."""
        self.bias_data = _np.array(value)
        max_ = _Const.BIASFB_MAX_DATA_SIZE
        if self.bias_data.size > max_:
            msg = f"WARN: Bias data is too big (>{max_:d}). "
            msg += "Trimming first points."
            _log.warning(msg)
            self.update_log(msg)
            self.bias_data = self.bias_data[-max_:]
        self._update_models()
        self.run_callbacks("ModelDataBias-RB", value)
        return True

    def set_data_injcurr(self, value):
        """."""
        self.injc_data = _np.array(value)
        max_ = _Const.BIASFB_MAX_DATA_SIZE
        if self.injc_data.size > max_:
            msg = f"WARN: InjCurr data is too big (>{max_:d}). "
            msg += "Trimming first points."
            _log.warning(msg)
            self.update_log(msg)
            self.injc_data = self.injc_data[-max_:]
        self._update_models()
        self.run_callbacks("ModelDataInjCurr-RB", value)
        return True

    def set_lin_ang_coeff(self, value):
        """."""
        self.linmodel_angcoeff = value
        self._update_models()
        self.run_callbacks("LinModAngCoeff-RB", value)
        return True

    def set_lin_off_coeff(self, value):
        """."""
        self.linmodel_offcoeff = value
        self._update_models()
        self.run_callbacks("LinModOffCoeff-RB", value)
        return True

    def set_gp_noise_std(self, value):
        """."""
        self.gpmodel.likelihood.variance = value**2
        self._update_models()
        self.run_callbacks("GPModNoiseStd-RB", value)
        return True

    def set_gp_kern_std(self, value):
        """."""
        self.gpmodel.kern.variance = value**2
        self._update_models()
        self.run_callbacks("GPModKernStd-RB", value)
        return True

    def set_gp_kern_leng(self, value):
        """."""
        self.gpmodel.kern.lengthscale = value
        self._update_models()
        self.run_callbacks("GPModKernLenScl-RB", value)
        return True

    def set_gp_noise_std_fit(self, value):
        """."""
        if bool(value):
            self.gpmodel.likelihood.variance.unfix()
        else:
            self.gpmodel.likelihood.variance.fix()
        self.run_callbacks("GPModNoiseStdFit-Sts", value)
        return True

    def set_gp_kern_std_fit(self, value):
        """."""
        if bool(value):
            self.gpmodel.kern.variance.unfix()
        else:
            self.gpmodel.kern.variance.fix()
        self.run_callbacks("GPModKernStdFit-Sts", value)
        return True

    def set_gp_kern_leng_fit(self, value):
        """."""
        if bool(value):
            self.gpmodel.kern.lengthscale.unfix()
        else:
            self.gpmodel.kern.lengthscale.fix()
        self.run_callbacks("GPModKernLenSclFit-Sts", value)
        return True

    # ############ Auxiliary Methods ############
    def _callback_to_thread(self, **kwgs):
        if not self.do_update_models or not self.model_update_data:
            return
        _Thread(target=self._update_data, kwargs=kwgs, daemon=True).start()

    def _initialize_models(self):
        """."""
        self.bias_data = _np.linspace(
            self.min_bias_voltage,
            self.max_bias_voltage,
            self.model_max_num_points,
        )

        self.injc_data = _np_poly.polyval(
            self.bias_data, self.linmodel_coeffs_inverse
        )

        x = self.bias_data[:, None].copy()
        y = self.injc_data[:, None].copy()

        kernel = gpy.kern.RBF(input_dim=1)
        db_ = self.database["BiasFBGPModKernStd-RB"]
        kernel.variance.constrain_bounded(db_["lolim"] ** 2, db_["hilim"] ** 2)
        kernel.variance = db_["value"] ** 2
        if bool(self.database["BiasFBGPModKernStdFit-Sts"]["value"]):
            kernel.variance.unfix()
        else:
            kernel.variance.fix()

        db_ = self.database["BiasFBGPModKernLenScl-RB"]
        kernel.lengthscale.constrain_bounded(db_["lolim"], db_["hilim"])
        kernel.lengthscale = db_["value"]
        if bool(self.database["BiasFBGPModKernLenSclFit-Sts"]["value"]):
            kernel.lengthscale.unfix()
        else:
            kernel.lengthscale.fix()

        gpmodel = gpy.models.GPRegression(x, y, kernel)
        db_ = self.database["BiasFBGPModNoiseStd-RB"]
        gpmodel.likelihood.variance.constrain_bounded(
            db_["lolim"] ** 2, db_["hilim"] ** 2
        )
        gpmodel.likelihood.variance = db_["value"] ** 2
        if bool(self.database["BiasFBGPModNoiseStdFit-Sts"]["value"]):
            gpmodel.likelihood.variance.unfix()
        else:
            gpmodel.likelihood.variance.fix()

        self.gpmodel = gpmodel
        self._update_predictions()

    def _update_data(self, **kwgs):
        bias = self._injctrl.egun_dev.bias.voltage
        dcurr = kwgs["value"]
        if None in {bias, dcurr}:
            return

        # Do not overload data with repeated points:
        xun, cnts = _np.unique(self.bias_data, return_counts=True)
        if bias in xun:
            idx = (xun == bias).nonzero()[0][0]
            if cnts[idx] >= max(2, self.bias_data.size // 5):
                msg = "WARN: Too many data with this abscissa. "
                msg += "Discarding point."
                _log.warning(msg)
                self.update_log(msg)
                return
        self._npts_after_fit += 1

        # Update models data
        self.bias_data = _np.r_[self.bias_data, bias]
        self.injc_data = _np.r_[self.injc_data, dcurr]
        self.bias_data = self.bias_data[-_Const.BIASFB_MAX_DATA_SIZE :]
        self.injc_data = self.injc_data[-_Const.BIASFB_MAX_DATA_SIZE :]
        self._update_models()

    def _update_models(self, force_optimize=False):
        x = _np.r_[self.bias_data, self.linmodel_offcoeff]
        y = _np.r_[self.injc_data, 0]
        x = x[-self.model_max_num_points :]
        y = y[-self.model_max_num_points :]
        if x.size != y.size:
            msg = "WARN: Arrays with incompatible sizes. "
            msg += "Trimming first points of "
            msg += "bias." if x.size > y.size else "injcurr."
            _log.warning(msg)
            self.update_log(msg)
            siz = min(x.size, y.size)
            x = x[-siz:]
            y = y[-siz:]

        if x.size < 2:
            msg = "ERR: Too few data points. "
            msg += "Skipping Model update."
            _log.error(msg)
            self.update_log(msg)
            return

        fit_rate = self.model_auto_fit_rate
        do_opt = self.model_auto_fit
        do_opt &= not (self._npts_after_fit % fit_rate)
        do_opt |= force_optimize

        # Optimize Linear Model
        if do_opt and not self.use_gpmodel:
            self.linmodel_angcoeff = _np_poly.polyfit(
                y, x - self.linmodel_offcoeff, deg=[1]
            )[1]
            self._npts_after_fit = 0

        # update Gaussian Process Model data
        x.shape = (x.size, 1)
        y.shape = (y.size, 1)
        self.gpmodel.set_XY(x, y)

        # Optimize Gaussian Process Model
        if do_opt and self.use_gpmodel:
            self.gpmodel.optimize_restarts(num_restarts=2, verbose=False)
            self._npts_after_fit = 0

        self.run_callbacks("ModelNrPtsAfterFit-Mon", self._npts_after_fit)
        self._update_predictions()

    def _update_predictions(self):
        gp_ = self.gpmodel
        self.run_callbacks(
            "GPModNoiseStd-Mon", float(gp_.likelihood.variance) ** 0.5
        )
        self.run_callbacks("GPModKernStd-Mon", float(gp_.kern.variance) ** 0.5)
        self.run_callbacks("GPModKernLenScl-Mon", float(gp_.kern.lengthscale))
        self.run_callbacks("LinModAngCoeff-Mon", self.linmodel_angcoeff)
        self.run_callbacks("LinModOffCoeff-Mon", self.linmodel_offcoeff)

        self.run_callbacks("ModelDataBias-Mon", self.gpmodel.X.ravel())
        self.run_callbacks("ModelDataInjCurr-Mon", self.gpmodel.Y.ravel())
        self.run_callbacks("ModelNrPts-Mon", self.gpmodel.Y.size)

        injcurr = _np.linspace(0, 1, 100)
        bias_lin = self._get_bias_voltage_linear_model(injcurr)
        bias_gp = self._get_bias_voltage_gpmodel(injcurr)
        self.run_callbacks("LinModInferenceInjCurr-Mon", injcurr)
        self.run_callbacks("LinModInferenceBias-Mon", bias_lin)
        self.run_callbacks("GPModInferenceInjCurr-Mon", injcurr)
        self.run_callbacks("GPModInferenceBias-Mon", bias_gp)

        bias = _np.linspace(self.min_bias_voltage, self.max_bias_voltage, 100)
        injc_lin = _np_poly.polyval(bias, self.linmodel_coeffs_inverse)
        injca_gp, injcs_gp = self._gpmodel_predict(bias)
        injcs_gp = _np.sqrt(injcs_gp)
        self.run_callbacks("LinModPredBias-Mon", bias)
        self.run_callbacks("LinModPredInjCurrAvg-Mon", injc_lin)
        self.run_callbacks("GPModPredBias-Mon", bias)
        self.run_callbacks("GPModPredInjCurrAvg-Mon", injca_gp.ravel())
        self.run_callbacks("GPModPredInjCurrStd-Mon", injcs_gp.ravel())

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
        x = _np.linspace(self.min_bias_voltage, self.max_bias_voltage, 300)
        ys, _ = self._gpmodel_predict(x)
        ys[ys < 0] = 0
        idm = ys[:, 0].argmax()
        idm += 1
        idx = _np.argmin(_np.abs(ys[:idm] - y[None, :]), axis=0)
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
