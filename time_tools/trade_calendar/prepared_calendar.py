import os
import json
from pathlib import Path

from time_tools.trade_calendar.customize_calendar import Calendar


def get_data_path():
    return Path(__file__).resolve().parent.parent / "data"


def get_stock_calendar():
    data_path = get_data_path()
    stock_calendar = os.path.join(data_path, "stock_calendar.json")
    with open(stock_calendar) as f:
        _stock_calendar_data = json.load(f)
        stock_calendar = Calendar(_stock_calendar_data)
    return stock_calendar
