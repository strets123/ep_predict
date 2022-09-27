import time

def date_as_unix(val):
    return time.mktime(val.timetuple())
