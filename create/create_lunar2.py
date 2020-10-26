from datetime import date, timedelta
from dateutil.parser import parse as date_parse

leap_year = set()

with open('lunarcal.txt', 'r') as lc:
    lunar_cal = lc.read().splitlines()

for line in lunar_cal[1:]:
    fields = line.split('\t')
    try:
        year, month, day = fields[1].split('-')
        year = int(year)
        month = int(month)
        if month == 13:
            leap_year.add(year)
    except ValueError:
        pass            # Skip the #VALUE! error for 2/29/1900

with open('lunarcal.bin', 'wb') as lc2:
    #print('Lunar 0E\tisleap', file=lc2)
    for line in lunar_cal[1:]:
        fields = line.split('\t')
        try:
            year, month, day = fields[1].split('-')
            year = int(year)
            month = int(month)
            day = int(day)
            isleap = 1 if year in leap_year else 0
            #print(f'{fields[1]}\t{isleap}', file=lc2)
            value = ((year-1899)<<10) | (month<<6) | (day<<1) | isleap
            lc2.write(value.to_bytes(3, byteorder='big'))
        except ValueError:
            pass            # Skip the #VALUE! error for 2/29/1900
