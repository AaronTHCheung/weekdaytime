from bitarray import bitarray, frozenbitarray
from bitarray.util import intervals
import re
from weekdaytime import weekdaytime
from itertools import combinations

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
        m = re.search(';|^([0-9:~,]+)(;|$)', string)
        if m.group(0) != '' and m.groups()[0] is not None:
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
                try:
                    start_weekday = weekdaytime.intfweekday(weekdayAbbrev)
                    specific_predicates[start_weekday] = 1
                    for s, e in zip(starts_minute_of_day, ends_minute_of_day):
                        start_weekdaytime = weekdaytime.from_min_of_week(start_weekday * 24 * 60 + s)
                        end_weekdaytime = weekdaytime.from_min_of_week(start_weekday * 24 * 60 + e)
                        ba |= period(start_weekdaytime, end_weekdaytime)._fba
                except Exception:
                    pass

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
    
    @staticmethod
    def from_regulars(start_hour, start_minute, end_hour, end_minute, repeat_from, repeat_to):
        return period(
            *sum([[weekdaytime(i, start_hour, start_minute), weekdaytime(i, end_hour, end_minute)] for i in range(repeat_from, repeat_to+1)], [])
        )

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
        
    def __xor__(self, p):
        if not isinstance(p, period): 
            raise TypeError('at least one operands is not a valid weekdaytime.period')
        return period.from_bitarray(self._fba ^ p._fba)
    
    def __invert__(self):
        return period.from_bitarray(~self._fba)
        
    def __str__(self):
        weekdays_oneDayFba = [self._fba[i*24*60 : (i+1)*24*60] for i in range(7)]
        A = [bitarray('0000000') for i in range(7)]
        for i in range(7):
            if sum(weekdays_oneDayFba[i]) > 0: A[i][i] = 1
        for i, j in combinations(range(7), 2):
            if sum(weekdays_oneDayFba[i] ^ weekdays_oneDayFba[j]) == 0 and sum(weekdays_oneDayFba[i]) > 0 and sum(weekdays_oneDayFba[j]) > 0:
                # i, j have the same time period if we disregard the weekday
                A[i][j] = 1

        grouped_predicates = bitarray('0000000')
        groups = []
        for i in range(7):
            if grouped_predicates[i]: continue
            nonzero_idxs = A[i].search(1)
            groups.append(set(nonzero_idxs))
            for j in nonzero_idxs:
                grouped_predicates[j] = 1
        
        string = ''
        for group in sorted(groups, key=len, reverse=True):
            if len(group) == 0: break
            itvs_true_string = [
                str(x[1]//60).zfill(2) +  #  start_hour
                ':' +
                str(x[1]%60).zfill(2)  +  #  start_minute
                '~' +
                str(x[2]//60).zfill(2) +  #  end_hour
                ':' +
                str(x[2]%60).zfill(2)     #  end_minute
            for x in intervals(weekdays_oneDayFba[next(iter(group))]) if x[0]]
            string += ','.join(itvs_true_string)
            string += '('
            string += ','.join([weekdaytime.strpweekday(x) for x in group])
            string += ');'
            
        return string[:-1]  # remove the last ';'