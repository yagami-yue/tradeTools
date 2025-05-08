# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: config
@datetime: 2025/5/8 14:01
"""
import os


class MDFileCfg:
    STOCK_SNAP_PATH = "/tmp/data/selectedData/securities/parquet/snapshot/stable/{date}"
    STOCK_TRANS_PATH = "/tmp/data/selectedData/securities/parquet/transaction/stable/{date}"

    ETF_SNAP_PATH = "/tmp/data/selectedData/etf/parquet/snapshot/stable/{date}"
    ETF_TRANS_PATH = "/tmp/data/selectedData/etf/parquet/transaction/stable/{date}"

    CB_SNAP_PATH = "/tmp/data/selectedData/convertible_bond/parquet/snapshot/stable/{date}"
    CB_TRANS_PATH = "/tmp/data/selectedData/convertible_bond/parquet/transaction/stable/{date}"

    RAW_STOCK_SNAP_PATH = ""
    RAW_STOCK_TRANS_PATH = ""

    RAW_ETF_SNAP_PATH = ""
    RAW_ETF_TRANS_PATH = ""

    RAW_CB_SNAP_PATH = ""
    RAW_CB_TRANS_PATH = ""

    DAILY_FILE_PATH = ""
    MICRO_FILE_PATH = ""
    PREFILE_PATH = ""

    MICRO_FILE_ENCRYPT = False


class PrefilePath:
    ROOT = ""

    @classmethod
    def preinfo(cls):
        return os.path.join(cls.ROOT, "algo_prefile", "preinfo.csv")

    @classmethod
    def universe(cls):
        return os.path.join(cls.ROOT, "algo_prefile", "universe.csv")

    @classmethod
    def stats_history(cls):
        return os.path.join(cls.ROOT, "eodinfos", "stats_history.csv")
