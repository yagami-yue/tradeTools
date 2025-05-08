# -*- coding: UTF-8 -*-
"""
@author: wzc
@file: time_utils
"""
from time_tools.trade_calendar import get_stock_calendar

calendar = get_stock_calendar()


def stoe(s):
    return calendar.stoe(s)


def etom(e):
    return int(calendar.etos(e)[-8:].replace(":", "")) * 1000_000


def mtoe(m, date):
    return stoe(f"{date} {str(m // 1000_000).rjust(6, '0')}")


def stom(s):
    return int(s[-8:].replace(":", "")) * 1000_000


def mtos(m, date):
    return f"{date} {str(m // 1000_000).rjust(6, '0')}"


def mtoi(m):
    return calendar.mtoi(m)


def itom(i):
    return calendar.itom(i)


if __name__ == '__main__':
    time_str = "20231030 09:30:00"
    print(stoe(time_str))
