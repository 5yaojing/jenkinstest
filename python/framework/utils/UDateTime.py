import datetime

#2011-11-11 11:11:11 UTC, time zone is ignored
def ToDateTime(s : str):
    f = '%Y-%m-%d %H:%M:%S'
    s = s[0:19]

    dt = None
    try:
        dt = datetime.datetime.strptime(s, f)
    except:
        dt = datetime.datetime.now()
    return dt

def ToDateTimeSecond(s : str):
    dt = ToDateTime(s)
    return int(dt.timestamp())

def CurTimeSecond():
    dt = datetime.datetime.now()
    return int(dt.timestamp())