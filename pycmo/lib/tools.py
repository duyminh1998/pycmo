# Author: Minh Hua
# Date: 08/16/2021
# Purpose: Library of helper functions.

from datetime import datetime, timedelta

def parse_datetime(time_int):
    n_ticks = time_int & 0x3fffffffffffffff
    secs = n_ticks / 1e7

    d1 = datetime(1, 1, 1)
    t1 = timedelta(seconds = secs)
    return d1 + t1

def ticks_to_unix(ticks):
    return int((int(ticks)/10000000) - 621355968000000000/10000000)