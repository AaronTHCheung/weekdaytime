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

        p3 = period.strpperiod('09:00~14:30,16:30~21:00')
        self.assertEqual(str(p3), '09:00~14:30,16:30~21:00(Sun,Mon,Tue,Wed,Thu,Fri,Sat)')

    def test_period_from_googlemaps_periods(self):
        response1 = {'html_attributions': [], 'result': {'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 22.127214, 'lng': 113.532849}}, 'opening_hours': {'periods': [{'open': {'day': 0, 'time': '0000'}}]}, 'types': ['tourist_attraction', 'point_of_interest', 'establishment']}, 'status': 'OK'}
        response2 = {'html_attributions': [], 'result': {'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 22.5816173, 'lng': 114.5125911}}, 'opening_hours': {'periods': [{'close': {'day': 1, 'time': '2100'}, 'open': {'day': 1, 'time': '0900'}}, {'close': {'day': 2, 'time': '2100'}, 'open': {'day': 2, 'time': '0900'}}, {'close': {'day': 3, 'time': '2100'}, 'open': {'day': 3, 'time': '0900'}}, {'close': {'day': 4, 'time': '2100'}, 'open': {'day': 4, 'time': '0900'}}, {'close': {'day': 5, 'time': '2100'}, 'open': {'day': 5, 'time': '0900'}}, {'close': {'day': 6, 'time': '1800'}, 'open': {'day': 6, 'time': '0900'}}]}, 'types': ['restaurant', 'food', 'point_of_interest', 'establishment']}, 'status': 'OK'}
        p1 = period.from_googlemaps_periods(response1['result']['opening_hours']['periods'])
        p2 = period.from_googlemaps_periods(response2['result']['opening_hours']['periods'])
        
        self.assertEqual(sum(p1._fba), 7*24*60)
        self.assertEqual(str(p1), '00:00~24:00(Sun,Mon,Tue,Wed,Thu,Fri,Sat)')
        
        self.assertEqual(sum(p2._fba), (21-9)*60*5+9*60)
        self.assertEqual(str(p2), '09:00~21:00(Mon,Tue,Wed,Thu,Fri);09:00~18:00(Sat)')

if __name__ == '__main__':
    unittest.main()