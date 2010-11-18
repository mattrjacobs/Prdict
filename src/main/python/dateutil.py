import datetime
import time

http_date_formats = [
    "%a, %d %b %Y %H:%M:%S GMT", # RFC1123
    "%A, %d-%b-%y %H:%M:%S GMT", # RFC1036
    "%a %b %d %H:%M:%S %Y",      # asctime()
]
 
def unix_timestamp(dt):
    """Converts a datetime object into a Unix timestamp, including
    fractional seconds."""
    return time.mktime(dt.timetuple()) + (0.000001)*dt.microsecond

def http_header(dt):
    """Formats a datetime object as an HTTP/1.1-compliant date header, e.g.
    Sun, 06 Nov 1994 08:49:37 GMT"""
    return dt.strftime(http_date_formats[0])

def parse_http_date(s):
    """Given a string, attempt to parse it as an HTTP date value and
    return a datetime."""
    for fmt in http_date_formats:
        try:
            return datetime.datetime.strptime(s,fmt)
        except:
            pass
    return None

def normalize(dt):
    """Because HTTP date values only have a 1-second resolution, we may
    need to normalize a datetime to the proper even-second in order to
    do accurate datetime comparisons."""
    return parse_http_date(http_header(dt))
