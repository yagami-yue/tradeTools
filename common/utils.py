# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: utils
"""

import pandas as pd
from numpy import isnan, isinf
from const.enum import StringEnum


class SymbolType(StringEnum):
    STOCK = "stock"
    ETF = "etf"
    CB = "cb"
    UNION = "union"


class DataType(StringEnum):
    TRANS = "trans"
    ORDER = "order"
    SNAP = "snap"
    UNITICK = "unitick"


def format_string(fstring, **kwargs):
    return fstring.format(**kwargs)


def calc_mid(ask, bid):
    ask_is_0 = ask == 0
    bid_is_0 = bid == 0
    return (ask * (1 + bid_is_0) + bid * (1 + ask_is_0)) / 2


def get_wavg_price(ticks):
    amount = sum(ticks[f"ask{i}vol"] * ticks[f"ask{i}"] + ticks[f"bid{i}vol"] * ticks[f"bid{i}"] for i in range(1, 11))
    vol = sum(ticks[f'ask{i}vol'] + ticks[f'bid{i}vol'] for i in range(1, 11))
    return amount / vol


def get_tick_periods(ticks):
    mid_change = ticks.mid.diff().abs()
    tick_periods = ticks.itime[mid_change != 0].diff()[1:]
    return tick_periods


def get_quote_size(ticks, s=1):
    return sum(ticks[f'ask{i}vol'] + ticks[f'bid{i}vol'] for i in range(1, s + 1)) / (2 * s)


def get_bookskew(ticks):
    return (ticks.wavg - ticks.mid) / ticks.mid


def get_tick_magnitude(ticks):
    mid_change = ticks.mid.diff().abs()
    return mid_change[1:][mid_change != 0]


def get_trade_periods(trans):
    trans_periods = trans[trans.type == 1].itime.diff()[1:]
    return trans_periods


def avg(series, default=None):
    if series.empty:
        return default
    else:
        return series.mean()


def fillna(value, default=None):
    if isnan(value):
        return default
    else:
        return value


def fixfloat(value, default=None):
    if isnan(value) or isinf(value):
        return default
    else:
        return value


def calc_cost(price, base_price, direction=1):
    price = price or 0
    return fillna((price / base_price - 1) * direction if base_price else 0, 0)


def find_by_time(df: pd.DataFrame, value, side: int = -1, include: bool = True):
    if df is None or df.empty:
        return None
    if side not in (-1, 1):
        raise ValueError("side must be -1 or 1")

    if side == -1:
        condition = df["time"] <= value if include else df["time"] < value
    else:
        condition = df["time"] >= value if include else df["time"] > value

    filtered = df[condition]

    if filtered.empty:
        return None

    return filtered.iloc[-1] if side == -1 else filtered.iloc[0]


def find_range_by_time(dataframe: [pd.DataFrame, None], start=None, end=None, includes: str = "None"):
    if dataframe is None or dataframe.empty:
        return None
    cond = None
    if start:
        if includes in {"left", "both"}:
            cond = dataframe.time >= start
        else:
            cond = dataframe.time > start
    if end:
        if includes in {"right", "both"}:
            cond = cond & (dataframe.time <= end) if cond is not None else dataframe.time <= end
        else:
            cond = cond & (dataframe.time < end) if cond is not None else dataframe.time < end
    return dataframe[cond].copy()
