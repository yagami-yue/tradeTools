# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: make_daily_data
@datetime: 2022/9/1 16:14
"""
import datetime
import os

from loguru import logger
import pandas as pd
from common.config import (
    MDFileCfg,
    PrefilePath
)
from common.base import MarketTime
from common.datacenter import Datacenter
from common.utils import (
    format_string,
    fillna
)

HIGH_LIMIT = 2 ** 32


def read_snap(date):
    return Datacenter.fetch_snaps(date=date)

def clear_snap(snap):
    # 午间休市
    snap = snap[~((MarketTime.MORNING_END < snap["time"])
               & (snap["time"] < MarketTime.AFTERNOON_START))]
    # 去除竞价
    snap = snap[(snap["time"] >= MarketTime.CONTINUES_START) & (snap["time"] < MarketTime.CONTINUES_END)]
    return snap

def align(value):
    return round(value * 10000)

def process_one_code(date, code, snap, preinfo):
    pre_close = 0
    high_limit_price = -1
    low_limit_price = -1
    limit = 0

    mic = {".SZ": "XSHE", ".SH": "XSHG"}.get(code[6:])
    continues_ticks = clear_snap(snap)
    stopped_ticks = continues_ticks[
        ((continues_ticks["bid1"] == 0) | (continues_ticks["ask1"] == 0)) &
        ((continues_ticks["bid1"] == continues_ticks["high"]) | (continues_ticks["ask1"] == continues_ticks["low"]))]
    if not stopped_ticks.empty:
        limit = 1
    try:
        code_preinfo = preinfo[(preinfo["InstrumentId"] == code[0:6]) & (preinfo["MIC"] == mic)].iloc[0]
        if round(float(code_preinfo["PreClose"])) < HIGH_LIMIT:
            pre_close = round(float(code_preinfo["PreClose"]) * 1e4)
    except IndexError:
        # logger.warning("code: {} not exists in preinfo".format(code))
        return None
    snap = snap[(snap["time"] >= MarketTime.CONTINUES_START)]
    last_df = snap[(snap["time"] > MarketTime.CLOSE_AUCTION_END)]
    low_df = snap[
        (snap["time"] < MarketTime.CONTINUES_END) | (
                (snap["time"] > MarketTime.CLOSE_AUCTION_END) & (snap["time"] < MarketTime.CLOSE_AUCTION_END + 10_00_000_000)
        )
    ]
    low_df = low_df[(low_df["low"] > 0)]

    mic = snap["MIC"].iloc[0]
    open_price = align(snap["open"].mode().loc[0])

    if last_df.empty:
        close = align(low_df.sort_values(by="time")["last"].iloc[-1])
    else:
        close = align(last_df["last"].iloc[0])
    high = align(fillna(snap["high"].max(), 0))
    low = align(fillna(low_df["low"].min(), 0))
    amount = fillna(snap["cumamount"].max(), 0)
    volume = fillna(snap["cumvol"].max(), 0)

    result = [date, code, mic, open_price, close, pre_close, high, low, limit,
              high_limit_price, low_limit_price, amount, volume]
    return result


def make_daily(date, overwrite=False):
    columns_index = ["date", "code", "mic", "open", "close", "pre_close", "high",
                     "low", "limit", "high_limit", "low_limit", "amount", "volume"]
    preinfo_path = format_string(PrefilePath.preinfo, date=date)
    pre_info = pd.read_csv(preinfo_path, dtype=str)
    target_path = format_string(MDFileCfg.DAILY_FILE_PATH, date=date)
    daily_file_path = os.path.join(target_path, f"{date}.csv")
    os.makedirs(target_path, exist_ok=True)
    # 完成
    if os.path.exists(daily_file_path):
        if overwrite:
            logger.info("{} daily already finish, overwrite daily csv".format(date))
        else:
            logger.info("{} daily already finish, make daily finish".format(date))
            return

    all_day_snap = read_snap(date)
    # all_day_snap = all_day_snap.groupby("wid")

    start_time = datetime.datetime.now()
    logger.info("make daily start time: {}".format(start_time))

    daily_data_list = []
    for code, snap in all_day_snap.items():
        try:
            daily_data = process_one_code(date, code, snap, pre_info)
        except Exception as e:
            logger.error("process code: {}, raise error: {}".format(code, e))
            continue
        if daily_data:
            daily_data_list.append(daily_data)
    end_time = datetime.datetime.now()

    logger.info("all stock code(num: {}) make daily success".format(len(daily_data_list)))
    pd.DataFrame(daily_data_list, columns=columns_index).to_csv(daily_file_path, index=False)
    logger.info("daily data write to {}".format(daily_file_path))
    logger.info("cost time:{}".format(end_time - start_time))
    logger.info("make daily finish")
