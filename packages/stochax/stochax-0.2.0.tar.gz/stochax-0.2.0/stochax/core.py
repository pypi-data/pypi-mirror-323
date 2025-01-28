"""
-------
core.py
-------

The base module for stochastic processes

Useful resources are:

• Ait-Sahalia, Yacine.
    "Transition densities for interest rate and other nonlinear diffusions."
    Quantitative Analysis In Financial Markets:
    Collected Papers of the New York University Mathematical Finance Seminar
    (Volume II). 2001.

• Aït‐Sahalia, Yacine.
    "Maximum likelihood estimation of discretely sampled diffusions:
    a closed‐form approximation approach."
    Econometrica 70.1 (2002): 223-262.

• Brigo, Damiano, et al.
    "A stochastic processes toolkit for risk management."
    Available at SSRN 1109160 (2007).
"""

import abc
import sys
import logging

from copy import deepcopy
from typing import Any, Self, Callable
from inspect import signature

import numpy as np
import pandas as pd
import polars as pl

from joblib import Parallel, delayed
from pydantic import BaseModel, ValidationError
from scipy.stats import truncnorm
from numpy.random import Generator
from arch.bootstrap import CircularBlockBootstrap, optimal_block_length
from scipy.optimize import minimize

from .calibration_results import CalibrationResult

logger = logging.getLogger(__name__)


def objective(
    params: list,
    process: Any | None = None,
    observations: pd.DataFrame | pl.DataFrame | None = None,
    delta: float = 1.0,
) -> float:
    """
    Calculate the objective (i.e. the negative log-likelihood)
    function using a wrapper for a given stochastic process

    Args:
        params: The input values representing parameters for the stochastic process.
        process: An instance of a stochastic process object
        observations: The observation data used for calculating the log-likelihood
        delta: The sampling frequency or time step used in the observations

    Returns:
        the negative log-likelihood value

    Notes:
        - If the provided parameters lead to an invalid computation (e.g., due to invalid input or model constraints),
            the function returns positive infinity (np.inf).
        - The log-likelihood value returned is negated to align with optimization conventions,
            where the objective is typically minimized.

    """
    try:
        obj = process(*params)
    except (ValueError, ValidationError):
        return np.inf

    try:
        return -obj.log_likelihood(observations=observations, delta=delta)
    except ValueError:
        return np.inf


