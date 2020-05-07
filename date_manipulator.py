import datetime as dt
from datetime import datetime
import pandas as pd
import numpy as np


def parse_date(date:str, initial_format, final_format):
    # return a date in MM-DD-YYYY format
    datetimeobject = datetime.strptime(date, initial_format)
    return datetimeobject.strftime(final_format)

def get_dates(start, end, freq = None):
    # date: YYYY-MM-DD format
    for date in pd.date_range(start=start, end=end, freq = freq).date:
        yield str(date)

def get_range_of_dates(date_range):
    # date_range: lists of date strings in mm/dd/yy format 
    # returns numpy array since matplotlib works with numpy arrays
    first_date = parse_date(date_range[0],'%m/%d/%y','%Y-%m-%d')
    final_date = parse_date(date_range[-1],'%m/%d/%y','%Y-%m-%d')
    final_date = get_changed_date(final_date, '%Y-%m-%d', 1, True) # need to get final date + 1 day because of np.arange()
    return np.arange(first_date, final_date, dtype='datetime64[D]')

def get_changed_date(date, format, change, dtobj = False):
    # return datetime object if dtobj is True
    datetimeobject = datetime.strptime(date, format)
    changed_date = datetimeobject + dt.timedelta(days=change)
    if dtobj:
        return changed_date
    else:
        return changed_date.strftime(format)

def get_previous_date(date, format, dtobj = False):
    return get_changed_date(date, format, -1, dtobj)

