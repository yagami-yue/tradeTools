# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: tick_trans
"""
import os

import pandas as pd
from loguru import logger

from common.config import MDFileCfg
from common.utils import (
    SymbolType,
    DataType, format_string
)
from common.base import s
from concurrent.futures import ThreadPoolExecutor


origin_data_source_format = {
    "folder_fmt": "yyyymmdd",
    "file_type": "csv",
    "header": True,
    "delimiter": ",",
    "columns": [
        "code", "trdTime", "recvTime", "highLimit", "lowLimit",
        "open", "last", "high", "low",
        "cumCnt", "cumVol", "turnover",
        "askPrc1", "askVol1", "bidPrc1", "bidVol1", "askPrc2", "askVol2", "bidPrc2", "bidVol2",
        "askPrc3", "askVol3", "bidPrc3", "bidVol3", "askPrc4", "askVol4", "bidPrc4", "bidVol4",
        "askPrc5", "askVol5", "bidPrc5", "bidVol5", "askPrc6", "askVol6", "bidPrc6", "bidVol6",
        "askPrc7", "askVol7", "bidPrc7", "bidVol7", "askPrc8", "askVol8", "bidPrc8", "bidVol8",
        "askPrc9", "askVol9", "bidPrc9", "bidVol9", "askPrc10", "askVol10", "bidPrc10", "bidVol10"
    ],
    "dtype": {'code': 'str', 'trdTime': 'int64', 'recvTime': 'int64',
              'highLimit': 'int32', 'lowLimit': 'int32', 'open': 'int32',
              'last': 'int32', 'high': 'int32', 'low': 'int32', 'cumCnt': 'int32',
              'cumVol': 'int32', 'turnover': 'int64', 'askPrc1': 'int32',
              'askVol1': 'int32', 'bidPrc1': 'int32', 'bidVol1': 'int32',
              'askPrc2': 'int32', 'askVol2': 'int32', 'bidPrc2': 'int32',
              'bidVol2': 'int32', 'askPrc3': 'int32', 'askVol3': 'int32',
              'bidPrc3': 'int32', 'bidVol3': 'int32', 'askPrc4': 'int32',
              'askVol4': 'int32', 'bidPrc4': 'int32', 'bidVol4': 'int32',
              'askPrc5': 'int32', 'askVol5': 'int32', 'bidPrc5': 'int32',
              'bidVol5': 'int32', 'askPrc6': 'int32', 'askVol6': 'int32',
              'bidPrc6': 'int32', 'bidVol6': 'int32', 'askPrc7': 'int32',
              'askVol7': 'int32', 'bidPrc7': 'int32', 'bidVol7': 'int32',
              'askPrc8': 'int32', 'askVol8': 'int32', 'bidPrc8': 'int32',
              'bidVol8': 'int32', 'askPrc9': 'int32', 'askVol9': 'int32',
              'bidPrc9': 'int32', 'bidVol9': 'int32', 'askPrc10': 'int32',
              'askVol10': 'int32', 'bidPrc10': 'int32', 'bidVol10': 'int32'}
}

result_data_source_format = {
    "header": [
        "tradingDay", "tradeTime", "recvTime", "code", "MIC",
        "cumCnt", "cumVol", "turnover",
        "last", "open", "high", "low",
        "bp1", "bv1", "ap1", "av1",
        "bp2", "bv2", "ap2", "av2",
        "bp3", "bv3", "ap3", "av3",
        "bp4", "bv4", "ap4", "av4",
        "bp5", "bv5", "ap5", "av5",
        "bp6", "bv6", "ap6", "av6",
        "bp7", "bv7", "ap7", "av7",
        "bp8", "bv8", "ap8", "av8",
        "bp9", "bv9", "ap9", "av9",
        "bp10", "bv10", "ap10", "av10"
    ],
    "dtype": {
        "tradingDay": "int32",
        "tradeTime": "int64",
        "recvTime": "int64",
        "code": "str",
        "MIC": "str",
        "cumCnt": "int32",
        "cumVol": "int32",
        "turnover": "int64",
        "last": "int32",
        "open": "int32",
        "high": "int32",
        "low": "int32",
        "bp1": "int32", "bv1": "int32", "ap1": "int32", "av1": "int32",
        "bp2": "int32", "bv2": "int32", "ap2": "int32", "av2": "int32",
        "bp3": "int32", "bv3": "int32", "ap3": "int32", "av3": "int32",
        "bp4": "int32", "bv4": "int32", "ap4": "int32", "av4": "int32",
        "bp5": "int32", "bv5": "int32", "ap5": "int32", "av5": "int32",
        "bp6": "int32", "bv6": "int32", "ap6": "int32", "av6": "int32",
        "bp7": "int32", "bv7": "int32", "ap7": "int32", "av7": "int32",
        "bp8": "int32", "bv8": "int32", "ap8": "int32", "av8": "int32",
        "bp9": "int32", "bv9": "int32", "ap9": "int32", "av9": "int32",
        "bp10": "int32", "bv10": "int32", "ap10": "int32", "av10": "int32"
    }
}


def get_target_path(data_type, symbol_type, date):
    target_mapping = {
        (DataType.SNAP, SymbolType.STOCK): MDFileCfg.STOCK_SNAP_PATH,
        (DataType.SNAP, SymbolType.ETF): MDFileCfg.ETF_SNAP_PATH,
        (DataType.SNAP, SymbolType.CB): MDFileCfg.CB_SNAP_PATH,
        (DataType.TRANS, SymbolType.STOCK): MDFileCfg.STOCK_TRANS_PATH,
        (DataType.TRANS, SymbolType.ETF): MDFileCfg.ETF_TRANS_PATH,
        (DataType.TRANS, SymbolType.CB): MDFileCfg.CB_TRANS_PATH
    }
    if (data_type, symbol_type) not in target_mapping:
        raise ValueError(f"Can't support convert {data_type}, {symbol_type}")
    else:
        return format_string(target_mapping[(data_type, symbol_type)], date=date)


def get_source_path(data_type, symbol_type, date):
    source_mapping = {
        (DataType.SNAP, SymbolType.STOCK): MDFileCfg.RAW_STOCK_SNAP_PATH,
        (DataType.SNAP, SymbolType.ETF): MDFileCfg.RAW_ETF_SNAP_PATH,
        (DataType.SNAP, SymbolType.CB): MDFileCfg.RAW_CB_SNAP_PATH,
        (DataType.TRANS, SymbolType.STOCK): MDFileCfg.RAW_STOCK_TRANS_PATH,
        (DataType.TRANS, SymbolType.ETF): MDFileCfg.RAW_ETF_TRANS_PATH,
        (DataType.TRANS, SymbolType.CB): MDFileCfg.RAW_CB_TRANS_PATH
    }
    if (data_type, symbol_type) not in source_mapping:
        raise ValueError(f"Can't support convert {data_type}, {symbol_type}")
    else:
        return format_string(source_mapping[(data_type, symbol_type)], date=date)


def make_parquet(data_type, symbol_type, date: str, source_format,
                 overwrite: bool = False, parallel: int = None):
    target_path = get_target_path(data_type, symbol_type, date)
    target_file = os.path.join(target_path, f"{date}.parquet")
    source_path = get_source_path(data_type, symbol_type, date)

    if os.path.exists(target_file) and not overwrite:
        logger.warning("{} has exists, ignore".format(target_file))
        return None
    dtype = source_format.get("dtype", None)
    columns = source_format["columns"]

    source_file_paths = os.listdir(source_path)
    source_file_paths.sort()
    source_file_paths = [os.path.join(source_path, path) for path in source_file_paths]
    os.makedirs(target_path, exist_ok=True)

    logger.info(f"start loading {date}, {data_type}, {symbol_type}")

    result_df = load_file_by_once(source_file_paths, dtype=dtype, columns=columns, parallel=parallel)
    logger.info(f"all snaps shape is {result_df.shape}")
    logger.debug(f"dtypes of origin: {result_df.dtypes}")
    convert(
        dst_data=result_df,
        date=date
    )
    logger.info(f"all snaps shape after convert is {result_df.shape}")
    result_df.to_parquet(target_file)
    return result_df


def convert(dst_data: pd.DataFrame, date: str):
    """
    股票快照，5min_csv 转 归档格式
    """
    if len(dst_data) == 0:
        return pd.DataFrame(columns=origin_data_source_format["columns"])

    dst_data["tradingDay"] = date
    # 秒以下精度填充0
    dst_data["tradeTime"] = dst_data["trdTime"] * s

    # 新格式中MIC在code中 形式: XSHG002174
    # turnover 已经乘上 10000
    dst_data["MIC"] = dst_data["code"].astype("str").str[:4]
    dst_data["code"] = dst_data["code"].astype("str").str[4:]
    # dst_data["turnover"] = round(dst_data["turnover"] * 10000, 0)
    name_mapping = {
        "opnPrc": "open",
        "highPrc": "high",
        "lowPrc": "low"
    }
    for i in range(1, 11):
        name_mapping[f'bidPrc{i}'] = f"bp{i}"
        name_mapping[f'bidVol{i}'] = f"bv{i}"
        name_mapping[f'askPrc{i}'] = f"ap{i}"
        name_mapping[f'askVol{i}'] = f"av{i}"
    dst_data.rename(columns=name_mapping, inplace=True)
    # 股票无openInterest字段，填充-1

    dst_data.sort_values(["recvTime", "cumCnt"], inplace=True)
    raw_columns = dst_data.columns
    columns = result_data_source_format["header"]
    for col in raw_columns:
        if col not in columns:
            del dst_data[col]
    dst_data.index = range(len(dst_data))


def load_file_by_once(
        file_list,
        dtype=None,
        columns=None,
        parallel: int = 4
):
    def read_csv(file_name):
        return pd.read_csv(file_name, usecols=columns, dtype=dtype)

    with ThreadPoolExecutor(max_workers=parallel) as executor:
        results = list(executor.map(read_csv, file_list))

    return pd.concat(results, ignore_index=True)
