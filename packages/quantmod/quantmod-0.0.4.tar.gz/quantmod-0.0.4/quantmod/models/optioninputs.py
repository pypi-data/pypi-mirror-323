from pydantic import BaseModel, Field
from typing import Optional

class OptionInputs(BaseModel):
    """
    Option inputs parameters

    Parameters
    ----------
    spot : float
        Spot price of the underlying asset
    strike : float
        Strike price of the option
    rate : float
        Risk-free interest rate
    ttm : float
        Time to maturity in years
    volatility : float
        Volatility of the underlying asset
    callprice : float | None
        Default is None
        Market price of the call option
    putprice : float | None
        Default is None
        Market price of the put option
    
    Returns
    -------
    OptionInputs
        Option inputs parameters
    
    Raises
    ------
    ValueError
        If any of the input parameters are invalid
    """

    spot: float = Field(..., gt=0, description="Spot price of the underlying asset")
    strike: float = Field(..., gt=0, description="Strike price of the option")
    rate: float = Field(..., gt=0, le=1, description="Risk-free interest rate")
    ttm: float = Field(..., gt=0, description="Time to maturity in years")
    volatility: float = Field(..., gt=0, description="Volatility of the underlying asset")
    callprice: Optional[float] = Field(default=None, ge=0, description="Market price of the call option")
    putprice: Optional[float] = Field(default=None, ge=0, description="Market price of the put option")