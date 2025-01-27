import pandas as pd
import numpy as np
from scipy import stats
from arch import arch_model
from .riskinputs import RiskInputs
from typing import Literal


class ValueAtRisk:
    """
    Class to calculate Value at Risk (VaR) based on returns and confidence level

    Parameters
    ----------
    inputs : RiskInputs
        An instance of Risk inputs containing returns and confidence level
    method : Literal['historical', 'parametric', 'montecarlo']
        The method to calculate VaR, by default 'historical'

    Returns
    -------
    attributes: float
        var
    """

    def __init__(self, inputs: RiskInputs, method: Literal['historical', 'parametric', 'montecarlo']) -> float:
        self.inputs = inputs
        self.returns = pd.Series(inputs.returns)
        self.method = method
        self.mean = np.mean(self.returns)
        self.std = np.std(self.returns)
        self.var = self._var()
        
    def _pvar(self) -> float:
        """
        Calculate the Value at Risk (VaR) at the specified confidence level using variance - covariance approach
        """
        # return (self.mean + stats.norm.ppf(1-self.inputs.confidence_level) * self.std)
        return np.round(stats.norm.ppf(1-self.inputs.confidence_level, self.mean, self.std),4)

    def _hvar(self) -> float:
        """
        Calculate the Value at Risk (VaR) at the specified confidence level using historical returns
        """
        return np.round(np.percentile(self.returns, (1 - self.inputs.confidence_level) * 100),4)

    def _mcvar(self) -> float:
        """
        Calculate the Value at Risk (VaR) at the specified confidence level using Monte Carlo simulation
        """
        simulated_returns = stats.norm.rvs(loc=self.mean, scale=self.std, size=5000)
        return np.round(np.percentile(simulated_returns, (1 - self.inputs.confidence_level) * 100),4)

    # def _garchvar(self) -> float:
    #     """
    #     Calculate the Value at Risk (VaR) at the specified confidence level using GARCH model
    #     """
    #     model = arch_model(self.returns*1000, vol='GARCH', p=1, q=1, dist="gaussian")
    #     fitted_model = model.fit(disp="off")
    #     conditional_volatilities = fitted_model.conditional_volatility
    #     return (stats.norm.ppf(1-self.inputs.confidence_level) * conditional_volatilities.iloc[-1]) / 1000


    def _var(self) -> float:
        if self.method == 'parametric':
            return self._pvar()
        elif self.method == 'historical':
            return self._hvar()
        elif self.method == 'montecarlo':
            return self._mcvar()
        # elif self.method == 'garch':
        #     return self._garchvar()
        else:
            raise ValueError("Invalid method")


class ConditionalVaR:
    """
    Class to calculate Conditional Value at Risk (CVaR) aka Expected Shortfall (ES) based on historical returns and confidence level

    Parameters
    ----------
    inputs : RiskInputs
        An instance of Risk inputs containing returns and confidence level

    Returns
    -------
    attributes: float
        CVaR
    """

    def __init__(self, inputs: RiskInputs) -> float:       
        self.inputs = inputs
        self.returns = pd.Series(inputs.returns)
        self.cvar = self._cvar()

    def _cvar(self) -> float:
        """
        Calculate the Conditional Value at Risk (CVaR) at the specified confidence level
        """
        var = np.percentile(self.returns, (1 - self.inputs.confidence_level) * 100)
        tail_returns = self.returns[self.returns <= var]
        return np.round(tail_returns.mean() if len(tail_returns) > 0 else float('nan'),4)
