"""
Date utilities - Stolen from the tms :)
"""
import calendar, datetime, re, time
import pytz


_date_date_re = re.compile(r'([\d-]+)T?')
_date_time_re = re.compile(r'(?:T| )([\d:]+)')
def parse_date(datetime_str, default_to_local_time = True):
    """
    Parses a string for a date and time, assuming
    that the date is of the format 'YYYY-MM-DD' and the time is of the format 'HH:MM:SS'
    and handles +/-HH:MM offsets according to RFC3339.
    Returns the datetime as a posix timestamp or None if it fails to parse
    """
    date_search = _date_date_re.search(datetime_str)
    if date_search:
        if date_search.group(1).find('-') != -1:
            date_time_array = [int(i) for i in date_search.group(1).split('-')]
        else:
            date_time_array = [
                int(date_search.group(1)[0:4]),
                int(date_search.group(1)[4:6]),
                int(date_search.group(1)[6:8])
            ]
        datetime_str = datetime_str[date_search.end(1):]
        
        # -- Search for the time component (which is optional)
        time_search = _date_time_re.search(datetime_str)
        if time_search:
            if time_search.group(1).find(':') != -1:
                time_array = [int(i) for i in time_search.group(1).split(':')]
            else:
                time_array = [
                    int(time_search.group(1)[i] + time_search.group(1)[i+1])
                    for i in range(0, len(time_search.group(1)), 2)
                ]
            # -- Pad out any missing time components with zeroes
            for i in range(3 - len(time_array)):
                time_array.append(0)
            date_time_array.extend(time_array)
            datetime_str = datetime_str[time_search.end():]
        else:
            #Missing time so fill it with zeros
            date_time_array += [0,0,0]
        
        #Create the datetime object 
        parsed_timestamp = float(calendar.timegm(date_time_array))
        
        #Convert the KDM's local time to UTC
        parsed_timestamp += _parse_time_zone(datetime_str, parsed_timestamp, default_to_local_time)
        
        return datetime.datetime.utcfromtimestamp(parsed_timestamp)

    return ValueError

_date_timezone_regex = re.compile(r'(\+|-)(\d\d):?(\d\d)')
_zulu_time_regex     = re.compile(r'Z')
def _parse_time_zone(datetime_str, parsed_timestamp, default_to_local_time):
    """
    Parses a datetime string and looks for the RFC 3339 specified time offset +\-HH:MM
    and returns a int that will convert the timestamp to UTC
    It doesn't look for the possible Z (zulu) case because zulu==UTC and a failed search results in 0 being returned
    """
    
    tz_search = _date_timezone_regex.search(datetime_str)
    if tz_search:
        utc_offset_direction = tz_search.group(1)
        utc_offset_hours = int(utc_offset_direction + tz_search.group(2))
        utc_offset_mins = int(utc_offset_direction + tz_search.group(3))
        #Multiply the result by -1 because +05:00 means the UTC time will be 5 hours less than local time
        return (60*60*utc_offset_hours + 60*utc_offset_mins) * -1
    elif _zulu_time_regex.match(datetime_str) or not default_to_local_time:
        return 0
    else:
        if time.localtime(parsed_timestamp).tm_isdst and time.daylight:
            return time.altzone
        else:
            return time.timezone

