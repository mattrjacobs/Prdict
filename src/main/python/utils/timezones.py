from datetime import timedelta, tzinfo

class EstTzInfo(tzinfo):
    def utcoffset(self, dt): return timedelta(hours=-4)
    def dst(self, dt): return timedelta(0)
    def tzname(self, dt): return 'EST+04EDT'
    def olsen_name(self): return 'US/Eastern'

class UstTzInfo(tzinfo):
    def utcoffset(self, dt): return timedelta(hours=0)
    def dst(self, dt): return timedelta(0)
    def tzname(self, dt): return 'UST'
    def olsen_name(self): return 'UST'
