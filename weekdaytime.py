from bitarray import bitarray, frozenbitarray
from bitarray.util import intervals

class weekdaytime():
    def __init__(self, weekday: int, hour: int, minute: int):
        if not (isinstance(weekday, int) and 0 <= weekday and weekday <= 6):
            raise Exception('weekday must be an integer between 0 and 6 inclusive')
        self.weekday = weekday

        if not (isinstance(hour, int) and 0 <= hour and hour <= 23):
            raise Exception('hour must be an integer between 0 and 23 inclusive')
        self.hour = hour

        if not (isinstance(minute, int) and 0 <= minute and minute <= 59):
            raise Exception('minute must be an integer between 0 and 59 inclusive')
        self.minute = minute

    @property
    def min_of_week(self) -> int:
        return self.weekday*24*60 + self.hour*60 + self.minute
    
    @staticmethod
    def from_min_of_week(m: int):
        wdt = weekdaytime(0, 0, 0)
        wdt.add_minute(m)
        return wdt

    def add_day(self, day: int):
        self.weekday = (self.weekday+day) % 7

    def add_hour(self, hour: int):
        hour += self.hour
        self.hour = 0
        day = hour // 24
        new_hour = hour % 24
        self.add_day(day)
        self.hour = new_hour

    def add_minute(self, minute: int):
        minute += self.minute
        self.minute = 0
        hour = minute // 60
        new_minute = minute % 60
        self.add_hour(hour)
        self.minute = new_minute

    def add(self, **kwargs: int):
        for k,v in kwargs.items():
            if k == 'day': self.add_day(v)
            if k == 'hour': self.add_hour(v)
            if k == 'minute': self.add_minute(v)

    def __str__(self):
        return {
            0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'
        }[self.weekday] + ' ' + str(self.hour).zfill(2) + ':' + str(self.minute).zfill(2)

    
class period():
    def __init__(self, *args: weekdaytime):
        '''
        args is [start1_weekdaytime, end1_weekdaytime, start2_weekdaytime, end2_weekdaytime, ... ]
        '''

        ba = bitarray(60*24*7)
        ba.setall(0)

        for i in range(len(args)//2):
            start_idx, end_idx = args[2*i].min_of_week, args[2*i+1].min_of_week
            if end_idx > start_idx:  
                # the period does NOT span across from Sat to Sun
                ba[start_idx:end_idx] = 1
            elif end_idx < start_idx:  
                # the period spans across from Sat to Sun
                ba[start_idx:] = 1
                ba[:end_idx] = 1

        self._fba = frozenbitarray(ba)

    @staticmethod
    def from_bitarray(ba: bitarray):
        if isinstance(ba, bitarray) and len(ba.unpack()) == 60*24*7:
            p = period()
            p._fba = frozenbitarray(ba)
            return p
        else:
            raise Exception('argument is not a valid bitarray instance with size 60*24*7')
    
    def __and__(self, p):
        if not isinstance(p, period): 
            raise TypeError('at least one operands is not a valid weekdaytime.period')
        return period.from_bitarray(self._fba & p._fba)
    
    def __or__(self, p):
        if not isinstance(p, period): 
            raise TypeError('at least one operands is not a valid weekdaytime.period')
        return period.from_bitarray(self._fba | p._fba)
    
    def __contains__(self, x) -> bool:
        if isinstance(x, period):
            return sum(x._fba) == sum(self._fba & x._fba)
        
    def __str__(self):
        string = ''
        for value, start, end in intervals(self._fba):
            if value == 1:
                string += str(weekdaytime.from_min_of_week(start)) + ' ~ ' + str(weekdaytime.from_min_of_week(end)) + '\n'
        return string.rstrip()