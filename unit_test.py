import unittest
from weekdaytime import weekdaytime
from weekdaytime import period

class Test(unittest.TestCase):
    def test_weekdaytime_add(self):
        wdt = weekdaytime(2, 18, 18)
        wdt.add_day(1)
        wdt.add_hour(8)
        wdt.add_minute(11)
        self.assertEqual(wdt.weekday, 4)
        self.assertEqual(wdt.hour, 2)
        self.assertEqual(wdt.minute, 29)
        self.assertEqual(wdt.min_of_week, 5909)

    def test_period_from_regulars(self):
        p1 = period(
            weekdaytime(2, 2, 34), weekdaytime(2, 22, 9),
            weekdaytime(3, 2, 34), weekdaytime(3, 22, 9),
            weekdaytime(4, 2, 34), weekdaytime(4, 22, 9),
        )
        p2 = period.from_regulars(2, 34, 22, 9, 2, 4)
        self.assertEqual(p1._fba, p2._fba)

    def test_period_strpperiod(self):
        p1 = period.strpperiod('09:00~15:00,17:00~21:00;00:00~00:00(Wed,aeafdgs);12:00~02:00(Fri,Sat);09:00~21:00(Sun)')
        p2 = period.strpperiod('09:00~15:00,17:00~21:00(Mon,Tue,Thu);12:00~02:00(Fri,Sat);09:00~21:00(Sun,Hol)')
        self.assertEqual(p1._fba, p2._fba)
        self.assertEqual(str(p1), '09:00~15:00,17:00~21:00(Mon,Tue,Thu);00:00~02:00,09:00~21:00(Sun);12:00~24:00(Fri);00:00~02:00,12:00~24:00(Sat)')

if __name__ == '__main__':
    unittest.main()