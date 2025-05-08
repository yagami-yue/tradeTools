# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: base
@datetime: 2025/5/8 9:46
"""
s = 1_000_000  # base on us

bps = 10000
pct = 100


class MarketTime:
    CONTINUES_START = 9_30_00 * s
    CONTINUES_END = 14_57_00 * s
    NOON = 12_00_00 * s
    MORNING_END = 11_30_00 * s
    AFTERNOON_START = 13_00_00 * s
    OPEN_AUCTION_END = 9_25_00 * s
    CLOSE_AUCTION_END = 15_00_00 * s
