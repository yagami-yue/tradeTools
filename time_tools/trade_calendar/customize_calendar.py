from bisect import bisect_left
from typing import (
    List,
    Dict
)
import datetime
from time_tools.trade_calendar.section import (
    Section,
    Sections,
)
from time_tools.trade_calendar.timepoint import TimePoint
import numpy as np
import dateutil.tz as tz
from dateutil import parser


def make_sections(sessions: List[Dict], tz_info, c0=0, auction=True) -> List[Section]:
    i0 = 0
    sections = []
    for session in sessions:
        if not auction:
            if not session['is_continuous']:
                continue
        s0 = session['start_stime']
        s1 = session['end_stime']
        dt0 = datetime.datetime.fromisoformat(s0)
        if dt0.tzinfo is None:
            dt0 = dt0.astimezone(tz_info)
        
        dt1 = datetime.datetime.fromisoformat(s1)
        if dt1.tzinfo is None:
            dt1 = dt1.astimezone(tz_info)
        
        e0 = int(dt0.timestamp() * 1e6)
        e1 = int(dt1.timestamp() * 1e6)
        length = e1 - e0
        m0 = int(s0.split("T")[1].replace(":", "")) * 1_000_000
        m1 = int(s1.split("T")[1].replace(":", "")) * 1_000_000
        tp0 = TimePoint(e0, i0, c0, m0)
        tp1 = TimePoint(e1, i0 + length, c0 + length, m1)
        i0 = i0 + length
        c0 = c0 + length
        section = Section(tp0, tp1)
        sections.append(section)
    return sections


class Calendar(Sections):
    def __init__(self, calendar_data) -> None:
        self.days = {}
        self.trading_days = []
        self.e0s = []
        self.c0 = calendar_data['initial_ctime']
        self.e0 = calendar_data['initial_etime']
        timezone = calendar_data["timezone"]  # hardcode here
        self.tz_info = tz.gettz(timezone)
        c0 = self.c0
        for date_data in calendar_data['trading_dates']:
            sessions = date_data['sessions']
            sections = make_sections(sessions, tz_info=self.tz_info, c0=c0, auction=False)
            date = date_data['natural_date'].replace("-", "")
            trading_day = Sections(date, sections, c0)
            self.days[date] = trading_day
            self.trading_days.append(trading_day)
            self.e0s.append(sections[0].e0)
            c0 = sections[-1].c1
        self.e0s = np.asarray(self.e0s)
        self.trading_days = np.asarray(self.trading_days)

    def get_day(self, sd=None) -> Sections:
        if sd not in self.days:
            raise ValueError("not in calendar")
        return self.days[sd]
    
    def get_section(self, e=None, c=None, i=None):
        section_idx = bisect_left(self.e0s, e)
        return self.sections[section_idx]
    
    def get_trading_day(self, e=None, c=None, i=None) -> Section:
        trading_idx = self.e0s.searchsorted(e, side="right") - 1
        if len(self.trading_days) - 1 > trading_idx > 0:
            return self.trading_days[trading_idx]
        elif len(self.trading_days) - 1 == trading_idx:
            if self.trading_days[trading_idx].sections[-1].e1 > e:
                return self.trading_days[trading_idx]
            else:
                raise ValueError("not in calendar")    
        else:
            raise ValueError("not in calendar")
    
    def etoi(self, e, date=None):
        try:
            if date:
                trading_day = self.get_day(date)
            else:
                trading_day = self.get_trading_day(e)
            return trading_day.etoi(e)
        except ValueError:
            return self.mtoi(self.etom(e))
    
    def itoe(self, i, date):
        try:
            day = self.get_day(date)
            section = day.get_section(i=i)
            return i - section.i0 + section.e0
        except ValueError:
            return self.mtoe(self.itom(i, date=date), date=date)
    
    def etos(self, e, time_format=None):
        time_format = time_format or "%Y%m%d %H:%M:%S"
        time_unit = 1e6 # hardcode here
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
        return int(self.etos(e)[-8:].replace(":", "")) * 1000_000

    def mtoe(self, m, date):
        return self.stoe(f"{date} {str(m // 1000_000).rjust(6, '0')}")

    def stoi(self, s):
        pass
    
    def itos(self, i, date=None):
        pass
    
    def stom(self, s):
        pass
    
    def mtos(self, m):
        pass
    
    def stoc(self, s):
        pass
    
    def ctos(self, c):
        pass
    
    def itom(self, i, date=None):
        if date is not None:
            try:
                trading_day = self.get_day(date)
            except ValueError:
                trading_day = self.trading_days[-1]
        else:
            trading_day = self.trading_days[-1]
        return trading_day.itom(i)
    
    def mtoi(self, m, date=None):
        if date is not None:
            try:
                trading_day = self.get_day(date)
            except ValueError:
                trading_day = self.trading_days[-1]
        else:
            trading_day = self.trading_days[-1]
        return trading_day.mtoi(m)
    
    def itoc(self, i, date=None):
        pass
    
    def ctoi(self, c):
        pass