class ABCStochasticProcess(abc.ABC):
    """
    An abstract base class representing stochastic processes.

    This class serves as the abstract base class for defining stochastic processes.
    It provides methods for simulation, likelihood calculation, parameter estimation, and calibration.
    Subclasses must implement specific methods for simulation, likelihood calculation, and parameter estimation based
    on the characteristics of the stochastic process.

    Notes:
        Subclasses must implement the _simulate, _log_likelihood, and _calibrate methods.
        - The _simulate method should simulate paths of the stochastic process.
        - The _log_likelihood method should calculate the log-likelihood function.
        - The _calibrate method should calibrate the parameters based on observations.
        - Users should instantiate concrete subclasses of ABCStochasticProcess rather than ABCStochasticProcess itself.

    """

    _min_optimal_length = 25
    _bounds = None

    def __init__(self, rng: Generator | int | None):
        """
        Initialize the class

        Args:
            rng: The random state for generating simulations and bootstrap samples

        """

        if rng is None:
            rng = np.random.default_rng()
        elif isinstance(rng, int):
            rng = np.random.default_rng(rng)

        self._rng = rng

    @property
    def parameters(self) -> dict:
        """Return the model parameters"""
        parameters = signature(self.__init__).parameters
        return {par: getattr(self, par) for par in parameters if par != "rng"}

    @property
    def bounds(self) -> BaseModel:
        """Return the model bounds"""
        return self._bounds

    @property
    def is_calibrated(self) -> bool:
        """Return a flag to indicate whereas parameters are not null"""
        return all(v is not None for v in self.parameters.values())

    def _validate_parameters(self) -> None:
        """Validate the process parameters using pydantic"""
        self._bounds(**self.parameters)

    def _assert_finite_parameters(self) -> None:
        """Raise an error if any parameter is None, Inf or null"""

        for key, val in self.parameters.items():
            if val is None:
                raise TypeError(f"`{key}` is None")
            elif pd.isnull(val):
                raise TypeError(f"`{key}` is NaN")
            elif np.isinf(val):
                raise TypeError(f"`{key}` is Inf")

        self._validate_parameters()

    def _msg(self) -> str:
        """Create the str attribute"""
        params = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.__class__.__name__}({params})"

    def __str__(self) -> str:
        """Override the print output"""
        return self._msg()

    def __repr__(self) -> str:
        """Override the REPL output"""
        return self._msg()

    def simulate(
        self,
        initial_value: float | tuple,
        n_steps: int,
        delta: float = 1.0,
        n_simulations: int = 1,
        method: str = "exact",
    ) -> pd.DataFrame:
        """
        Simulate paths of the stochastic process.

        This method generates simulated paths of a generic stochastic process based on the provided parameters.

        Args:
            initial_value: The initial value or starting point for the simulation, if required also the
                initial volatility
            n_steps: The number of steps or observations to simulate, excluding the initial value
            delta: The sampling interval between consecutive observations
            n_simulations: The number of paths to simulate
            method: The number of paths to simulate


        Returns:
            A DataFrame containing simulated paths of the stochastic process.
                Each row represents time step, and each column represents a separate simulation path.
                The first row corresponds to the initial value, and subsequent rows correspond
                to subsequent observations.
                The DataFrame has shape `(n_steps + 1, n_simulations)`

        """
        self._assert_finite_parameters()

        if delta <= 0:
            raise ValueError("delta must be > 0")
        if n_steps < 1:
            raise ValueError("path length n_steps must be >= 1")
        if n_simulations < 1:
            raise ValueError("n_simulations must be >= 1")

        return self._simulate(
            initial_value=initial_value,
            n_steps=n_steps,
            delta=delta,
            n_simulations=n_simulations,
            method=method,
        )

    @abc.abstractmethod
    def _simulate(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        pass

    def log_likelihood(self, observations: pd.DataFrame, delta: float = 1.0) -> float:
        """
        Calculate the log-likelihood function for the stochastic process.

        This method computes the log-likelihood function of the stochastic process based on the provided observations
        and sampling interval, using the parameters stored as attributes within the object.

        Args:
            observations: A DataFrame containing observations of the stochastic process. The column
                represents a path or realization of the process, and each row represents a separate time step.
                The DataFrame should have dimensions `(n_observations, ),` where `n_observations` is the number of
                observations per path.
            delta: The sampling interval between consecutive observations

        Returns:
            The value of the log-likelihood function computed for the given observations

        """
        self._assert_finite_parameters()
        observations = self._validate_observations(observations=observations)

        ll = self._log_likelihood(observations=observations, delta=delta)

        if pd.isnull(ll) or np.isinf(ll):
            raise ValueError(f"log-likelihood: {ll} is not finite")

        return ll

    @abc.abstractmethod
    def _log_likelihood(self, *args, **kwargs) -> float:
        pass

    def _maximize_log_likelihood(
        self,
        observations: pd.DataFrame,
        delta: float = 1.0,
        n_trials: int = 8,
        starting_value: dict | None = None,
        n_jobs: int = 2,
    ) -> dict:
        """
        Estimate the process parameter using a numerical procedure.
        For a review on this topic see for instance

        • López-Pérez, Alejandra, Manuel Febrero-Bande, and Wencesalo González-Manteiga.
            "Parametric Estimation of Diffusion Processes:
            A Review and Comparative Study."
            Mathematics 9.8 (2021): 859.

        Args:
            observations: column indicates the path and rows indicates the observations
            delta: sampling interval
            n_trials: number of trials for different starting points
            starting_value: initial point for the numerical estimation
            n_jobs: number of parallel jobs

        """
        m = sys.maxsize / 2
        bounds = [(-m, m) for _ in range(len(self.parameters))]

        if starting_value is None:
            scaling = {parameter: (0.0, 1.0) for parameter in self.parameters}

        elif isinstance(starting_value, dict):
            scaling = {
                k: (v, v / 2 if v != 0 else 1.0) for k, v in starting_value.items()
            }

        else:
            raise TypeError("starting_value is a dict")

        rv_list = list()
        for itm in bounds:
            rv = truncnorm(a=itm[0], b=itm[1])
            rv.random_state = self._rng
            rv_list.append(rv)

        x0s = [
            np.array(
                [
                    mu + sigma * rv.rvs()
                    for rv, (_, (mu, sigma)) in zip(rv_list, scaling.items())
                ]
            )
            for _ in range(n_trials)
        ]

        results = Parallel(n_jobs=n_jobs)(
            delayed(
                lambda x: minimize(
                    objective,
                    x0=x,
                    args=(self.__class__, observations, delta),
                    bounds=bounds,
                    method="Powell",
                )
            )(x0)
            for x0 in x0s
        )

        results = sorted(
            filter(lambda r: (r.success and np.isfinite(r.fun)), results),
            key=lambda r: r.fun,
        )
        if len(results) == 0:
            raise RuntimeError("Numerical optimization not performed.")

        best_result = results[0]

        return {
            parameter: val
            for parameter, val in zip(self.parameters.keys(), best_result.x)
        }

    def _compute_mle(
        self, f: Callable, observations: pd.DataFrame, delta: float = 1.0, **kwargs
    ):
        """
        Set coefficients to mle estimators. Coefficients_std remains None

        Args:
            f: estimate function
            observations: column indicates the path and rows indicates the observations
            delta: sampling interval
            kwargs: additional parameters used by the function `f`

        """

        estimated_params = f(observations, delta, **kwargs)

        for parameter, val in estimated_params.items():
            if parameter not in self.parameters.keys():
                raise KeyError(f"`{parameter}` not defined")
            setattr(self, parameter, val)
            setattr(self, f"{parameter}_std", None)

    def _compute_nonparametric_bootstrap(
        self,
        f: Callable,
        observations: pd.DataFrame,
        delta: float = 1.0,
        n_boot_resamples: int = 10,
        n_jobs: int = 2,
    ):
        """
        Perform the non-parametric bootstrap using circular-block bootstrap
        as proposed by:

        • Hall, Peter.
            "Resampling a coverage pattern."
            Stochastic processes and their applications 20.2 (1985): 231-246.

        • Bühlmann, Peter.
            "Bootstraps for time series."
            Statistical science (2002): 52-72.

        The optimal length is selected according to:

        • Buhlmann, Peter.
            "Blockwise bootstrapped empirical process for stationary sequences."
             The Annals of Statistics (1994): 995-1012.

        Set coefficients to non-parametric bootstrap coefficients.
        Set coefficients_std to non-parametric bootstrap coefficients std.

        Args:
            f: estimate function
            observations: column indicates the path and rows indicates the observations
            delta: sampling interval
            n_boot_resamples: number bootstrap resamples
            n_jobs: number of parallel jobs

        """

        optimal_length = max(
            int(optimal_block_length(observations).circular.iloc[0]),
            self._min_optimal_length,
        )

        bs_c = CircularBlockBootstrap(optimal_length, observations, seed=self._rng)

        result = Parallel(n_jobs=n_jobs)(
            delayed(lambda x: f(x, delta=delta))(*pos_data)
            for pos_data, kw_data in bs_c.bootstrap(n_boot_resamples)
        )
        self._bootstrap_results = pd.DataFrame(result)

        for parameter in self._bootstrap_results.columns:
            setattr(self, parameter, self._bootstrap_results[parameter].mean())
            setattr(self, f"{parameter}_std", self._bootstrap_results[parameter].std())

    def _compute_parametric_bootstrap(
        self,
        f: Callable,
        observations: pd.DataFrame,
        delta: float = 1.0,
        n_boot_resamples: int = 10,
        n_jobs: int = 2,
    ):
        """
        Perform a parametric bootstrap calibration according to the procedure
        proposed in:

        • Tang, Cheng Yong, and Song Xi Chen.
            "Parameter estimation and bias correction for diffusion processes."
            Journal of Econometrics 149.1 (2009): 65-81.

        Set coefficients to parametric bootstrap coefficients.
        Set coefficients_std to parametric bootstrap coefficients std.

        Args:
            f: estimate function
            observations: column indicates the path and rows indicates the observations
            delta: sampling interval
            n_boot_resamples: number bootstrap resamples
            n_jobs: number of parallel jobs

        """
        estimated_params = f(observations, delta)

        if all(pd.notnull(val) for key, val in estimated_params.items()):
            for parameter in self.parameters.keys():
                setattr(self, parameter, estimated_params[parameter])

            obs_boot = self.simulate(
                observations.iloc[0, 0],
                n_steps=len(observations) - 1,
                delta=delta,
                n_simulations=n_boot_resamples,
            )

            result = Parallel(n_jobs=n_jobs)(
                delayed(lambda x: f(x, delta=delta))(obs_boot.iloc[:, i].to_frame())
                for i in range(n_boot_resamples)
            )
            self._bootstrap_results = pd.DataFrame(result)

            for parameter in self._bootstrap_results.columns:
                val = getattr(self, parameter)
                setattr(
                    self, parameter, 2.0 * val - self._bootstrap_results[parameter].mean()
                )
                setattr(
                    self, f"{parameter}_std", self._bootstrap_results[parameter].std()
                )

    def calibrate(
        self,
        observations: pd.DataFrame,
        delta: float = 1,
        method: str = "mle",
        n_boot_resamples: int = 1000,
        n_jobs: int = 2,
        n_trials: int = 8,
        starting_value: dict | None = None,
    ) -> CalibrationResult:
        """
        Calibrate the parameters of the stochastic process using various estimation methods.

        This method calibrates the parameters of the stochastic process based on the provided observations
        and specified calibration settings. The calibration can be performed using different methods, including
        Maximum Likelihood Estimation (MLE), parametric bootstrap, or non-parametric bootstrap.

        For numerical estimation of MLE see:

        • López-Pérez, Alejandra, Manuel Febrero-Bande, and Wencesalo González-Manteiga.
            "Parametric Estimation of Diffusion Processes:
            A Review and Comparative Study."
            Mathematics 9.8 (2021): 859.

        For parametric bootstrap:

        • Tang, Cheng Yong, and Song Xi Chen.
            "Parameter estimation and bias correction for diffusion processes."
            Journal of Econometrics 149.1 (2009): 65-81.

        For non-parametric bootstrap

        • Hall, Peter.
            "Resampling a coverage pattern."
            Stochastic processes and their applications 20.2 (1985): 231-246.

        • Bühlmann, Peter.
            "Bootstraps for time series."
            Statistical science (2002): 52-72.

        The optimal length is selected according to:

        • Buhlmann, Peter.
            "Blockwise bootstrapped empirical process for stationary sequences."
             The Annals of Statistics (1994): 995-1012.


        Args:
            observations: A DataFrame containing observations of the stochastic process. The column
                represents a path or realization of the process, and each row represents a separate time step.
                The DataFrame should have dimensions (n_observations, ), where n_observations is the number of
                observations per path.
            delta: The sampling interval between consecutive observations
            method: The calibration method to use. Choices are 'mle' for Maximum Likelihood Estimation,
                'parametric_bootstrap' for parametric bootstrap, and 'non_parametric_bootstrap'
                for non-parametric bootstrap
            n_boot_resamples: The number of bootstrap resamples to perform during calibration
            n_jobs: The number of parallel jobs to use during calibration
            starting_value: initial value used in the numerical calibration procedue, if not
                provided a random guess is performed
            n_trials: number of numerical trials in the numerical mle

        Returns:
            An object that stores the results of the calibration procedure, including the calibrated
                parameters, observations used for calibration, calibration method,
                number of bootstrap resamples, number of
                parallel jobs, and bootstrap results.


        """
        observations = self._validate_observations(observations=observations)

        if delta <= 0:
            raise ValueError("delta must be >0 ")
        if n_boot_resamples < 1:
            raise ValueError("n_boot resamples must be >= 1; recommended > 500")
        if len(observations) < 2:
            raise ValueError("observations length must be >= 1")

        self._bootstrap_results = pd.DataFrame(
            {k: [None] for k in self.parameters.keys()}
        )

        self._calibrate(
            observations=observations,
            delta=delta,
            method=method,
            n_boot_resamples=n_boot_resamples,
            n_jobs=n_jobs,
            n_trials=n_trials,
            starting_value=starting_value,
        )
        # test if parameters are well-defined
        self._validate_parameters()

        return CalibrationResult(
            process=self.copy(),
            observations=observations.copy(),
            delta=delta,
            method=method,
            n_boot_resamples=n_boot_resamples,
            n_jobs=n_jobs,
            rng=self._rng,
            bootstrap_results=self._bootstrap_results,
        )

    def _calibrate(
        self,
        observations: pd.DataFrame,
        delta: float = 1,
        method: str = "mle",
        n_boot_resamples: int = 1000,
        n_jobs: int = 2,
        starting_value: list | None = None,
        n_trials: int = 8,
    ):
        """
        Calibrate the stochastic process and store parameters as attribute
        If method is 'mle' function does a simple mle
        If method is 'parametric_bootstrap' function does a parametric bootstrap procedure for bias correction.
        If method is 'non_parametric_bootstrap' function does a non-parametric bootstrap procedure for bias correction

        Warnings:

            A remark: f_mle MUST return parameters in the same
            order as `__init__` method with the following signature:

        Examples:

                >>> def f_mle(observations: pd.DataFrame,
                >>>     delta: float = 1.,
                >>>     **kwargs
                >>> ): -> dict

        Args:
            observations: column indicates the path and rows indicates the observations
            delta: sampling interval
            method: choices are 'mle', 'pseudo_mle', 'parametric_bootstrap', 'non_parametric_bootstrap'
            n_boot_resamples: number bootstrap resamples
            n_jobs: number of parallel jobs
            starting_value: initial value used in the numerical calibration procedue, if not
                provided a random guess is performed
            n_trials: number of numerical trials in the numerical mle

        """

        if hasattr(self, "_maximum_likelihood_estimation"):
            f_mle = self._maximum_likelihood_estimation
        elif hasattr(self, "_pseudo_maximum_likelihood_estimation"):
            f_mle = self._pseudo_maximum_likelihood_estimation
        else:
            f_mle = self._maximize_log_likelihood
            logger.warning(
                "mle/pseudo_mle not implemented.\
            Use numerical estimation from the log_likelihood."
            )

        available_methods = (
            "mle",
            "pseudo_mle",
            "numerical_mle",
            "parametric_bootstrap",
            "non_parametric_bootstrap",
        )
        if method in ["mle", "pseudo_mle"]:
            self._compute_mle(f=f_mle, observations=observations, delta=delta)
        elif method == "numerical_mle":
            self._compute_mle(
                f=self._maximize_log_likelihood,
                observations=observations,
                delta=delta,
                starting_value=starting_value,
                n_trials=n_trials,
                n_jobs=n_jobs,
            )
        elif method == "parametric_bootstrap":
            self._compute_parametric_bootstrap(
                f=f_mle,
                observations=observations,
                delta=delta,
                n_boot_resamples=n_boot_resamples,
                n_jobs=n_jobs,
            )
        elif method == "non_parametric_bootstrap":
            self._compute_nonparametric_bootstrap(
                f=f_mle,
                observations=observations,
                delta=delta,
                n_boot_resamples=n_boot_resamples,
                n_jobs=n_jobs,
            )
        else:
            raise TypeError(
                f"not valid choice for `method`. "
                f"Available methods are {available_methods}."
            )

    @staticmethod
    def _validate_observations(observations: Any) -> pd.DataFrame:
        """
        Validate the observations input

        Args:
            observations: input data

        Returns:
            output data

        """
        if isinstance(observations, (np.ndarray, list, dict)):
            observations = pd.DataFrame(observations)
        elif isinstance(observations, pl.DataFrame):
            observations = observations.to_pandas()
        elif isinstance(observations, pd.Series):
            observations = observations.to_frame()

        if not isinstance(observations, pd.DataFrame):
            raise TypeError("`observations` is a pd.DataFrame-like object")

        if observations.empty:
            raise ValueError("`observations` is a non-empty pd.DataFrame")

        if observations.isna().any().any():
            raise ValueError("`observations` cannot contain NaN")

        return observations

    def copy(self) -> Self:
        """
        Create a deep-copy of the object

        Returns:
            A deep-copy of the stochastic processes class

        """
        return deepcopy(self)


if __name__ == "__main__":
    pass
