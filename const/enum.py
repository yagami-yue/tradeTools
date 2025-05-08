# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: enum
@datetime: 2025/5/6 13:35
"""
from enum import Enum, IntEnum
from datetime import datetime

# 时间单位因子
s = 1


class ETime(Enum):
    """时间转换工具类"""

    @classmethod
    def dump(cls, value: int) -> str:
        return datetime.fromtimestamp(value / s).strftime("%Y%m%d %H:%M:%S")

    @classmethod
    def load(cls, text: str) -> int:
        return int(datetime.strptime(text, "%Y%m%d %H:%M:%S").timestamp() * s)

    @classmethod
    def show(cls, value: int) -> str:
        return cls.dump(value)


class StringEnum(str, Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class VIntEnum(IntEnum):
    def __str__(self) -> str:
        return str(self.value)


class StockCluster(StringEnum):
    ULTRA_FAST = "UltraFast"
    SPARSE = "Sparse"
    SLOW = "Slow"
    NORMAL = "Normal"
    FAST = "Fast"

    @classmethod
    def list(cls):
        return [item.value for item in cls]

    @classmethod
    def from_str(cls, value: str):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"{value} is not a valid {cls.__name__}")


class StockLabel(StringEnum):
    ULTRA_FAST_0 = "UltraFast_0"
    SPARSE_0 = "Sparse_0"
    SLOW_0 = "Slow_0"
    SLOW_1 = "Slow_1"
    SLOW_2 = "Slow_2"
    NORMAL_0 = "Normal_0"
    NORMAL_1 = "Normal_1"
    FAST_0 = "Fast_0"
    FAST_1 = "Fast_1"

    @classmethod
    def list(cls):
        return [item.value for item in cls]

    @classmethod
    def from_str(cls, value: str):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"{value} is not a valid {cls.__name__}")


class TaskStatus(VIntEnum):
    ERROR = 0
    NEW = 1
    PART_FILLED = 2
    CANCELLING = 3
    RUNNING = 4
    REJECTED = 10
    FILLED = 11
    CANCELLED = 12
    EXPIRED = 13


class Side(VIntEnum):
    BUY = 1
    SELL = -1


Direction = Side


class Offset(VIntEnum):
    OPEN = 0
    CLOSE = 1


class IsYd(VIntEnum):
    YD = 1
    TD = 0


class TradeType(VIntEnum):
    NORMAL_BUY = 1
    NORMAL_SELL = 2
    COLLATERAL_BUY = 3  # 担保品买
    COLLATERAL_SELL = 4  # 担保品卖

    BUY_TO_COVER = 5  # 买券还券
    SELL_TO_SHORT = 6  # 融券卖出
    MARGIN_BUY = 7  # 融资买入
    SELL_TO_REPAY = 8  # 卖券还款


class TaskTag(VIntEnum):
    ALGO = 0
    INC_OR_DEC = 1  # 增持减持
    LENDING = 2  # 两融市值建仓
    T0 = 3  # T0交易


class RawEventStatus(VIntEnum):
    UNKNOWN = -1
    INSERTING = 10
    INSERTED = 20
    INSERTFAILED = 25
    TRADED = 30
    TRADEDPARTIAL = 31
    CANCELLING = 40
    CANCELLFAILED = 45
    CANCELLED = 50
    CANCELLEDPARTIAL = 55
    REJECTED = 70
    FSMERR = 80
    BYPASS = 100


class EventStatusSet:
    closed_status = {RawEventStatus.CANCELLED, RawEventStatus.TRADED, RawEventStatus.TRADEDPARTIAL,
                     RawEventStatus.INSERTED}
    trade_status = {RawEventStatus.TRADED, RawEventStatus.TRADEDPARTIAL}
    cancel_status = {RawEventStatus.CANCELLED, RawEventStatus.CANCELLING, RawEventStatus.CANCELLFAILED,
                     RawEventStatus.CANCELLEDPARTIAL}
    insert_status = {RawEventStatus.INSERTING, RawEventStatus.INSERTED}
    order_closed_status = {RawEventStatus.CANCELLED, RawEventStatus.TRADED}
    valid_status = {
        RawEventStatus.INSERTED,
        RawEventStatus.INSERTING,
        RawEventStatus.CANCELLED,
        RawEventStatus.CANCELLING,
        RawEventStatus.CANCELLFAILED,
        RawEventStatus.CANCELLEDPARTIAL,
        RawEventStatus.UNKNOWN,
        RawEventStatus.TRADED,
        RawEventStatus.TRADEDPARTIAL
    }


if __name__ == '__main__':
    print(ETime.dump(1714280640))  # 时间戳转字符串
    print(ETime.load("20250428 14:24:00"))  # 字符串转时间戳

    print(StockCluster.list())  # 列出所有 cluster
    print(StockLabel.from_str("Slow_2"))  # 获取枚举项
    print(StockLabel.FAST_0.value)
