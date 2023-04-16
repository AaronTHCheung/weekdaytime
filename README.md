# weekdaytime: modelling availability within a week
This library includes Python classes for modelling available periods within a week.

## Key features
- Simple checking of whether visiting period is within an available period. The expression
    ```
    visit_period in available_period
    ```
    evaluates to True if and only if ```visit_period``` is within ```available_period```.
- Manipulate period objects with bitwise operators (```|, &, ~, ^```)
- Convert period string into a period object, and vise versa (e.g., `'09:00~15:00,17:00~21:00;15:00~02:00(Fri,Sat)'`)
- (*New in version 0.1.0*) A period can be instantiated with JSON dictionary obtained as the ```opening_hours/periods``` field in a Google Maps Places (Details) API response (https://developers.google.com/maps/documentation/places/web-service/details#PlaceOpeningHours)

## Installation
1. Python version must not be less than 3.6.
2. The dependent library `bitarray` requires Microsoft Visual C++ 14.0. Get it with "Microsoft Visual C++ Build Tools": https://visualstudio.microsoft.com/downloads/
3. Install with pip using the command
    ```
    pip install weekdaytime
    ```

## Usage
### weekdaytime class
A weekdaytime instance specifies a point in time in a week.
```
from weekdaytime import weekdaytime as wdt

my_wdt = wdt(weekday=1, hour=9, minute=0)
print(my_wdt.weekday)     # 1
print(my_wdt.hour)        # 9
print(my_wdt.minute)      # 0
print(my_wdt)             # 'Mon 09:00'
print(my_wdt.min_of_week) # 1980

my_wdt.add(
    day=1, 
    hour=2, 
    minute=30
)
print(my_wdt)             # 'Tue 11:30'
```
---
### period class
A period instance specifies the available periods within a week. Compatibility of period instances can be checked using the `in` keyword.
```
from weekdaytime import period
from weekdaytime import weekdaytime as wdt

# Available from Mon 09:00 to Mon 15:30, and from Mon 17:30 to Mon 21:00
mon0900 = wdt(1, 9, 0)
mon1530 = wdt(1, 15, 30)
mon1730 = wdt(1, 17, 30)
mon2100 = wdt(1, 21, 0)
avail = period(mon0900, mon1530, mon1730, mon2100)
print(avail)             # '09:00~15:30,17:30~21:00(Mon)'

# Visiting period from Mon 10:00 to Mon 12:00
mon1000 = wdt(1, 10, 0)
mon1200 = wdt(1, 12 ,0)
visit_1 = period(mon1000, mon1200)
print(visit_1)           # '10:00~12:00(Mon)'
print(visit_1 in avail)  # True

# Visiting period from Mon 15:00 to Mon 17:00
mon1500 = wdt(1, 15, 0)
mon1700 = wdt(1, 17 ,0)
visit_2 = period(mon1500, mon1700)
print(visit_2)           # '15:00~17:00(Mon)'
print(visit_2 in avail)  # False
```
---
A period can have arbitrary number of discontinuous segments and can be manipulated using boolean operators.
```
from weekdaytime import period
from weekdaytime import weekdaytime as wdt

# Another way to instantiate a period with regular hours 09:00~18:00 for Monday to Friday
avail_mon2fri = period.from_regulars(
    start_hour=9,
    start_minute=0,
    end_hour=18,
    end_minute=0,
    repeat_from=1,
    repeat_to=5
)
print(avail_mon2fri)   # '09:00~18:00(Mon,Tue,Wed,Thu,Fri)'

# Weekend hours are 12:00~17:00
avail_weekend = period(
    wdt(6, 12, 0), wdt(6, 17, 0),
    wdt(0, 12, 0), wdt(0, 17, 0)
)
print(avail_weekend)   # '12:00~17:00(Sun,Sat)'

avail_or = avail_mon2fri | avail_weekend  # or operator, add the hours together
print(avail_or)        # '09:00~18:00(Mon,Tue,Wed,Thu,Fri);12:00~17:00(Sun,Sat)'

avail_and = avail_mon2fri & avail_weekend  # intersection
print(avail_and)       # ''

avail_not = ~avail_or  # inverse, unavailable becomes available
print(avail_not)       # '00:00~09:00,18:00~24:00(Mon,Tue,Wed,Thu,Fri);00:00~12:00,17:00~24:00(Sun,Sat)'

avail_xor = avail_mon2fri ^ avail_weekend  # exclusive or
print(avail_xor)       # '09:00~18:00(Mon,Tue,Wed,Thu,Fri);12:00~17:00(Sun,Sat)'
```
---
A period can be instantiated by parsing a formatted string. Suppose we want to model shop with the following opening hours:
- Default: 09:00\~15:00,17:00\~21:00
- Wed:     Not open
- Fri,Sat: 12:00~02:00 (i.e., to 02:00 AM the following day)
- Sun:     09:00~21:00
```
from weekdaytime import period

# Using a default string
avail_string = '09:00~15:00,17:00~21:00;00:00~00:00(Wed);12:00~02:00(Fri,Sat);09:00~21:00(Sun)'
p = period.strpperiod(avail_string)
print(p)  # '09:00~15:00,17:00~21:00(Mon,Tue,Thu);00:00~02:00,09:00~21:00(Sun);12:00~24:00(Fri);00:00~02:00,12:00~24:00(Sat)'

# Specifying all opening weekdays, the effect is the same
avail_string = '09:00~15:00,17:00~21:00(Mon,Tue,Thu);12:00~02:00(Fri,Sat);09:00~21:00(Sun)'
p = period.strpperiod(avail_string)
print(p)  # '09:00~15:00,17:00~21:00(Mon,Tue,Thu);00:00~02:00,09:00~21:00(Sun);12:00~24:00(Fri);00:00~02:00,12:00~24:00(Sat)'
```

---
*New in version 0.1.0*

A period can be instantiated with JSON dictionary obtained as the ```opening_hours/periods``` field in a Google Maps Places (Details) API response (https://developers.google.com/maps/documentation/places/web-service/details#PlaceOpeningHours)
```
from weekdaytime import period

gperiods1 = [{'open': {'day': 0, 'time': '0000'}}]
gperiods2 = [{'close': {'day': 1, 'time': '2100'}, 'open': {'day': 1, 'time': '0900'}}, 
             {'close': {'day': 2, 'time': '2100'}, 'open': {'day': 2, 'time': '0900'}}, 
             {'close': {'day': 3, 'time': '2100'}, 'open': {'day': 3, 'time': '0900'}}, 
             {'close': {'day': 4, 'time': '2100'}, 'open': {'day': 4, 'time': '0900'}}, 
             {'close': {'day': 5, 'time': '2100'}, 'open': {'day': 5, 'time': '0900'}}, 
             {'close': {'day': 6, 'time': '1800'}, 'open': {'day': 6, 'time': '0900'}}]

p1 = period.from_googlemaps_periods(gperiods1)
p2 = period.from_googlemaps_periods(gperiods2)

print(p1)    # '00:00~24:00(Sun,Mon,Tue,Wed,Thu,Fri,Sat)'
print(p2)    # '09:00~21:00(Mon,Tue,Wed,Thu,Fri);09:00~18:00(Sat)'
```
