from pydantic import BaseModel, Field
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Tuple
from .optioninputs import OptionInputs


class BlackScholesOptionPricing:
    """
    Class for Black-Scholes Option Pricing

    Parameters
    ----------
    inputs : OptionInputs
        Option inputs parameters

    Returns
    -------
    attributes: float
        call_price, put_price

        call_delta, put_delta 

        gamma 
        
        vega
        
        call_theta, put_theta

        call_rho, put_rho
        
        impvol
    """
    
    def __init__(self, inputs: OptionInputs) -> None:
        self.inputs = inputs
        self._a_ = self.inputs.volatility * np.sqrt(self.inputs.ttm)
        
        self._d1_ = (np.log(self.inputs.spot / self.inputs.strike) +
                     (self.inputs.rate + (self.inputs.volatility**2) / 2) * self.inputs.ttm) / self._a_
        
        self._d2_ = self._d1_ - self._a_
        self._b_ = np.exp(-self.inputs.rate * self.inputs.ttm)
        
        self.call_price, self.put_price = self._price()
        self.call_delta, self.put_delta = self._delta()
        self.gamma = self._gamma()
        self.vega = self._vega()
        self.call_theta, self.put_theta = self._theta()
        self.call_rho, self.put_rho = self._rho()
        self.impvol = self._impvol()        

    def _price(self) -> Tuple[float, float]:
        """
        Calculate option prices: Call price and Put price

        Returns
        -------
        Tuple[float, float]
            Call price and Put price
        """
        call = self.inputs.spot * norm.cdf(self._d1_) - self.inputs.strike * self._b_ * norm.cdf(self._d2_)
        put = self.inputs.strike * self._b_ * norm.cdf(-self._d2_) - self.inputs.spot * norm.cdf(-self._d1_)
        return call, put

    def _delta(self) -> Tuple[float, float]:
        """
        Calculate option deltas: Call delta and Put delta

        Returns
        -------
        Tuple[float, float]
            Call delta and Put delta
        """
        call = norm.cdf(self._d1_)
        put = -norm.cdf(-self._d1_)
        return call, put

    def _gamma(self) -> float:
        """
        Calculate option gamma

        Returns
        -------
        float
            Gamma
        """
        return norm.pdf(self._d1_) / (self.inputs.spot * self._a_)

    def _vega(self) -> float:
        """
        Calculate option vega

        Returns
        -------
        float
            Vega
        """
        return self.inputs.spot * norm.pdf(self._d1_) * np.sqrt(self.inputs.ttm) / 100

    def _theta(self) -> Tuple[float, float]:
        """
        Calculate option thetas: Call theta and Put theta

        Returns
        -------
        Tuple[float, float]
            Call theta and Put theta
        """
        call = -self.inputs.spot * norm.pdf(self._d1_) * self.inputs.volatility / (2 * np.sqrt(self.inputs.ttm)) - \
               self.inputs.rate * self.inputs.strike * self._b_ * norm.cdf(self._d2_)

        put = -self.inputs.spot * norm.pdf(self._d1_) * self.inputs.volatility / (2 * np.sqrt(self.inputs.ttm)) + \
               self.inputs.rate * self.inputs.strike * self._b_ * norm.cdf(-self._d2_)
        return call / 365, put / 365

    def _rho(self) -> Tuple[float, float]:
        """
        Calculate option rhos: Call rho and Put rho

        Returns
        -------
        Tuple[float, float]
            Call rho and Put rho
        """
        call = self.inputs.strike * self.inputs.ttm * self._b_ * norm.cdf(self._d2_) / 100
        put = -self.inputs.strike * self.inputs.ttm * self._b_ * norm.cdf(-self._d2_) / 100
        return call, put
    
    def _impvol(self) -> float:
        """
        Calculate option implied volatility

        Returns
        -------
        float
            Implied volatility
        """
        if self.inputs.callprice is None and self.inputs.putprice is None:
            return self.inputs.volatility
        else:
            def f(sigma: float) -> float:
                option = BlackScholesOptionPricing(OptionInputs(spot=self.inputs.spot, strike=self.inputs.strike, rate=self.inputs.rate, ttm=self.inputs.ttm, volatility=sigma))
                if self.inputs.callprice is not None:
                     model_call_price = option.call_price 
                     return model_call_price  - self.inputs.callprice 
                else:
                    model_put_price = option.put_price
                    return model_put_price - self.inputs.putprice
            try:
                implied_vol = brentq(f, a=1e-5, b=5.0, xtol=1e-8, rtol=1e-8, maxiter=100)
                implied_vol = max(implied_vol, 1e-5)
            except ValueError:
                implied_vol = np.nan
            return implied_vol        