def parse_xs_duration(duration_str):
    """
    Parses a string representing a duration according to ISO 8601 and returns it's value in seconds
    Only intended to be used for short durations (months and years are treated as a fixed number of seconds)
    """
    seconds_per_minute = 60.0
    seconds_per_hour = seconds_per_minute * 60.0
    seconds_per_day = seconds_per_hour * 24.0
    seconds_per_year = 31557600.0 # -- http://en.wikipedia.org/wiki/Year
    seconds_per_month = seconds_per_year / 12.0
    
    duration_re = re.compile(r"""
        (?P<sign>[-])?
        P
        ((?P<years>\d\d?)Y)?
        ((?P<months>\d\d?)M)?
        ((?P<days>\d\d?)D)?
        (T
        ((?P<hours>\d\d?)H)?
        ((?P<mins>\d\d?)M)?
        ((?P<secs>\d?\d?([.]\d+)?)S)?
        )?
        $""", re.VERBOSE)

    re_match = duration_re.match(duration_str)
    if not re_match:
        raise ValueError('Invalid duration string format')
    info = re_match.groupdict()
    duration_in_seconds = 0.0

    if info['secs']:
        duration_in_seconds += float(info['secs'])
    if info['mins']:
        duration_in_seconds += seconds_per_minute * float(info['mins'])
    if info['hours']:
        duration_in_seconds += seconds_per_hour * float(info['hours'])
    if info['days']:
        duration_in_seconds += seconds_per_day * float(info['days'])
        
    accuracy_warning = False
    if info['months'] and info['months'] != '0':
        accuracy_warning = True
        duration_in_seconds += seconds_per_month * float(info['months'])
    if info['years'] and info['years'] != '0':
        accuracy_warning = True
        duration_in_seconds += seconds_per_year * float(info['years'])
    
    if accuracy_warning:
        logging.warning('The duration parser is not intended to be used on durations > 1 day [%s]' % duration_str)

    return duration_in_seconds

def seconds_to_xs_duration(seconds):
    return 'PT{seconds}S'.format(seconds = seconds)

def parse_simple_duration(duration_str):
    """
    Parses a simple duration format HH:MM:SS.fff
    """
    duration_re = re.compile(r"""
        ^
        (?P<hours>\d\d?):
        (?P<mins>\d\d?):
        (?P<secs>\d?\d?([.]\d+)?)
        $
        """, re.VERBOSE)
    
    re_match = duration_re.match(duration_str)
    if not re_match:
        raise ValueError('Invalid duration string format')
    
    info = re_match.groupdict()
    duration_in_seconds = float(info['secs'])
    duration_in_seconds += float(info['mins']) * 60
    duration_in_seconds += float(info['hours']) * 60 * 60
    
    return duration_in_seconds
    
def seconds_to_simple_duration(seconds):
    hours = seconds // (60 * 60)
    seconds -= hours * (60 * 60)
    minutes = seconds // 60
    seconds -= minutes * 60
    return '%02d:%02d:%06.3f' % (hours, minutes, seconds) 

def utc_datetime_to_local(utc_datetime):
    """
    Adjusts a datetime to the local time from UTC
    """
    utc_timestamp = calendar.timegm(utc_datetime.timetuple())
    return datetime.datetime.fromtimestamp(utc_timestamp)

def local_datetime_to_utc(local_datetime):
    """
    Adjusts a datetime to UTC from the local time
    """
    utc_timestamp = time.mktime(local_datetime.timetuple())
    return datetime.datetime.utcfromtimestamp(utc_timestamp)

def posix_to_local_datetime(posix_timestamp, timezone_name):
    tz = pytz.timezone(timezone_name)
    utc_datetime = datetime.datetime.utcfromtimestamp(posix_timestamp)
    utc_datetime = pytz.utc.localize(utc_datetime)
    return utc_datetime.astimezone(tz)

def local_datetime_to_posix(local_datetime, timezone_name):
    tz = pytz.timezone(timezone_name)
    if local_datetime.tzinfo is None:
        local_datetime = tz.localize(local_datetime)
    utc_datetime = local_datetime.astimezone(pytz.utc)
    return calendar.timegm(utc_datetime.timetuple()) + (utc_datetime.microsecond / 1000000)

def datetime_tz_offset(local_datetime, tz_name):
    """
    Returns the offset in hours of a datetime based on it's timxzone name.
    :param local_datetime: Datetime object.
    :param timezone_name: tz name
    """
    return pytz.timezone(tz_name).localize(local_datetime).strftime("%z")

def get_timezone(timezone_name):
    try:
        return pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError:
        return None

def datespan(start, end, delta=datetime.timedelta(days=1)):
    """
    Generator that returns dates between two times, incrementing based on the 
    delta attribute.
    """
    curr = start
    while curr <= end:
        yield curr
        curr += delta


if __name__ == '__main__':
    print parse_date('2012-01-30 12:58:00')
    print parse_date('2012-06-30 12:58:00')
    
    print parse_date('2012-01-30T12:58:00Z')
    print parse_date('2012-06-30T12:58:00Z')
    
