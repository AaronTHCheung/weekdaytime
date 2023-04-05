from bitarray import bitarray, frozenbitarray
from bitarray.util import intervals
import re

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
    
    @staticmethod
    def strpweekday(weekday: int):
        d = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
        if weekday not in d.keys(): raise Exception('weekday must be an integer between 0 and 6 inclusive')
        return d[weekday]

    @staticmethod
    def intfweekday(weekdayAbbrev: str):
        d = {'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6}
        if weekdayAbbrev not in d.keys(): raise Exception('weekdayAbbrev must be one of ' + ','.join(d.keys()))
        return d[weekdayAbbrev]

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
        return self.strpweekday(self.weekday) + ' ' + str(self.hour).zfill(2) + ':' + str(self.minute).zfill(2)

    
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
        
    @staticmethod
    def strpperiod(string: str):
        # string example: 09:00~15:00,17:00~20:00;14:00~02:00(Fri);12:00~20:00(Sat,Sun)
        ba = bitarray(60*24*7)
        ba.setall(0)

        generic_string = ''
        m = re.search(';?([0-9:~,]+);|$', string)
        if m.group(0) != '':
            # there is a weekday-generic part
            generic_string = m.group(1)
            specific_string = string[:m.span()[0]] + ';' + string[m.span()[1]:]
        else:
            # all parts are weekday-specific
            specific_string = string

        # weekday-specific days are filled first
        specific_predicates = bitarray('0000000')
        for specific_substring in specific_string.split(';'):
            m = re.search('([0-9:~,]+)\(([A-Za-z,]+)\)', specific_substring)
            if m is None: continue
            time_string, weekdayAbbrev_string = m.groups()
            starts_minute_of_day, ends_minute_of_day = [], []
            for time_substring in time_string.split(','):
                start_hour, start_minute, end_hour, end_minute = [int(x) for x in re.split(':|~', time_substring)]

                start_minute_of_day = start_hour * 60 + start_minute
                end_minute_of_day = end_hour * 60 + end_minute
                if end_minute_of_day < start_minute_of_day: end_minute_of_day += 60 * 24  # across midnight

                starts_minute_of_day.append(start_minute_of_day)
                ends_minute_of_day.append(end_minute_of_day)
                
            for weekdayAbbrev in weekdayAbbrev_string.split(','):
                start_weekday = weekdaytime.intfweekday(weekdayAbbrev)
                specific_predicates[start_weekday] = 1
                for s, e in zip(starts_minute_of_day, ends_minute_of_day):
                    start_weekdaytime = weekdaytime.from_min_of_week(start_weekday * 24 * 60 + s)
                    end_weekdaytime = weekdaytime.from_min_of_week(start_weekday * 24 * 60 + e)
                    ba |= period(start_weekdaytime, end_weekdaytime)._fba

        # remaining days are filled with weekday-generic information
        for time_substring in generic_string.split(','):
            if len(time_substring) != 11: continue
            start_hour, start_minute, end_hour, end_minute = [int(x) for x in re.split(':|~', time_substring)]

            start_minute_of_day = start_hour * 60 + start_minute
            end_minute_of_day = end_hour * 60 + end_minute
            if end_minute_of_day < start_minute_of_day: end_minute_of_day += 60 * 24  # across midnight

            for i in specific_predicates.search(0):
                start_weekdaytime = weekdaytime.from_min_of_week(i * 24 * 60 + start_minute_of_day)
                end_weekdaytime = weekdaytime.from_min_of_week(i * 24 * 60 + end_minute_of_day)
                ba |= period(start_weekdaytime, end_weekdaytime)._fba

        return period.from_bitarray(ba)
    
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
        for i, weekday in enumerate(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']):
            weekday_fba = self._fba[i*24*60 : (i+1) * 24 * 60]
            if sum(weekday_fba) == 0: continue
            for value, start_mod, end_mod in intervals(weekday_fba):
                if value == 0: continue
                start_hour, start_minute = start_mod // 60, start_mod % 60
                end_hour, end_minute = end_mod // 60, end_mod % 60
                string += str(start_hour).zfill(2) + ':' + str(start_minute).zfill(2) + '~' + str(end_hour).zfill(2) + ':' + str(end_minute).zfill(2) + ','
            string = string[:-1]  # remove the last ','
            string += f'({weekday});'
        return string[:-1]