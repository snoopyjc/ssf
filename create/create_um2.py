from datetime import date, timedelta
from dateutil.parser import parse as date_parse

leap_year = set()

with open('umcal.txt', 'r') as lc:
    um_cal = lc.read().splitlines()

with open('umcal.bin', 'wb') as um2:
    for line in um_cal[1:]:
        fields = line.split('\t')
        try:
            year, month, day = fields[1].split('-')
            year = int(year)
            month = int(month)
            day = int(day)
            value = ((year-1317)<<9) | (month<<5) | day
            um2.write(value.to_bytes(2, byteorder='big'))
        except ValueError:
            pass            # Skip the #VALUE! error for 2/29/1900
