import functools
import pandas as pd
import yfinance as yf
import numpy as np
from warnings import warn
from loguru import logger as log


def rolling_return(
    s: pd.Series, years: int = 5, snap_to_closest: bool = False
) -> pd.Series:
    """
    Returns a timeseries representing the simple return over 'years'.
    If 'snap_to_closest' is True, then we will snap to the last known value
    prior to (current_date - years). If False, we use the direct freq-based
    pct_change, which may yield NaNs if exact dates don't line up.
    """
    # Basic sanity checks
    assert isinstance(s.index, pd.DatetimeIndex), (
        f"The index of the Series must be a DatetimeIndex, got: {type(s.index)}"
    )
    assert s.index.is_monotonic_increasing, (
        "The index of the Series must be sorted in increasing order"
    )

    # Forward-fill to avoid NaNs *inside* existing date ranges
    s_filled = s.ffill(limit_area="inside")
    offset = pd.DateOffset(years=years)

    # If NOT snapping, use the built-in freq-based approach
    if not snap_to_closest:
        simple_return = s_filled.pct_change(freq=offset, fill_method=None).add(1)
        return simple_return

    # Otherwise, do the "snap to last known prior date" logic in a vectorized way
    idx = s_filled.index  # sorted, monotonic DatetimeIndex
    vals = s_filled.values  # the underlying float array

    # For each date t, we want the index of t - offset
    target_dates = idx - offset  # array of "target" Datetime values
    # searchsorted(..., side='right') gives us the insertion position
    # subtract 1 to get the largest index <= target_dates[i]
    # i_lookups[i] = j means that idx[j] <= target_dates[i] < idx[j+1]
    i_lookups = np.searchsorted(idx, target_dates, side="right") - 1

    # Build an array for old values; if i_lookups < 0 => no older date => NaN
    old_vals = np.full_like(vals, np.nan, dtype=float)
    valid_mask = i_lookups >= 0
    old_vals[valid_mask] = vals[i_lookups[valid_mask]]

    # Compute ratio s(t) / s(t - offset)
    # If old_vals is NaN, ratio is automatically NaN
    ratio = vals / old_vals

    # Build the final Series|DataFrame
    if isinstance(s, pd.DataFrame):
        return pd.DataFrame(ratio, index=idx, columns=s.columns)

    return pd.Series(ratio, index=idx, name=s_filled.name)


def rolling_cagr(s: pd.DataFrame | pd.Series, years=5, snap_to_closest=False):
    # Basic sanity checks
    assert isinstance(s.index, pd.DatetimeIndex), (
        f"The index of the Series must be a DatetimeIndex, got: {type(s.index)}"
    )
    assert s.index.is_monotonic_increasing, (
        "The index of the Series must be sorted in increasing order"
    )

    if (s.index[-1] - s.index[0]).days < 365:
        warn("Less than 1 year of data. Returning NaNs")
        return pd.Series(index=s.index, data=np.nan)

    simple_return = rolling_return(s, years=years, snap_to_closest=snap_to_closest)
    return (simple_return ** (1 / years)) - 1


@functools.cache
def download_ccy_pair(ccy_from, ccy_to="USD", start=None, end=None):
    ccy_pair = f"{ccy_from}{ccy_to}=X"
    log.debug(f"Downloading currency pair {ccy_pair}")
    df = yf.download(ccy_pair, start=start, end=end)
    return df


def normalize_currencies(df: pd.DataFrame, to="USD"):
    # TODO
    pass


def to_usd(df, ccy_df=None, from_ccy="INR"):
    start_date = df.index[0]
    end_date = df.index[-1]
    if ccy_df is None:
        ccy_df = yf.download(f"{from_ccy}USD=X", start=start_date, end=end_date)[
            "Close"
        ]
    # TODO: Mask the Volume column if present
    return df.mul(ccy_df, axis=0)


def drawdowns(data: pd.DataFrame | pd.Series):
    """
    Calculate the drawdowns of a time series.
    """
    return (data / data.cummax()) - 1


def remove_tz(df):
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df
