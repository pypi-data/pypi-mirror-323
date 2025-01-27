import numpy as np
from pydantic import BaseModel, Field
from typing import Optional,Tuple
from .optioninputs import OptionInputs

# Monte Carlo Option Pricing Engine
class MonteCarloOptionPricing:
    """
    Class for Monte Carlo Option Pricing

    Parameters
    ----------
    inputs : OptionInputs
        Option inputs parameters
    initialspot : float, optional
        Initial stock price
    nsims : int, optional
        Number of simulations
    timestep : int, optional
        Timestep, by default 252
    barrier : float, optional
        Barrier, by default None
    rebate : int, optional
        Rebate, by default None

    Returns
    -------
    attributes: float
        call_vanilla, put_vanilla

        call_asian, put_asian

        upandoutcall
    """
    
    def __init__(self, 
                 inputs: OptionInputs, 
                 initialspot: float = Field(..., gt=0, description="Initial stock price"), 
                 nsims: int = Field(..., gt=0, description="Number of simulations"), 
                 timestep: int = 252, 
                 barrier: Optional[float] = None, 
                 rebate: Optional[int] = None
                 ) -> None:
        
        self.inputs = inputs
        self.initialspot = initialspot
        self.nsims = nsims
        self.timestep = timestep
        self.barrier = barrier
        self.rebate = rebate

        self.call_vanilla, self.put_vanilla = self._vanillaoption()
        self.call_asian, self.put_asian = self._asianoption()
        self.upandoutcall = self._upandoutcall()

    @property
    def _discount_factor(self) -> float:
        return np.exp(-self.inputs.rate * self.inputs.ttm)

    @property
    def _pseudorandomnumber(self) -> np.ndarray:
        return np.random.standard_normal(self.nsims)

    @property
    def _simulatepath(self) -> np.ndarray:
        """Simulate price path"""
        np.random.seed(2024)

        dt = self.inputs.ttm / self.timestep

        S = np.zeros((self.timestep, self.nsims))
        S[0] = self.initialspot

        for i in range(0, self.timestep-1):
            w = self._pseudorandomnumber
            S[i+1] = S[i] * (1 + self.inputs.rate*dt + self.inputs.volatility*np.sqrt(dt)*w)

        return S

    def _vanillaoption(self) -> Tuple[float, float]:
        """Calculate vanilla option payoff"""
        S = self._simulatepath

        vanilla_call = self._discount_factor * np.mean(np.maximum(0, S[-1] -  self.inputs.strike))
        vanilla_put = self._discount_factor * np.mean(np.maximum(0,  self.inputs.strike - S[-1]))

        return [vanilla_call, vanilla_put]

    def _asianoption(self) -> Tuple[float]:
        """Calculate asian option payoff"""
        S = self._simulatepath

        A = S.mean(axis=0)

        asian_call = self._discount_factor * np.mean(np.maximum(0, A -  self.inputs.strike))
        asian_put = self._discount_factor * np.mean(np.maximum(0,  self.inputs.strike - A))

        return [asian_call, asian_put]

    def _upandoutcall(self) ->  float:
        """Calculate up-and-out barrier call option payoff"""
        S = self._simulatepath

        # Barrier shift
        barriershift = self.barrier * np.exp(0.5826 * self.inputs.volatility * np.sqrt(self.inputs.ttm/self.timestep))

        value = 0
        for i in range(self.nsims):
            if S[:,i].max () < barriershift:
                value += np.maximum(0, S[-1,i] -  self.inputs.strike)
            else:
                value += self.rebate

        return self._discount_factor * value / self.nsims
    