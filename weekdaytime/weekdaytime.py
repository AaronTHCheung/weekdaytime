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