"""
This module contains functions to perform
sensor-specific calculations such as conversion between units,
computation of absolute moisture from relative moisture, conversion
between molar and mass concentrations and similar operations.
It also includes some useful constants

-> Initial source: Simone Bafelli <sensorutils>
Refactored by Patrick Aigner
"""

from typing import Final
import numpy as np

T0: Final = 273.15  # T0: float = The 0 C temperature in K
TC: Final = 647.096  # TC: float = The critical point temperature of water
PC: Final = 22.064e6  # PC: float = The critical point pressure of water
P0: Final = 1013.25e2  # P0: float = Reference pressure at sea level


def absolute_temperature(t: float) -> float:
    """
    Computes the absolute temperature in K from a given temperature in C.

    t: float = Temperature in C

    Returns:
    float = Temperature in K
    """
    return t + T0


def saturation_vapor_pressure(t: float) -> float:
    """
    Compute saturation vapor pressure of water (in pascal) at given absolute temperature.

    t: float = Temperature in K

    Returns:
    float = Saturation Vapor Pressure of water in Pa
    """
    coef_1 = -7.85951783
    coef_2 = 1.84408259
    coef_3 = -11.7866497
    coef_4 = 22.6807411
    coef_5 = -15.9618719
    coef_6 = 1.80122502
    theta = 1 - t / TC
    pw = (np.exp(
        TC / t *
        (coef_1 * theta + coef_2 * theta**1.5 + coef_3 * theta**3 +
         coef_4 * theta**3.5 + coef_5 * theta**4 + coef_6 * theta**7.5)) * PC)
    return float(pw)


def rh_to_ah(rh: float, t: float) -> float:
    """
    Conver relative to absolute humidity (in g/m^3) given temperature and pressure.

    rh: float = Relative humidity in %
    pressure: float = Pressure in Pa

    Returns:
    float = Absolute Humidity in g/m^3
    """
    pw = saturation_vapor_pressure(t)
    c = 2.16679
    return c * pw / t * rh / 100


def rh_to_molar_mixing(rh: float, t: float, p: float) -> float:
    """
    Convert the give relative humidity (in 100%) to a molar mixing ratio (kg/kg).

    rh: float = The relative humidity in %
    t: float = The absolute temperature in K
    p: float = Pressure in Pa

    Returns:
    float = Water vapor molar mixing ratio in kg/kg
    """
    return saturation_vapor_pressure(t) * rh / 100 / p


def calculate_co2dry(co2wet: float, temperature: float, rh: float,
                     pressure: float) -> float:
    """
    Convert CO2 wet concentration to dry concentration in ppm.

    co2wet float: CO2 wet in ppm
    temperature float: Temperature in °C
    humidity float: The relative humidity in %
    p float: Pressure in Pa

    Returns:
    float: CO2 dry in ppm
    """
    xh2o = rh_to_molar_mixing(rh=rh,
                              t=absolute_temperature(temperature),
                              p=pressure)
    return co2wet / (1 - xh2o)
