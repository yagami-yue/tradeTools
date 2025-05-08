from typing import List
from time_tools.trade_calendar.utils import (
    mtime_delta,
    mtime_add,
    find
)
from dateutil import parser
import datetime


class Section:
    __slots__ = [
        "e0",
        "e1",
        "i0",
        "i1",
        "c0",
        "c1",
        "m0",
        "m1",
        "length"
    ]

    def __init__(self, tp0, tp1) -> None:
        self.length = tp1.e - tp0.e
        self.e0 = tp0.e
        self.e1 = tp1.e
        self.i0 = tp0.i
        self.i1 = tp1.i
        self.c0 = tp0.c
        self.c1 = tp1.c
        self.m0 = tp0.m
        self.m1 = tp1.m


def make_etoi(sections: List[Section]):
    epairs = []
    for section in sections:
        e0 = section.e0
        e1 = section.e1
        epairs.append((e0, e1))

    def etoi(e):
        i = 0
        for e0, e1 in epairs:
            if_in = (e >= e0) & (e < e1)
            if_after = (e >= e1)
            i += if_in * (e - e0) + if_after * (e1 - e0)
        return i

    return etoi


def make_itoe(sections: List[Section]):
    ipairs = []
    for section in sections:
        i0 = section.i0
        i1 = section.i1
        ipairs.append((i0, i1))

    def itoe(i):
        e = sections[0].e0
        for i0, i1 in ipairs:
            if_in = (i >= i0) & (i < i1)
            if_after = (i >= i1)
            e += if_in * (i - i0) + if_after * (i1 - i0)
        return e

    return itoe


def make_mtoi(sections: List[Section]):
    mpairs = []
    for section in sections:
        m0 = section.m0
        m1 = section.m1
        mpairs.append((m0, m1))

    def mtoi(m):
        i = sections[0].i0
        for m0, m1 in mpairs:
            if_in = (m >= m0) & (m < m1)
            if_after = (m >= m1)
            i += if_in * mtime_delta(m, m0) + if_after * mtime_delta(m1, m0)
        return i

    return mtoi


def make_itom(sections: List[Section]):
    ipairs = []
    for section in sections:
        i0 = section.i0
        i1 = section.i1
        ipairs.append((i0, i1))

    def itom(i):
        m = 0
        for section in sections:
            i0 = section.i0
            i1 = section.i1
            if_in = (i >= i0) & (i < i1)
            if_after = (i >= i1)
            m += if_in * mtime_add(section.m0, i - i0)
        m += if_after * section.m1
        return m

    return itom


class Sections:
    def __init__(self, date, sections, c0=0) -> None:
        self.date = date
        self.sections = sections
        self.e0s = [sec.e0 for sec in self.sections]
        self.i0s = [sec.i0 for sec in self.sections]
        self.c0s = [sec.c0 for sec in self.sections]
        self.c0 = c0
        self._etoi = make_etoi(self.sections)
        self._itoe = make_itoe(self.sections)
        self._itom = make_itom(self.sections)
        self._mtoi = make_mtoi(self.sections)

    def get_section(self, e=None, c=None, i=None):
        if e is not None:
            section_idx, _ = find(e, self.e0s)
        elif c is not None:
            section_idx, _ = find(c, self.c0s)
        elif i is not None:
            section_idx, _ = find(i, self.i0s)
        else:
            raise ValueError("e,c,i can't be None at the same time")
        return self.sections[section_idx]

    def etoi(self, e):
        return self._etoi(e)

    def itoe(self, i):
        return self._itoe(i)

    def etos(self, e, time_format=None):
        time_format = time_format or "%Y%m%d %H:%M:%S"
        time_unit = 1e6  # hardcode here
        timestamp = e / time_unit
        return datetime.datetime.fromtimestamp(timestamp, tz=self.tz_info).strftime(time_format)

    def stoe(self, s):
        parsed_datetime = parser.parse(s)
        if parsed_datetime.tzinfo is None:
            parsed_datetime = parsed_datetime.astimezone(self.tz_info)
            # parsed_datetime = self.tz_info.convert(parsed_datetime)
        etime = int(parsed_datetime.timestamp() * 1e6)
        return etime

    def etom(self, e):
        pass

    def mtoe(self, m):
        pass

    def stoi(self, s):
        pass

    def itos(self, i):
        pass

    def stom(self, s):
        pass

    def mtos(self, m):
        pass

    def itom(self, i):
        return self._itom(i)

    def mtoi(self, m):
        return self._mtoi(m)
