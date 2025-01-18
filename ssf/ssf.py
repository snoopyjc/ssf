# -*- coding: utf-8 -*-
# ssf.py based on ssf.js: (C) 2013-present SheetJS -- http://sheetjs.com */
#    var SSF = ({});
import math
from datetime import datetime, date, timedelta, timezone
from datetime import time as tm
from types import SimpleNamespace
from dateutil.tz import tzlocal
from dateutil.parser import parse as date_parse
import re
import locale as lcl
import ast              # Issue #13
import calendar
from babel.core import default_locale, Locale, UnknownLocaleError
from babel.numbers import format_decimal, decimal
import yaml
import json
import os
import warnings
from copy import copy
import gzip
from convertdate import hebrew, islamic
#from lunarcalendar import Solar, Converter
import mmap
from ummalqura.hijri_date import HijriDate

class SSF_CALENDAR:         # Issue #6
    """Handle alternative calendars for ssf.  This shouldn't be used directly."""
    (SYSTEM_DEFAULT, GREGORIAN_LOCAL, GREGORIAN_US, JAPANESE, TAIWAN, KOREAN,       # 00-05
    HIJRI, THAI_BUDDHIST, JEWISH, GREGORIAN_MIDDLE_EASTERN_FRENCH, GREGORIAN_ARABIC, # 06-0A
    GREGORIAN_TRANSLITERATED_ENGLISH, GREGORIAN_TRANSLITERATED_FRENCH, x0D, # 0B-0D
    LUNAR_x0E, x0F, x10, LUNAR_x11, LUNAR_x12,                              # 0E-12
    CHINESE_LUNAR, x14, x15, x16, UM_AL_QURA, x18, x19, x1A, x1B, x1C, x1D, x1E, x1F) = range(0x20)

    _has_leap_month = {0x08, 0x0E, 0x11, 0x12, 0x13}
    _LEAP_MONTH_FLAG = 0x80     # Added to calendar number in day_month_map for years that have a leap month
    day_month_map = {}          # calendar to {locale to [('Monday', 'Mon', 'January', 'Jan', 'J'), ('Tuesday', ...), ...]}

    # Each converter takes a (named)tuple (year, month, day) and returns a SimpleNamespace(year, month, day, isleap, era)

    @property
    def has_leap_month(self):
        """Could this calendar have a leap month?"""
        return self.calendar_code in SSF_CALENDAR._has_leap_month

    def to_default(self, ymd):        # No changes
        return SimpleNamespace(year=ymd[0], month=ymd[1], day=ymd[2], isleap=calendar.isleap(ymd[0]), era=None)

    def fixup_special(self, ymd):       # Issue #14
        if ymd[0] == 1900:      # Handle a couple of 'special' dates which are not real dates
            if ymd[1] == 1 and ymd[2] == 0:
                ymd = (1900, 1, 1)
            elif ymd[1] == 2 and ymd[2] == 29:
                ymd = (1900, 3, 1)
        return ymd

    era_list = None

    def to_japanese(self, ymd):       # Year changes to year in era
        if SSF_CALENDAR.era_list is None:
            era_file = os.path.join(os.path.dirname(__file__), 'eras.tsv')
            if os.path.isfile(era_file):
                with open(era_file, 'r', encoding='utf-8') as ef:
                    eras = ef.read().splitlines()
                ea = []
                for e in eras[1:]:    # Skip heading
                    loc, dt, g, gg, ggg = e.split('\t')
                    if loc != 'ja-JP':
                        continue
                    ea.append(date_parse(dt).date())
                SSF_CALENDAR.era_list = ea
        ymd2 = self.fixup_special(ymd)      # Issue #14
        dt = date(*ymd2)
        result = self.to_default(ymd)
        for eno, e in enumerate(SSF_CALENDAR.era_list):
            if dt >= e:
                result = SimpleNamespace(year=(dt.year-e.year)+1, month=ymd[1], day=ymd[2], isleap=calendar.isleap(ymd[0]), era=eno)
            else:
                return result
        return result

    def to_taiwan(self, ymd):         # No changes
        return self.to_default(ymd)

    def to_korean(self, ymd):         # year changes (2020 -> 4353)
        return SimpleNamespace(year=ymd[0] + 2333, month=ymd[1], day=ymd[2], isleap=calendar.isleap(ymd[0]), era=None)

    def to_hijri(self, ymd):          # Everything changes e.g. Mon Jan January 1/6/2020 -> AlEthnien Jamada El Oula Jamada El Oula 5/11/1441
        ymd = self.fixup_special(ymd)      # Issue #14
        year, month, day = islamic.from_gregorian(*ymd)
        leap_year = islamic.leap(year)
        return SimpleNamespace(year=year, month=month, day=day, isleap=leap_year, era=None)

    def to_thai_buddhist(self, ymd):  # Year changes along with day and month names e.g.  Mon Jan January 1/6/2020 -> จ. ม.ค. มกราคม 1/6/2563
        return SimpleNamespace(year=ymd[0] + 543, month=ymd[1], day=ymd[2], isleap=calendar.isleap(ymd[0]), era=None)

    ecclesiastical_to_civil = {7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12}
    ecclesiastical_leap_to_civil = {7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6, 13: 7, 1: 8, 2: 9, 3: 10, 4: 11, 5: 12, 6: 13}

    def to_jewish(self, ymd):         # Everything changes e.g. Mon Jan January 1/6/2020 -> Yom Sheni Tishrei Tishrei 4/9/5780
                                # Some years have a leap-month (13 months).  Conversion in convertdate module.
                                # Months are named Tishrei, Cheshvan, Kislev, Tevet, Shevat, Adar, Nisan, Iyar, Sivan, Tammuz,
                                # Av, Elul.  In years with a leap-month, "AdarI" is inserted before Adar, and Adar is renamed
                                # as "AdarII".  Note: convertdate/hebrew uses the traditional month numbers, so
                                # Nisan is 1.  5782 is a leap year.
        ymd = self.fixup_special(ymd)      # Issue #14
        year, month, day = hebrew.from_gregorian(*ymd)
        leap_year = hebrew.leap(year)
        if leap_year:
            month = SSF_CALENDAR.ecclesiastical_leap_to_civil[month]
        else:
            month = SSF_CALENDAR.ecclesiastical_to_civil[month]
        return SimpleNamespace(year=year, month=month, day=day, isleap=leap_year, era=None)

    lunar_bin = None

    def to_lunar_x0e(self, ymd):      # Everything changes e.g. Mon Jan Jan 1/6/2020 -> 月 Dec December 12/12/2019
                                      # This year (2020) has a leap April with 29 days!  This means leap: 闰
                                      # Months are named like First Month, Second Month, etc.  The leap month has
                                      # the same name as the prior month with the "leap" char before it.
                                      # Month names: 正月, 二月, 三月, 四月, 五月, 六月, 七月, 八月, 九月, 十月, 十一月, 腊月
        # We use our own converter to match what Excel does (which is probably wrong but we match it anyway)
        # lunarcal.bin is a binary file containing 3 bytes per date since the epoch (1/1/1900)
        # This 24-bit value is encoded as follows:
        #
        # 0             14      18    23       24
        # | offset_year | month | day | isleap |
        # |<  14 bits  >|< 4b  >|< 5b>|< 1 bit>|
        #
        # Where offset_year is year-1899

        if SSF_CALENDAR.lunar_bin is None:      # Runs exactly once
            lunarcal_file = os.path.join(os.path.dirname(__file__), 'lunarcal.bin')
            if os.path.isfile(lunarcal_file):
                lunar_fd = open(lunarcal_file, 'rb')    # No, we never close it
                SSF_CALENDAR.lunar_bin = mmap.mmap(lunar_fd.fileno(), 0, access=mmap.ACCESS_READ)
        ymd = self.fixup_special(ymd)      # Issue #14
        base = date(1900, 1, 1)
        delta = (date(*ymd) - base).days
        ndx = delta * 3
        try:
            value = int.from_bytes(SSF_CALENDAR.lunar_bin[ndx:ndx+3], byteorder='big')
        except Exception:
            value = 0
        result = SimpleNamespace(year=(value>>10)+1899, month=(value>>6)&0xF, 
                                 day=(value>>1)&0x1F, isleap=value&1, era=None)
        #result = Converter.Solar2Lunar(Solar(*ymd))
        #result.era = None
        #return SimpleNamespace(year=result.year, month=result.month, day=result.day, isleap=result.isleap)
        return result       # Already has all of the proper fields!

    def to_lunar_x11(self, ymd):      # Same as 0e except day name stays in English
        return self.to_lunar_x0e(ymd)

    def to_lunar_x12(self, ymd):      # Same as x11
        return self.to_lunar_x0e(ymd)

    def to_chinese_lunar(self, ymd):      # 0x13 - Same as x11
        return self.to_lunar_x0e(ymd)

    um_bin = None           # Issue #15

    def to_um_al_qura(self, ymd):     # 0x17: See https://pypi.org/project/ummalqura/
        ymd = self.fixup_special(ymd)      # Issue #14
        if ymd[0] < 1937 or (ymd[0] == 1937 and (ymd[1] < 3 or (ymd[1] == 3 and ymd[2] <= 13))):    # Issue #15
            #
            # We use our own converter to match what Excel does in the range 1900-01-01 - 1937-03-12,
            # since the ummalqura doesn't cover that date period.
            # umcal.bin is a binary file containing 2 bytes per date since the epoch (1/1/1900)
            # This 16-bit value is encoded as follows:
            #
            # 0             7       11    16
            # | offset_year | month | day |
            # |<   7 bits  >|< 4b  >|< 5b>|
            #
            # Where offset_year is year-1317
            #
            if SSF_CALENDAR.um_bin is None:     # Runs exactly once
                umcal_file = os.path.join(os.path.dirname(__file__), 'umcal.bin')
                if os.path.isfile(umcal_file):
                    with open(umcal_file, 'rb') as uf:
                        SSF_CALENDAR.um_bin = uf.read()
            base = date(1900, 1, 1)
            delta = (date(*ymd) - base).days
            ndx = delta * 2
            try:
                value = int.from_bytes(SSF_CALENDAR.um_bin[ndx:ndx+2], byteorder='big')
            except Exception:
                value = 0
            return SimpleNamespace(year=(value>>9)+1317, month=(value>>5)&0xF,
                                   day=value&0x1F, isleap=calendar.isleap(ymd[0]), era=None)

        result = HijriDate(*ymd, gr=True)
        # Leap year corresponds to the Gregorian calendar and adds a 30th day to the 6th month
        return SimpleNamespace(year=result.year, month=result.month, day=result.day, isleap=calendar.isleap(ymd[0]), era=None)

    def month_names(self, locale_name, isleap=False):
        """Return the month names for this calendar in the given ``locale_name``.  The result
        is an array of month names, starting with January in index 0, or None if
        we have no month names for this locale.  If isleap is True and this calendar
        has a leap month, then the result contains 13 entries, else it has the normal 12."""
        try:
            if isleap and self.has_leap_month:
                day_month_map = SSF_CALENDAR.day_month_map[self.calendar_code+SSF_CALENDAR._LEAP_MONTH_FLAG]
                last_month = 13
            else:
                day_month_map = SSF_CALENDAR.day_month_map[self.calendar_code]
                last_month = 12
        except KeyError:
            return None
        if locale_name not in day_month_map:
            return None
        months = []
        dmm = day_month_map[locale_name]
        for month in range(0, last_month):
            months.append((dmm[month].mmmmm, dmm[month].mmm, dmm[month].mmmm))
        return months

    def day_names(self, locale_name):
        """Return the day names for this calendar in the given ``locale_name``.  The result
        is an array of day names, starting with Sunday in index 0, or None if
        we have no day names for this locale"""
        if self.calendar_code not in SSF_CALENDAR.day_month_map:
            return None
        day_month_map = SSF_CALENDAR.day_month_map[self.calendar_code]
        if locale_name not in day_month_map:
            return None
        days = []
        dmm = day_month_map[locale_name]
        for day in (6, 0, 1, 2, 3, 4, 5):       # Start with SUN
            days.append((dmm[day].ddd, dmm[day].dddd))
        return days

    def __init__(self, calendar=SYSTEM_DEFAULT):
        if calendar is None:
            calendar = SSF_CALENDAR.SYSTEM_DEFAULT  # 00
        self.calendar_code = calendar
        _calendar_converter = [None, None, None, self.to_japanese, self.to_taiwan, self.to_korean,
            self.to_hijri, self.to_thai_buddhist, self.to_jewish, None, None, None, None, None, self.to_lunar_x0e,
            None, None, self.to_lunar_x11, self.to_lunar_x12, self.to_chinese_lunar, None, None, None, 
            self.to_um_al_qura, None, None, None, None, None, None, None, None]
        self.converter = self.to_default
        try:
            converter = _calendar_converter[calendar]
            self.converter = converter or self.to_default
        except (IndexError, TypeError):
            if isinstance(calendar, int):
                raise ValueError(f"Calendar {calendar:02X} is not valid!")
            else:
                raise ValueError(f"Calendar {calendar} must be an integer!")

        def unescape(s):
            """Excel save as tsv escaped all '"' chars - undo that!"""
            if len(s) < 2:
                return s
            if s[0] == '"' and s[-1] == '"':
                return s[1:-1].replace('""', '"')
            return s

        if calendar not in SSF_CALENDAR.day_month_map:      # We use a lazy algorithm to load the calendars as needed
            for leap in (('', 0), ('_leap', SSF_CALENDAR._LEAP_MONTH_FLAG)):
                if leap[0] and calendar not in SSF_CALENDAR._has_leap_month:
                    continue
                day_month_file = os.path.join(os.path.dirname(__file__), f'daymonth{calendar:02X}{leap[0]}.tsv.gz')
                day_month_map = {}
                if os.path.isfile(day_month_file):
                    with gzip.open(day_month_file, 'rt', encoding='utf-8') as dmf:
                        day_month = dmf.read().splitlines()
                    month_number = []          # field index to month number
                    for dm in day_month[1:]:    # Skip heading
                        fields = dm.split('\t')
                        if fields[1][0] == '*':
                            continue        # Skip the local time/date rows
                        dmm = {}
                        for f, fd in enumerate(fields[2:]):       # Start with Mon/Jan
                            dddd, ddd, mmmm, mmm, mmmmm, m = unescape(fd).split(',')
                            if f >= len(month_number) and m.isdigit():  # Use first row to define the month number mapping
                                month_number.append(int(m))
                            if month_number[f]-1 not in dmm:
                                dmm[month_number[f]-1] = SimpleNamespace(dddd=dddd, ddd=ddd, mmmm=mmmm, mmm=mmm, mmmmm=mmmmm)
                        # If we start with anything but January, then we need to move the days to the proper place
                        if month_number[0] != 1:
                            dmt = {}
                            for i in range(7):
                                dmt[i] = SimpleNamespace(dddd=dmm[month_number[i]-1].dddd,
                                                         ddd=dmm[month_number[i]-1].ddd)
                            for i in range(7):
                                dmm[i].dddd = dmt[i].dddd
                                dmm[i].ddd = dmt[i].ddd
                        day_month_map[fields[1]] = dmm
                    SSF_CALENDAR.day_month_map[calendar + leap[1]] = day_month_map

    def to_local(self, ymd):
        """Convert a tuple containing (year, month, day) to a SimpleNamespace containing (year, month, day, isleap, era)"""
        return self.converter(ymd)

class SSF_LOCALE:
    """Handle locale support for SSF.  This shouldn't be used directly."""
    lcid_map = None             # Language ID to Language tag, like 0x409 -> en-US
    dbnum_map = None            # "DBNum,locale" to [str of digits (0-9), 10, 100, 1000, etc]
    numbers_map = None          # xx to [str of digits (0-9), 10, 100, 1000, etc]
    am_pm_map = None            # locale to ('AM', 'PM')
    # day_month_map = None        # locale to [('Monday', 'Mon', 'January', 'Jan', 'J'), ('Tuesday', ...), ...]
    era_map = None              # locale to [SimpleNamespace(dt, g, gg, ggg), ...]
    table_map = None            # locale to dict(N=formatN, M=formatM, ...)
    currency_map = None         # country code to currency
    lcid_reverse_map = None
    lcid_max = 0
    MAX_AMPM=6      # Max chars in "Morning" or "Afternoon", else we use "AM/PM"
    GANNEN='元'                 # Issue #9
    lc_all_map = None           # Issue #10

    def __init__(self, locale=None, locale_support=True, locale_currency=True, decimal_separator=None, thousands_separator=None, calendar_code=None):
        decimal.setcontext(decimal.Context(rounding=decimal.ROUND_HALF_UP))
        self.currency_symbol='$'
        self.mon_decimal_point=decimal_separator or '.'
        self.mon_thousands_sep=thousands_separator or ','
        self.mon_grouping=[3, 0]
        self.positive_sign=''
        self.negative_sign='-'
        self.int_frac_digits=2
        self.frac_digits=2
        self.p_cs_precedes=1
        self.p_sep_by_space=0
        self.n_cs_precedes=1
        self.n_sep_by_space=0
        self.p_sign_posn=3
        self.n_sign_posn=0
        self.decimal_point=decimal_separator or '.'
        self.thousands_sep=thousands_separator or ','
        self.grouping=[3, 0]
        self.plus_sign='+'
        self.minus_sign='-'
        self.percent_sign='%'
        self.time_separator=':'
        self.exponential='E'
        self.time_format='h:mm:ss AM/PM'
        self.short_date_format='m/dd/yyyy'
        self.long_date_format='dddd, mmmm dd, yyyy'
        self.locale = None
        self.locale_name = 'local'
        self.dbnum = None
        self.numbers_xx = None
        self.text_direction = 'ltr'
        self.am = 'AM'      # https://github.com/SheetJS/ssf/issues/8
        self.pm = 'PM'
        self.a = 'A'
        self.p = 'P'
        self.gannen = 1     # Issue #9
        self.days = []
        for day in (6, 0, 1, 2, 3, 4, 5):       # Start with SUN
            self.days.append([calendar.day_abbr[day], calendar.day_name[day]])
        self.months = []
        for month in range(1, 12+1):
            self.months.append([calendar.month_abbr[month][0], calendar.month_abbr[month], calendar.month_name[month]])
        self.months_leap = self.months
        if locale_support:
            if SSF_LOCALE.currency_map is None:
                currency_file = os.path.join(os.path.dirname(__file__), 'currencies.json')
                SSF_LOCALE.currency_map = {}
                if os.path.isfile(currency_file):
                    with open(currency_file, 'r', encoding='utf-8') as cf:
                        currencies = json.load(cf)
                    for country_name, attr in currencies.items():
                        if 'abbreviation' not in attr:
                            continue        # Skip the 'comment'
                        SSF_LOCALE.currency_map[attr['abbreviation']] = attr['currency']    # e.g. US to USD

            if SSF_LOCALE.table_map is None:
                table_file = os.path.join(os.path.dirname(__file__), 'localize_table.yaml')
                SSF_LOCALE.table_map = {}
                if os.path.isfile(table_file):
                    with open(table_file, 'r', encoding='utf-8') as tf:
                        SSF_LOCALE.table_map = yaml.safe_load(tf)

            if SSF_LOCALE.era_map is None:
                era_file = os.path.join(os.path.dirname(__file__), 'eras.tsv')
                SSF_LOCALE.era_map = {}
                if os.path.isfile(era_file):
                    with open(era_file, 'r', encoding='utf-8') as ef:
                        eras = ef.read().splitlines()
                    ploc = None
                    ea = []
                    for e in eras[1:]:    # Skip heading
                        loc, dt, g, gg, ggg = e.split('\t')
                        if ploc and loc != ploc:
                            SSF_LOCALE.era_map[ploc] = ea
                            ea = []
                        ea.append(SimpleNamespace(dt=date_parse(dt).date(), g=g, gg=gg, ggg=ggg))
                        ploc = loc
                    SSF_LOCALE.era_map[ploc] = ea

            # Handled by SSF_CALENDAR now
            #if SSF_LOCALE.day_month_map is None:
                #day_month_file = os.path.join(os.path.dirname(__file__), 'daymonth.tsv')
                #SSF_LOCALE.day_month_map = {}
                #if os.path.isfile(day_month_file):
                    #with open(day_month_file, 'r', encoding='utf-8') as dmf:
                        #day_month = dmf.read().splitlines()
                    #for dm in day_month[1:]:    # Skip heading
                        #fields = dm.split('\t')
                        #dmm = []
                        #for fd in fields[2:]:       # Start with Mon/Jan
                            #dddd, ddd, mmmm, mmm, mmmmm = fd.split(',')
                            #dmm.append(SimpleNamespace(dddd=dddd, ddd=ddd, mmmm=mmmm, mmm=mmm, mmmmm=mmmmm))
                        #SSF_LOCALE.day_month_map[fields[1]] = dmm

            if SSF_LOCALE.am_pm_map is None:
                am_pm_file = os.path.join(os.path.dirname(__file__), 'ampm.tsv')
                SSF_LOCALE.am_pm_map = {}
                if os.path.isfile(am_pm_file):
                    with open(am_pm_file, 'r', encoding='utf-8') as af:
                        am_pm = af.read().splitlines()
                    for ap in am_pm[1:]:    # Skip heading
                        lcid, loc, am, pm = ap.split('\t')
                        SSF_LOCALE.am_pm_map[loc] = (am, pm)

            if SSF_LOCALE.numbers_map is None:
                numbers_file = os.path.join(os.path.dirname(__file__), 'numbers.tsv')
                SSF_LOCALE.numbers_map = {}
                if os.path.isfile(numbers_file):
                    with open(numbers_file, 'r', encoding='utf-8') as nf:
                        numbers = nf.read().splitlines()
                    for n in numbers[1:]:    # Skip heading
                        n_split = n.split('\t')
                        key = int(n_split[0], 16)
                        SSF_LOCALE.numbers_map[key] = n_split[2:]

            if SSF_LOCALE.dbnum_map is None:
                dbnum_file = os.path.join(os.path.dirname(__file__), 'dbnum.tsv')
                SSF_LOCALE.dbnum_map = {}
                if os.path.isfile(dbnum_file):
                    with open(dbnum_file, 'r', encoding='utf-8') as df:
                        dbnum = df.read().splitlines()
                    for db in dbnum[1:]:    # Skip heading
                        db_split = db.split('\t')
                        key = f'{db_split[0]},{db_split[2]}'
                        SSF_LOCALE.dbnum_map[key] = db_split[4:]

            def_locale = default_locale() or 'en-US'

            if SSF_LOCALE.lcid_map is None:
                lcid_file = os.path.join(os.path.dirname(__file__), 'lcid.tsv')
                SSF_LOCALE.lcid_map = {}      # Map from like 0x409 to 'en-US'
                SSF_LOCALE.lcid_reverse_map = {}
                if os.path.isfile(lcid_file):
                    with open(lcid_file, 'r', encoding='utf-8') as lf:
                        lcid = lf.read().splitlines()
                    lcid.append(f'0\t{def_locale}')     # Add a mapping for 0 for 'system default'
                    for lc in lcid[1:]:     # Skip heading
                        l_id, l_t = lc.split('\t')
                        i_id = int(l_id, 16)
                        l_t_s = l_t.strip()
                        SSF_LOCALE.lcid_map[i_id] = l_t_s
                        SSF_LOCALE.lcid_reverse_map[l_t_s] = i_id
                        SSF_LOCALE.lcid_max = max(SSF_LOCALE.lcid_max, i_id)

            if isinstance(locale, str) and locale.lower().endswith('-x-gannen'):     # Issue #9
                locale = locale[:-9]
                self.gannen = SSF_LOCALE.GANNEN
            locale = self.normalize_locale(locale) or def_locale
            if self.lcid_map and locale in self.lcid_map:
                locale = self.lcid_map[locale]

            sep = '-' if '-' in locale else '_'
            if locale_currency:
                if SSF_LOCALE.lc_all_map is None:       # Issue #13
                    lc_all_file = os.path.join(os.path.dirname(__file__), f'lc_all.tsv.gz')
                    SSF_LOCALE.lc_all_map = {}
                    if os.path.isfile(lc_all_file):
                        with gzip.open(lc_all_file, 'rt', encoding='utf-8') as laf:
                            lc_all = laf.read().splitlines()
                        keys = lc_all[0].split('\t')
                        for dm in lc_all[1:]:    # Skip heading
                            fields = dm.split('\t')
                            ln = fields[1]        # Locale name
                            lc_all_map = {}
                            for i, k in enumerate(keys[2:], start=2):   # Start after the locale
                                value = fields[i]
                                try:    # Convert ints back to int and lists back to list
                                    value = ast.literal_eval(value)
                                except Exception:  # If it's a string, then it's already ok
                                    pass
                                lc_all_map[k] = value
                            SSF_LOCALE.lc_all_map[ln] = lc_all_map
                if locale in SSF_LOCALE.lc_all_map:
                    for item, value in SSF_LOCALE.lc_all_map[locale].items():
                        setattr(self, item, value)      # Promote it to self
                else:           # Note: Most cases are handled by the code above, but try looking it up if we don't otherwise know it
                    try:
                        try:        # Issue #10
                            lcl.setlocale(lcl.LC_MONETARY, locale)
                        except Exception:       # v0.2.1: Handle unix-based locales by changing '-' to '_' and doing some lookups
                            locale2 = locale.replace('-', '_')
                            linux_lang_map = dict(nb="bokmal", ca="catalan", hr="croatian", cs="czech", da="danish", de="deutsch",
                                nl="dutch", et="estonian", fi="finnish", fr="french", gl="galician", el="greek", he="hebrew", hu="hungarian", 
                                it="italian", ja="japanese", ko="korean", lt="lithuanian", no="norwegian", nn="nynorsk", pl="polish", pt="portuguese", ro="romanian",
                                ru="russian", sk="slovak", sl="slovenian", es="spanish", sv="swedish", th="thai", tr="turkish")
                            linux_lang_map['is'] = 'icelandic'  # 'is' is a keyword
                            locale2 = linux_lang_map.get(locale2, locale2)
                            lcl.setlocale(lcl.LC_MONETARY, locale2)

                        conv = lcl.localeconv()     # pragma nocover
                        """{'int_curr_symbol': 'USD', 'currency_symbol': '$', 'mon_decimal_point': '.', 'mon_thousands_sep': ',', 'mon_grouping': [3, 0], 'positive_sign': '', 'negative_sign': '-', 'int_frac_digits': 2, 'frac_digits': 2, 'p_cs_precedes': 1, 'p_sep_by_space': 0, 'n_cs_precedes': 1, 'n_sep_by_space': 0, 'p_sign_posn': 3, 'n_sign_posn': 0}"""
                        if conv['currency_symbol'] == 'EUR':    # pragma nocover    # Issue #10
                            conv['currency_symbol'] = '\u20AC'  # real Euro symbol
                        for item, value in conv.items():    # pragma nocover
                            setattr(self, item, value)      # Promote it to self
                    except Exception:
                        pass
                    finally:
                        lcl.setlocale(lcl.LC_MONETARY, '') # Set it back to default

            self.locale_name = locale
            try:
                locale = Locale.parse(locale, sep=sep)
                self.locale = locale
                self.text_direction = locale.text_direction # ltr or rtl
            except Exception as e:
                #print(e)
                self.locale = None
                locale = None

            if SSF_LOCALE.am_pm_map and self.locale_name in SSF_LOCALE.am_pm_map:
                self.am, self.pm = SSF_LOCALE.am_pm_map[self.locale_name]
            elif locale:
                self.am = locale.day_periods['format']['abbreviated'].get('am', 'AM')
                if self.am.lower() == 'am':
                    am = locale.day_periods['format']['abbreviated'].get('morning1')
                    if am and len(am) <= SSF_LOCALE.MAX_AMPM:
                        self.am = am
                self.pm = locale.day_periods['format']['abbreviated'].get('pm', 'PM')
                if self.pm.lower() == 'pm':
                    pm = locale.day_periods['format']['abbreviated'].get('afternoon1')
                    if pm and len(pm) <= SSF_LOCALE.MAX_AMPM:
                        self.pm = pm
                self.a = locale.day_periods['format']['narrow'].get('am', 'A')
                self.p = locale.day_periods['format']['narrow'].get('pm', 'P')

            self.calendar_code = calendar_code
            self.calendar = SSF_CALENDAR(calendar_code)
            self.b2_calendar = SSF_CALENDAR(SSF_CALENDAR.HIJRI)

            #if SSF_LOCALE.day_month_map and self.locale_name in SSF_LOCALE.day_month_map:
                #self.days = []
                #self.months = []
                #dmm = SSF_LOCALE.day_month_map[self.locale_name]
                #for day in (6, 0, 1, 2, 3, 4, 5):       # Start with SUN
                    #self.days.append((dmm[day].ddd, dmm[day].dddd))
                #for month in range(0, 12):
                    #self.months.append((dmm[month].mmmmm, dmm[month].mmm, dmm[month].mmmm))
            self.days = self.calendar.day_names(self.locale_name)
            self.months = self.calendar.month_names(self.locale_name)
            self.months_leap = self.calendar.month_names(self.locale_name, isleap=True)
            from_map = False
            if self.days and self.months:
                from_map = True        # We got it covered
            elif locale:
                self.days = []
                self.months = []
                for day in (6, 0, 1, 2, 3, 4, 5):       # Start with SUN
                    self.days.append((locale.days['format']['abbreviated'][day], 
                                      locale.days['format']['wide'][day]))
                for month in range(1, 12+1):
                    self.months.append((locale.months['format']['narrow'][month],
                                        locale.months['format']['abbreviated'][month],
                                        locale.months['format']['wide'][month]))
                self.months_leap = self.months
            if locale:
                self.decimal_point = decimal_separator or self.get_number_symbols_property(locale, 'decimal')
                self.thousands_sep = thousands_separator or self.get_number_symbols_property(locale, 'group')
                self.plus_sign = self.get_number_symbols_property(locale, 'plusSign')
                self.minus_sign = self.get_number_symbols_property(locale, 'minusSign')
                self.percent_sign = self.get_number_symbols_property(locale, 'percentSign')
                self.time_separator = self.get_number_symbols_property(locale, 'timeSeparator')
                self.exponential = self.get_number_symbols_property(locale, 'exponential')
                self.time_format = locale.time_formats['medium'].pattern.replace('a', 'AM/PM')
                self.short_date_format = locale.date_formats['short'].pattern.replace('E', 'd'). \
                        replace('M', 'm')
                self.short_date_format = re.sub(r'\bd\b', 'dd', self.short_date_format)
                self.short_date_format = re.sub(r'\byy\b', 'yyyy', self.short_date_format)
                self.long_date_format = locale.date_formats['full'].pattern.replace('E', 'd'). \
                        replace('M', 'm')
                self.long_date_format = re.sub(r'\bd\b', 'dd', self.long_date_format)
                self.long_date_format = re.sub(r'\by\b', 'yyyy', self.long_date_format)
            #elif SSF_LOCALE.day_month_map and self.locale_name in SSF_LOCALE.day_month_map:
            elif from_map:
                if decimal_separator is not None:
                    self.decimal_point = decimal_separator
                if thousands_separator is not None:
                    self.thousands_sep = thousands_separator
            else:
                raise ValueError(f'Locale {self.locale_name} not found!')

    def get_number_symbols_property(self, locale, prop):
        """Get a property from the number symbols for the given locale"""
        # https://github.com/snoopyjc/ssf/issues/17
        old_val = locale.number_symbols.get(prop)
        new_val = locale.number_symbols.get('latn', {}).get(prop)
        return old_val or new_val

    def normalize_locale(self, locale):
        """Normalize locale based on examples in the lcid/locale map"""
        if locale is None:
            return locale
        if not isinstance(locale, str):
            return locale
        d = locale.find('.')
        if d >= 0:
            locale = locale[:d]
        a = locale.find('@')
        if a >= 0:
            locale = locale[:a]
        if locale[2:3] == '_':
            locale = locale[:2] + '-' + locale[3:].replace('-', '_')  # change en_US to en-US and ca-ES-valencia to ca-ES_valencia
        elif locale[3:4] == '_':
            locale = locale[:3] + '-' + locale[4:].replace('-', '_')  # change qps_plocm to qps-plocm
        lsplit = locale.split('-', 1)
        if len(lsplit) == 1:
            return lsplit[0].lower()        # If one word, make it lower-case like 'en'
        elif len(lsplit) == 2:      # Like en-US, ca-ES_valencia, or sr-Latn_CS
            rsplit = lsplit[1].replace('-', '_').split('_')
            if len(rsplit) == 1:        # like en-US or zh-Hans or qps-ploc
                if len(lsplit[1]) == 2:
                    return lsplit[0].lower() + '-' + lsplit[1].upper()    # en-US
                elif lsplit[0].lower() == 'qps':        # qps-plocm
                    return 'qps-' + lsplit[1].lower()
                else:
                    return lsplit[0].lower() + '-' + lsplit[1].title()    # zh-Hans
            elif len(rsplit) == 2:      # Like ff-Latn_SN or es-ES_tradnl
                if len(rsplit[0]) == 2:     # es-ES_tradnl
                    return lsplit[0].lower() + '-' + rsplit[0].upper() + '_' + rsplit[1].lower()
                else:                   # ff-Latn_SN
                    return lsplit[0].lower() + '-' + rsplit[0].title() + '_' + rsplit[1].upper()
        return locale


    #/*jshint +W086 */
    def commaify(self, s):        # Add commas to ints
        if not s:
            return ''
        if s[0] == ' ':     # Preserve but do not commaify leading spaces
            ls = len(s)
            ln = len(s.lstrip())
            df = ls-ln
            return s[:df] + self.commaify(s[df:])
        if self.locale is not None:
            locale_group = self.get_number_symbols_property(self.locale, 'group')
            if s[0] == '0':         # Special processing for leading zeros
                i = int('1'+s)      # Protect them with a leading '1', which we later remove
                result = format_decimal(i, locale=self.locale)
                result = re.sub(r'^1(?:' + re.escape(locale_group) + r')?(.*)$', r'\1', result)
            else:
                result = format_decimal(int(s), locale=self.locale)
            if self.thousands_sep != locale_group:
                result = result.replace(locale_group, self.thousands_sep)
            return result

        w = self.grouping[0] if len(self.grouping) >= 1 else 3
        sep = self.thousands_sep or ","
        if len(s) <= w:
            return s
        j = (len(s) % w)
        o = s[0:j]
        #for(; j!=s.length; j+=w) o+=(o.length > 0 ? "," : "") + s.substr(j,w);
        #for j in range(j, len(s), w):
        g = 1
        while j < len(s):
            o += (sep if len(o) > 0 else "") + s[j:j+w]
            w = self.grouping[g] if g < len(self.grouping) else w
            if w == 0:                  # Repeat prior grouping
                g -= 1
                w = self.grouping[g] if g < len(self.grouping) else 3
            elif w == lcl.CHAR_MAX:  # No more groupings
                o += s[j+w:]
                break
            g += 1
            j += w
        return o

class SSF:
    """Spreadsheet Formatter (number format). Formats values according to spreadsheet-style format codes.  If ``date1904``
    is True, then the base date is January 1, 1904, which was used on some spreadsheet programs for Mac.  The default (``False``),
    means that the base date is December 31, 1899 (which spreadsheet programs call the 1900 date system).  
    The ``dateNF`` if not None, replaces the default Short Date format of `m/dd/yyyy`.  The
    ``table`` if not None, replaces the entire translation from ints to formats table.
    
    The ``color_pre`` and ``color_post`` specify formats for values that are provided before and after the results that have
    a ``[ColorN]`` or color name e.g. ``[Red]`` specifier in the formats.  Any ``{}`` in the specified format are replaced by
    the specified color (in Title Case).  Any ``{rgb}`` in the formats are replaced with the hex color number (without a ``#``).

    If ``locale_support`` is True, then handle the international decimal point and thousands separator changes, and
    the language-based month names.  To use this, you can pass the ``locale`` here, or when you call ``ssf.format()``.
    If ``locale`` is None, then the default local locale is used.  The ``default_width``, if not None,
    gives the width to use on every ssf.format() call, if not otherwise specified. The ``decimal_separator``
    and ``thousands_separator`` are used to override the defaults as specified by the locale.  The ``errors``
    parameter specifies what to do on locale (and other) errors.  The default is to warn using the warnings
    module, then ignore the error.  The other choices are 'ignore', which completely ignores the error,
    'pounds', which fills the result with '#' characters, and 'raise', which will raise a ValueError exception.
    """
    #var make_ssf = function make_ssf(SSF){
    #SSF.version = '0.11.2';
    SSF_js_version = '0.11.2'       # This file is based on the JavaScript version

    def __init__(self, tzinfo=None, date1904=False, dateNF=None, table=None, color_pre=None, color_post=None,
            locale_support=True, locale=None, default_width=None, decimal_separator=None, thousands_separator=None,
            errors='warn'):
        
        self.color_pre = color_pre
        self.color_post = color_post
        self.fmt_calendar_code = None       # Calendar code from the format string (if any)
        self._errors = errors.lower().replace('pounds', 'pound') if errors else errors
        self._pound_sand = False
        self._default_width = default_width
        try:
            self.curl = SSF_LOCALE(locale_support=locale_support, locale=locale, decimal_separator=decimal_separator, thousands_separator=thousands_separator)
        except Exception as e:
            self._value_error(e)
            self.curl = SSF_LOCALE(locale_support=locale_support, locale=None, decimal_separator=decimal_separator, thousands_separator=thousands_separator)
        self.locale = self.curl.locale_name
        self.table_fmt = {}
        self._init_table(self.table_fmt)

        # We have to maintain 3 separate locales - the one specified in the SSF object creation (self.curl),
        # the one specified in the ssf.format() method (self.fmtl), and possibly one specified in the format
        # itself like [$-804]: (self.tmpl).  The self.fmtl is used for number formatting, while the self.tmpl is
        # used to get the names of days and months.

        self.tmpl = self.fmtl = self.curl   # Locale specified by the format
        self._locale_cache = {}
        self.locale_support = locale_support
        if locale_support:
            self._localize_table_from_locale(self.curl.locale_name)
            s_l = self.curl.locale_name
            s_l += decimal_separator if decimal_separator and decimal_separator != self.curl.decimal_point else ''
            s_l += thousands_separator if thousands_separator and thousands_separator != self.curl.thousands_sep else ''
            self._locale_cache[s_l] = self.curl
            if SSF_LOCALE.lcid_reverse_map and s_l in SSF_LOCALE.lcid_reverse_map:
                self._locale_cache[str(SSF_LOCALE.lcid_reverse_map[s_l])] = self.curl
        self._tzinfo = tzinfo
        if not tzinfo:
            self._tzinfo = tzlocal()
        self._opts = SimpleNamespace(date1904=date1904, dateNF=dateNF, table=table)
        self.gregorian_epoch = datetime(1582, 10, 15, tzinfo=timezone.utc)   # Start of the Gregorian Calendar
        self.basedate = datetime(1899, 12, 31, 0, 0, 0)
        basedate_utc = datetime(1899, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
        self.dnthresh = self.getTime(self.basedate)
        self.base1904 = datetime(1900, 3, 1, 0, 0, 0, tzinfo=self._tzinfo)

        self.rgb_colors = ['000000', 
                '000000', 'FFFFFF', 'FF0000', '00FF00', '0000FF', 'FFFF00', 'FF00FF', '00FFFF', '800000', '008000', # 1-10
                '000080', '808000', '800080', '008080', 'C0C0C0', '808080', '9999FF', '993366', 'FFFFCC', 'CCFFFF', # 11-20
                '660066', 'FF8080', '0066CC', 'CCCCFF', '000080', 'FF00FF', 'FFFF00', '00FFFF', '800080', '800000', # 21-30
                '008080', '0000FF', '00CCFF', 'CCFFFF', 'CCFFCC', 'FFFF99', '99CCFF', 'FF99CC', 'CC99FF', 'FFCC99', # 31-40
                '3366FF', '33CCCC', '99CC00', 'FFCC00', 'FF9900', 'FF6600', '666699', '969696', '003366', '339966', # 41-50
                '003300', '333300', '993300', '993366', '333399', '333333',                                         # 51-56
                ]

        self.color_map = dict(Black=1, White=2, Red=3, Green=4, Blue=5, Yellow=6, Magenta=7, Cyan=8)
        self.color_pat = r'\[(' + '|'.join([c for c in self.color_map]) + '|' + \
                '|'.join([r'Color\s*'+str(n) for n in range(1, len(self.rgb_colors)+1)]) + r')\]'
        for n in range(1, len(self.rgb_colors)):
            self.color_map[f'Color{n}'] = n

    def _value_error(self, e):
        if self._errors == 'warn':
            warnings.warn(e)
        elif self._errors == 'raise':
            raise ValueError(e)
        elif self._errors == 'pound' or '#' in self._errors:
            self._pound_sand = True

    def getTimezoneOffset(self, dt):
        """JavaScript style: Minutes from UTC"""
        try:
            return self._tzinfo.utcoffset(dt).total_seconds() / 60
        except OSError:     # Errno 22 if the date is too old
            return 0

    def getTime(self, dt):
        """JavaScript style: Milliseconds since an epoch"""
        dt_utc = dt.replace(tzinfo=timezone.utc)
        return (dt_utc - self.gregorian_epoch).total_seconds() * 1000 + self.getTimezoneOffset(dt)*60*1000

    @staticmethod
    def toPrecision(v, p):
        """Emulates JavaScript's flt.toPrecision(p)"""
        s = ''
        if v < 0:
            s = '-'
            v = -v
        np = math.floor(math.log10(v))+1 if v != 0 else 0
        pp = p - np
        rv = SSF.round(v, pp)      # Use our JavaScript-like rounding instead of the "round to even" that python gives
        result = format(rv, '-.%dg' % p)
        de = result.split('e')
        if '.' in de[0]:
            digits = len(de[0])-1
            de[0] += '0' * (p-digits)
        else:
            digits = len(de[0])
            if digits < p:
                de[0] += '.' + '0' * (p-digits)

        if len(de) == 2:        # We have an exponent
            de[1] = 'e' + re.sub(r'([+-])0(\d)', r'\1\2', de[1])       # Change e-09 to e-9
        else:
            de.append('')
        result = s + de[0] + de[1]      # Sign + mantissa + exponent
        #print(f'toPrecision({v}, {p}) (np={np}, pp={pp}, rv={rv}) = {result}')
        return result

    @staticmethod
    def round_to_precision(v, p):
        """Like toPrecision, except returns a float"""
        np = math.floor(math.log10(abs(v)))+1 if v != 0 else 0
        pp = p - np
        return SSF.round(v, pp)      # Use our JavaScript-like rounding instead of the "round to even" that python gives

    @staticmethod
    def round(number, places=0):
        """JavaScript style: Round 0.5 always up - not to even like python 3"""
        if isinstance(number, int):     # Issue #7
            if places >= 0:
                return number
        place = 10**places
        rounded = (int(number*place + (0.5 if number>=0 else -0.5)))/place
        if rounded == int(rounded):
            rounded = int(rounded)
        return rounded

    @staticmethod
    def to_str(v):
        """Emulate the ""+val in JavaScript.  If val is float but is an integer value, then the decimal is removed."""
        if isinstance(v, str):
            return v
        if isinstance(v, int):
            return str(v)
        if isinstance(v, float):
            av = abs(v)
            if av == 0.0:
                return '0'
            if av < 0.0001:     # issues/80
                return format_decimal(v, format='@@@@@@@@@@@@@@@', locale='en_US')
            elif av > 1E22:     # issues/80
                return format_decimal(v, format='@@@@@@@@@@@@@@@', locale='en_US')
            elif int(v) == v:
                return str(int(v))
            return str(v)
        return str(v)

    #function _strrev(x) { var o = "", i = x.length-1; while(i>=0) o += x.charAt(i--); return o; }
    @staticmethod
    def _strrev(x):
        return x[::-1]

    #function fill(c,l) { var o = ""; while(o.length < l) o+=c; return o; }
    @staticmethod
    def _fill(c,l):
        if not l:
            return ''
        return c * l

    #function pad0(v,d){var t=""+v; return t.length>=d?t:fill('0',d-t.length)+t;}
    @staticmethod
    def _pad0(v,d):
        t=SSF.to_str(v)
        return t if len(t)>=d else SSF._fill('0',d-len(t))+t

    #function pad_(v,d){var t=""+v;return t.length>=d?t:fill(' ',d-t.length)+t;}
    @staticmethod
    def _pad(v,d):
        t=SSF.to_str(v)
        if d is None:
            return t
        return t if len(t)>=d else SSF._fill(' ',d-len(t))+t

    #function rpad_(v,d){var t=""+v; return t.length>=d?t:t+fill(' ',d-t.length);}
    @staticmethod
    def _rpad(v,d):
        t=SSF.to_str(v)
        if d is None:
            return t
        return t if len(t)>=d else t+SSF._fill(' ',d-len(t))

    #function pad0r1(v,d){var t=""+Math.round(v); return t.length>=d?t:fill('0',d-t.length)+t;}
    @staticmethod
    def _pad0r1(v,d):
        # Issue #7 t=str(SSF.round(v))
        if isinstance(v, float) and abs(v) > 1e22:  # Issue #7
            t=SSF.to_str(v)  # Issue #7
        else:
            t=SSF.to_str(SSF.round(v))  # Issue #7
        return t if len(t)>=d else SSF._fill('0',d-len(t))+t

    #function pad0r2(v,d){var t=""+v; return t.length>=d?t:fill('0',d-t.length)+t;}
    @staticmethod
    def _pad0r2(v,d):
        t=SSF.to_str(v)
        return t if len(t)>=d else SSF._fill('0',d-len(t))+t

    #var p2_32 = Math.pow(2,32);
    _p2_32 = 2**32
    #function pad0r(v,d){if(v>p2_32||v<-p2_32) return pad0r1(v,d); var i = Math.round(v); return pad0r2(i,d); }
    @staticmethod
    def _pad0r(v,d):
        if(v>SSF._p2_32 or v<-SSF._p2_32):
            return SSF._pad0r1(v,d)
        i = SSF.round(v)
        return SSF._pad0r2(i,d)

    #function isgeneral(s, i) { i = i || 0; return s.length >= 7 + i && (s.charCodeAt(i)|32) === 103 && (s.charCodeAt(i+1)|32) === 101 && (s.charCodeAt(i+2)|32) === 110 && (s.charCodeAt(i+3)|32) === 101 && (s.charCodeAt(i+4)|32) === 114 && (s.charCodeAt(i+5)|32) === 97 && (s.charCodeAt(i+6)|32) === 108; }
    @staticmethod
    def _isgeneral(s, i=0):
        i = i or 0
        return s[i:i+7].lower() == 'general'

    #days = [
        #['Sun', 'Sunday'],
        #['Mon', 'Monday'],
        #['Tue', 'Tuesday'],
        #['Wed', 'Wednesday'],
        #['Thu', 'Thursday'],
        #['Fri', 'Friday'],
        #['Sat', 'Saturday']
        #]

    #months = [
        #['J', 'Jan', 'January'],
        #['F', 'Feb', 'February'],
        #['M', 'Mar', 'March'],
        #['A', 'Apr', 'April'],
        #['M', 'May', 'May'],
        #['J', 'Jun', 'June'],
        #['J', 'Jul', 'July'],
        #['A', 'Aug', 'August'],
        #['S', 'Sep', 'September'],
        #['O', 'Oct', 'October'],
        #['N', 'Nov', 'November'],
        #['D', 'Dec', 'December']
    #]

    def _init_table(self, t):
        t[0]=  'General'
        t[1]=  '0'
        t[2]=  '0.00'
        t[3]=  '#,##0'
        t[4]=  '#,##0.00'
        t[9]=  '0%'
        t[10]= '0.00%'
        t[11]= '0.00E+00'
        t[12]= '# ?/?'
        t[13]= '# ??/??'
        # t[14]= 'm/d/yy'
        t[14]= 'm/d/yyyy'       # https://github.com/SheetJS/ssf/issues/55
        t[15]= 'd-mmm-yy'
        t[16]= 'd-mmm'
        t[17]= 'mmm-yy'
        t[18]= 'h:mm AM/PM'
        t[19]= 'h:mm:ss AM/PM'
        t[20]= 'h:mm'
        t[21]= 'h:mm:ss'
        # t[22]= 'm/d/yy h:mm'
        t[22]= 'm/d/yyyy h:mm' # https://github.com/SheetJS/ssf/issues/55
        # t[37]= '#,##0 ;(#,##0)'
        # t[38]= '#,##0 ;[Red](#,##0)'
        # t[39]= '#,##0.00;(#,##0.00)'
        # t[40]= '#,##0.00;[Red](#,##0.00)'
        t[37]= '#,##0_);(#,##0)'        # https://github.com/SheetJS/ssf/issues/55
        t[38]= '#,##0_);[Red](#,##0)'   # https://github.com/SheetJS/ssf/issues/55
        t[39]= '#,##0.00_);(#,##0.00)'  # https://github.com/SheetJS/ssf/issues/55
        t[40]= '#,##0.00_);[Red](#,##0.00)' # https://github.com/SheetJS/ssf/issues/55
        t[45]= 'mm:ss'
        t[46]= '[h]:mm:ss'
        # t[47]= 'mmss.0'
        t[47]= 'mm:ss.0'        # https://github.com/SheetJS/ssf/issues/55
        t[48]= '##0.0E+0'
        t[49]= '@'
        t[56]= '"上午/下午 "hh"時"mm"分"ss"秒 "'


    #/* Defaults determined by systematically testing in Excel 2019 */

    #/* These formats appear to default to other formats in the table */
    _default_map = {}
    #defi = 0;

    #//  5 -> 37 ...  8 -> 40
    #for(defi = 5; defi <= 8; ++defi) default_map[defi] = 32 + defi;
    for _defi in range(5, 8+1):
        _default_map[_defi] = 32 + _defi

    #// 23 ->  0 ... 26 ->  0
    #for(defi = 23; defi <= 26; ++defi) default_map[defi] = 0;
    for _defi in range(23, 26+1):
        _default_map[_defi] = 0

    #// 27 -> 14 ... 31 -> 14
    #for(defi = 27; defi <= 31; ++defi) default_map[defi] = 14;
    for _defi in range(27,  31+1):
        _default_map[_defi] = 14

    #// 50 -> 14 ... 58 -> 14
    #for(defi = 50; defi <= 58; ++defi) default_map[defi] = 14;
    for _defi in range(50, 58+1):
        _default_map[_defi] = 14

    #// 59 ->  1 ... 62 ->  4
    #for(defi = 59; defi <= 62; ++defi) default_map[defi] = defi - 58;
    for _defi in range(59, 62+1):
        _default_map[_defi] = _defi - 58

    #// 67 ->  9 ... 68 -> 10
    #for(defi = 67; defi <= 68; ++defi) default_map[defi] = defi - 58;
    for _defi in range(67, 68+1):
        _default_map[_defi] = _defi - 58
    
    #// 72 -> 14 ... 75 -> 17
    #for(defi = 72; defi <= 75; ++defi) default_map[defi] = defi - 58;
    for _defi in range(72, 75+1):
        _default_map[_defi] = _defi - 58
    
    #// 69 -> 12 ... 71 -> 14
    #for(defi = 67; defi <= 68; ++defi) default_map[defi] = defi - 57;
    for _defi in range(67, 68+1):
        _default_map[_defi] = _defi - 57

    #// 76 -> 20 ... 78 -> 22
    #for(defi = 76; defi <= 78; ++defi) default_map[defi] = defi - 56;
    for _defi in range(76, 78+1):
        _default_map[_defi] = _defi - 56

    #// 79 -> 45 ... 81 -> 47
    #for(defi = 79; defi <= 81; ++defi) default_map[defi] = defi - 34;
    for _defi in range(79, 81+1):
        _default_map[_defi] = _defi - 34

    #// 82 ->  0 ... 65536 -> 0 (omitted)

    #/* These formats technically refer to Accounting formats with no equivalent */
    _default_str = {}

    #//  5 -- Currency,   0 decimal, black negative
    _default_str[5] = _default_str[63] = '"$"#,##0_);\\("$"#,##0\\)'
    #//  6 -- Currency,   0 decimal, red   negative
    _default_str[6] = _default_str[64] = '"$"#,##0_);[Red]\\("$"#,##0\\)'
    #//  7 -- Currency,   2 decimal, black negative
    _default_str[7] = _default_str[65] = '"$"#,##0.00_);\\("$"#,##0.00\\)'
    #//  8 -- Currency,   2 decimal, red   negative
    _default_str[8] = _default_str[66] = '"$"#,##0.00_);[Red]\\("$"#,##0.00\\)'

    #// 41 -- Accounting, 0 decimal, No Symbol
    _default_str[41] = '_(* #,##0_);_(* \\(#,##0\\);_(* "-"_);_(@_)'
    #// 42 -- Accounting, 0 decimal, $  Symbol
    _default_str[42] = '_("$"* #,##0_);_("$"* \\(#,##0\\);_("$"* "-"_);_(@_)'
    #// 43 -- Accounting, 2 decimal, No Symbol
    _default_str[43] = '_(* #,##0.00_);_(* \\(#,##0.00\\);_(* "-"??_);_(@_)'
    #// 44 -- Accounting, 2 decimal, $  Symbol
    _default_str[44] = '_("$"* #,##0.00_);_("$"* \\(#,##0.00\\);_("$"* "-"??_);_(@_)'

    @staticmethod
    def _pounds(width):
        if width is None:
            return '##########'
        return '#' * width

    @staticmethod
    def _frac(x, D, mixed):
        sgn = -1 if x < 0 else 1
        B = x * sgn
        P_2 = 0
        P_1 = 1
        P = 0
        Q_2 = 1
        Q_1 = 0
        Q = 0
        A = math.floor(B)
        while Q_1 < D:
            A = math.floor(B)
            P = A * P_1 + P_2
            Q = A * Q_1 + Q_2
            if (B - A) < 0.00000005: 
                break
            B = 1 / (B - A)
            P_2 = P_1; P_1 = P
            Q_2 = Q_1; Q_1 = Q

        if Q > D:
            if Q_1 > D:
                Q = Q_2
                P = P_2
            else:
                Q = Q_1
                P = P_1
        if not mixed:
            return [0, sgn * P, Q]
        q = math.floor(sgn * P/Q)       # pragma nocover - we never have mixed anymore
        return [q, sgn*P - q*Q, Q]      # pragma nocover

    def _parse_date_code(self,v,opts,b2=None, abstime=False):
        if v > 2958465 or (v < 0 and not abstime):      # https://github.com/SheetJS/ssf/issues/71
            return None
        dt = int(v)
        # issues/71 time = math.floor(86400 * (v - dt))
        time = int(86400 * (v - dt))        # issues/71
        dow=0
        dout=[]
        #out=SimpleNamespace(D=dt, T=time, u=86400*(v-dt)-time,y=0,m=0,d=0,H=0,M=0,S=0,q=0)
        out=SimpleNamespace(D=dt, T=time, u=86400*(v-dt)-time,y=0,m=0,d=0,H=0,M=0,S=0,q=0,L=False,e=None)
        if abs(out.u) < 1e-6:
            out.u = 0           # Truncate microseconds due to float rounding
        if opts and opts.date1904:
            dt += 1462
        if out.u > 0.9999:      # Correct for float rounding
            out.u = 0;
            time += 1
            if time == 86400:
                out.T = time = 0
                dt += 1
                out.D += 1
        elif out.u < -0.9999:      # Correct for float rounding
            out.u = 0;
            time -= 1
            if time <= -86400:
                out.T = time = 0
                dt -= 1
                out.D -= 1
        """Due to a bug in Lotus 1-2-3 which was propagated by Excel and other variants,
           the year 1900 is recognized as a leap year.  JS has no way of representing that
           abomination as a `Date`, so the easiest way is to store the data as a tuple.

           February 29, 1900 (date `60`) is recognized as a Wednesday.  Date `0` is treated
           as January 0, 1900 rather than December 31, 1899.
        """
        if dt == 60:
            # Issue #14 dout = [1317,10,29] if b2 else [1900,2,29]
            dout = [1900,2,29]  # Issue #14
            dow=3
        elif dt == 0:
            # Issue #14 dout = [1317,8,29] if b2 else [1900,1,0]
            dout = [1900,1,0]   # Issue #14
            dow=6
        else:
            if dt > 60:
                dt -= 1
            #/* 1 = Jan 1 1900 in Gregorian */
            d = date(1900, 1, 1)
            #d.setDate(d.getDate() + date - 1);
            d = d + timedelta(days=dt-1)
            #dout = [d.getFullYear(), d.getMonth()+1,d.getDate()];
            dout = [d.year, d.month, d.day]
            #dow = d.getDay();
            dow = (d.weekday()+1) % 7   # SUN=0, SAT=6
            if dt < 60:
                dow = (dow + 6) % 7     # Fixup day of week for the year 1900 bug, described above
            #if b2:
                #dow = SSF._fix_hijri(dt, d, dout)
        out.L, out.e = self._fix_calendar(dout, b2)
        
        out.y = dout[0]
        out.m = dout[1]
        out.d = dout[2]
        #71 out.S = time % 60
        #71 time = math.floor(time / 60)
        t = int(time / 60)      #71
        out.S = time - t * 60   #71
        time = t                #71
        #71 out.M = time % 60
        #71 time = math.floor(time / 60)
        t = int(time / 60)      #71
        out.M = time - t * 60   #71
        time = t                #71
        out.H = time
        out.q = dow
        return out

    #SSF.parse_date_code = parse_date_code;
    #var basedate = new Date(1899, 11, 31, 0, 0, 0);
    #var dnthresh = basedate.getTime();
    #var base1904 = new Date(1900, 2, 1, 0, 0, 0);

    def _datenum_local(self, v, date1904):
        #epoch = v.getTime();
        if not isinstance(v, datetime):
            if isinstance(v, date):
                v = datetime(v.year, v.month, v.day)
            elif isinstance(v, tm):
                v = datetime(self.basedate.year, self.basedate.month, self.basedate.day, v.hour, v.minute, v.second, v.microsecond)
            elif isinstance(v, timedelta):
                return v.total_seconds() / (24*60*60)

        if v.tzinfo is None:
            v = v.replace(tzinfo=self._tzinfo)
        epoch = self.getTime(v)
        if date1904:
            epoch -= 1461*24*60*60*1000
        elif v >= self.base1904:
            epoch += 24*60*60*1000

        #return (epoch - (dnthresh + (v.getTimezoneOffset() - basedate.getTimezoneOffset()) * 60000)) / (24 * 60 * 60 * 1000);
        return (epoch - (self.dnthresh + (self.getTimezoneOffset(v) - self.getTimezoneOffset(self.basedate)) * 60000)) / (24 * 60 * 60 * 1000)

    #/* The longest 32-bit integer text is "-4294967296", exactly 11 chars */
    #function general_fmt_int(v) { return v.toString(10); }
    @staticmethod
    def _general_fmt_int(v):        # pragma nocover
        return str(v)
    #SSF._general_int = general_fmt_int;
    _general_int = _general_fmt_int

    #/* ECMA-376 18.8.30 numFmt*/
    #/* Note: `toPrecision` uses standard form when prec > E and E >= -6 */
    def _general_fmt_num(self, v, width=None):
        #var trailing_zeroes_and_decimal = /(?:\.0*|(\.\d*[1-9])0+)$/;
        trailing_zeroes_and_decimal = r'(?:\.0*|(\.\d*[1-9])0+)$'
        def strip_decimal(o):
            #return (o.indexOf(".") == -1) ? o : o.replace(trailing_zeroes_and_decimal, "$1");
            return o if (o.find(".") == -1) else re.sub(trailing_zeroes_and_decimal, r"\1", o)

        #/* General Exponential always shows 2 digits exp and trims the mantissa */
        mantissa_zeroes_and_decimal = r'(?:\.0*|(\.\d*[1-9])0+)[Ee]'
        exp_with_single_digit = r'(E[+-])(\d)$'
        def normalize_exp(o):
            if o.find("E") == -1:
                return o
            o = re.sub(mantissa_zeroes_and_decimal,r"\1E", o)
            return re.sub(exp_with_single_digit,r"\g<1>0\2", o)

        #/* exponent >= -9 and <= 9 */
        def small_exp(v):
            w = (12 if v<0 else 11)
            p = 10
            ep = 5
            ep_o = ep
            if width is not None and width < w:
                w = width
                sign_width = 1 if v<0 else 0
                p = width - sign_width
                apv = abs(SSF.round_to_precision(v, max(p, 1)))
                V = math.floor(math.log10(apv)) if apv != 0 else 0
                if p > (V+1):       # If we need a spot for '.', then reserve it
                    p -= 1
                p = min(max(p, 1), 10)

                exp_width = 4       # Eg. "E+19"
                ep = width - sign_width - exp_width - 1     # -1 because this is the # places after the '.'
                if ep > 0:
                    ep -= 1      # A spot for the '.'
                ep_o = ep
                ep = min(max(ep, 0), 5)
            #o = strip_decimal(v.toFixed(12)); if(o.length <= w) return o;
            o = strip_decimal(f'{v:.12f}')
            if len(o) <= w:
                return o
            #o = v.toPrecision(10); if(o.length <= w) return o;
            #o = f'{v:.10g}'
            o = SSF.toPrecision(v, p)
            if len(o) <= w:
                result = o.replace(".", self.fmtl.decimal_point)
            else:
            #return v.toExponential(5);
                if ep_o < 0:
                    av = abs(v)
                    if av < 0.5:
                        return '-0' if v<0 else '0'
                    elif av < 9.5:
                        return str(SSF.round(v))        # Single digit
                #result = f'{v:.5e}'.replace(".", self.fmtl.decimal_point)
                result = ('{:.' + str(ep) + 'e}').format(v).replace(".", self.fmtl.decimal_point)
                # Python returns 1.2e+01 where JavaScript return 1.2e+1 so make this change:
                result = re.sub(r'(e[+-])0(\d)', r'\1\2', result)
            return result

        #/* exponent >= 11 or <= -10 likely exponential */
        def large_exp(v):
            #var o = strip_decimal(v.toFixed(11));
            o = strip_decimal(f'{v:.11f}')
            #return (o.length > (v<0?12:11) || o === "0" || o === "-0") ? v.toPrecision(6) : o;
            w = (12 if v<0 else 11)
            p = 6
            if width is not None and width < w:
                w = width
                sign_width = 1 if v<0 else 0
                exp_width = 4       # Eg. "E+19"
                p = width - sign_width - exp_width
                if p >= 2:
                    p -= 1      # A spot for the '.'
                if p < 1 and abs(v) < 1:
                    return '-0' if v<0 else '0'
                p = min(max(p, 1), 6)
            result = SSF.toPrecision(v, p) if (len(o) > w or o == "0" or o == "-0") else o
            return result.replace(".", self.fmtl.decimal_point)

        #function general_fmt_num_base(v) {
        #var V = Math.floor(Math.log(Math.abs(v))*Math.LOG10E), o;
        V = math.floor(math.log10(abs(v))) if v != 0 else 0

        if V >= -4 and V <= -1:     # 0.0001 - 0.9999
            #o = v.toPrecision(10+V);
            p = 10+V
            sign_width = 1 if v<0 else 0
            if width is not None and width <= 10+sign_width:
                p = width - sign_width - 1 + V
                p = min(max(p, 1), 10+V)
            o = SSF.toPrecision(v, p)
            if width is not None and len(o) > width:
                o = small_exp(v)
                #if len(o) > width:
                    #av = abs(v)
                    #if v < 0.5:
                        #o = '-0' if v<0 else '0'
                    #elif av < 9.5:
                        #o = str(SSF.round(v))        # Single digit
        elif abs(V) <= 9:
            o = small_exp(v)
        elif V == 10 and (width is None or width >= 12):
            #o = v.toFixed(10).substr(0,12)
            o = f'{v:.10f}'[0:12]
        else:
            o = large_exp(v)

        result = strip_decimal(normalize_exp(o.upper()))
        if width is not None and len(result) > width:
            result = '#' * width
        return result.replace(".", self.fmtl.decimal_point).replace("E", self.fmtl.exponential).\
                replace("-", self.fmtl.minus_sign).replace("+", self.fmtl.plus_sign)

        #return general_fmt_num_base;

    _general_num = _general_fmt_num

    """
        "General" rules:
        - text is passed through ("@")
        - booleans are rendered as TRUE/FALSE
        - "up to 11 characters" displayed for numbers
        - Default date format (code 14) used for Dates

        The display depends on the width of the cell, if specified
    """
    def _general_fmt(self, v, opts, width=None, text_fmt=False, align=None):
        def align_it(s, width, align):
            if width is None:
                return s
            ls = len(s)
            if ls >= width:
                return s
            al = align.lower()
            if al == 'center':
                return SSF._rpad(SSF._pad(s, ls+math.ceil((width-ls)/2)), width)
            elif al == 'left':
                return SSF._rpad(s, width)
            else:   # right
                return SSF._pad(s, width)

        #switch(typeof v) {
        #case 'string': return v;
        if isinstance(v, str):
            return align_it(v, width, align or 'left')
        #case 'boolean': return v ? "TRUE" : "FALSE";
        if isinstance(v, bool):     # pragma nocover - bool is handled elsewhere
            if width is None:
                return ("FALSE", "TRUE")[v]
            elif v:         # Center it
                if width >= 4:
                    return align_it("TRUE", width, align or 'center')
                return '#' * width
            else:
                if width >= 5:
                    return align_it("FALSE", width, align or 'center')
                return '#' * width
        #case 'number': return (v|0) === v ? v.toString(10) : general_fmt_num(v);
        if isinstance(v, timedelta):
            v = v.total_seconds() / (24*60*60)
        if (isinstance(v, int) or (isinstance(v, float) and int(v) == v)) and (-2147483648 <= v <= 2147483647):
            result = SSF.to_str(v)
            if width is None or len(result) <= width:
                return align_it(result, width, align or ('left' if text_fmt else 'right'))
        if isinstance(v, float) or isinstance(v, int):
            return align_it(self._general_fmt_num(v, width), width, align or ('left' if text_fmt else 'right'))
        #case 'undefined': return "";
        #case 'object':
            #if(v == null) return "";
        if v is None:
            return SSF._fill(' ', width)
        #if(v instanceof Date) return format(14, datenum_local(v, opts && opts.date1904), opts);
        if isinstance(v, date) and not isinstance(v, datetime):
            v = datetime(v.year, v.month, v.day)
        if isinstance(v, tm):
            v = datetime(self.basedate.year, self.basedate.month, self.basedate.day, v.hour, v.minute, v.second, v.microsecond)
        if isinstance(v, datetime):
            if text_fmt:      # Text format
                return self.format('@', self._datenum_local(v, opts and opts.date1904), width, align=align)
            return self.format(14, self._datenum_local(v, opts and opts.date1904), width, align=align)
        #throw new Error("unsupported value in General format: " + v);
        self._value_error("unsupported value in General format: " + str(v))

    _general = _general_fmt

    def _fix_calendar(self, o, b2):
        if self.fmt_calendar_code:
            sns = self.tmpl.calendar.to_local(o)
            o[0] = sns.year
            o[1] = sns.month
            o[2] = sns.day
            return (sns.isleap, sns.era)
        elif b2:
            sns = self.tmpl.b2_calendar.to_local(o)
            o[0] = sns.year
            o[1] = sns.month
            o[2] = sns.day
            return (sns.isleap, sns.era)
        return (False, None)                # Not year with leap-month and no era number
      
    #@staticmethod
    #def _fix_hijri(dt,d, o):
      #o[0] -= 581;
      #var dow = date.getDay();
      #dow = (d.weekday()+1) % 7   # SUN=0, SAT=6
      # if d < 60:
      #if dn < 60:           # https://github.com/SheetJS/ssf/issues/58
          #dow = (dow + 6) % 7
      #return dow
    
    #var THAI_DIGITS = "\u0E50\u0E51\u0E52\u0E53\u0E54\u0E55\u0E56\u0E57\u0E58\u0E59".split("");
    #/*jshint -W086 */
    def _write_date(self, type, fmt, val, ss0):
        o=""
        ss=0
        tt=0
        y = val.y
        outl = 0
        out = 0

        def era_data(dt, era_no=None):
            """Get the era data (e, g, gg, ggg) for a the era given by the given date.  Return year if not found"""
            locale_name = self.tmpl.locale_name if era_no is None else 'ja-JP'
            era = SSF_LOCALE.era_map.get(locale_name) if SSF_LOCALE.era_map else None
            result = (dt.year, '', '', '')        # Issue #1
            if not era:
                return result
            if era_no is not None:
                e = era[era_no]
                result = (dt.year, e.g, e.gg, e.ggg)
                if result[0] == 1:
                    result (self.tmpl.gannen, e.g, e.gg, e.ggg)
                return result

            for e in era:
                if dt >= e.dt:
                    result = ((dt.year - e.dt.year)+1, e.g, e.gg, e.ggg)    # Issue #9
                    if result[0] == 1:      # Issue #9: Gannen year
                        result = (self.tmpl.gannen, e.g, e.gg, e.ggg)
                else:
                    return result
            return result

        #switch(type) {
        #case 98: /* 'b' buddhist year */
        if type == 98:
            y = val.y + 543;
            #/* falls through */
            type = 121
        #case 121: /* 'y' year */
        if type == 121:
                #switch(fmt.length) {
                        #case 1: case 2: out = y % 100; outl = 2; break;
                        #default: out = y % 10000; outl = 4; break;
                #} break;
            if len(fmt) in (1, 2):
                out = y % 100
                outl = 2
            else:
                out = y % 10000
                outl = 4
            if val.e is not None:       # Era dates - suppress leading zeros
                outl = len(str(out))
        elif type == 103:      # 'g': Emperor reign year (https://taiken.co/single/understanding-the-years-based-on-japanese-eras/)
            _, *g = era_data(date(y, val.m, max(val.d, 1)), val.e)     # 'max' is to handle the potential 1/0/1900
            lg = min(len(fmt), 3)
            return g[lg-1]
        #case 109: /* 'm' month */
        elif type == 109:
                #switch(fmt.length) {
                    #case 1: case 2: out = val.m; outl = fmt.length; break;
                    #case 3: return months[val.m-1][1];
                    #case 5: return months[val.m-1][0];
                    #default: return months[val.m-1][2];
                #} break;
            if len(fmt) in (1, 2):
                out = val.m
                outl = len(fmt)
            elif len(fmt) == 3:
                return (self.tmpl.months_leap[val.m-1] if val.L else self.tmpl.months[val.m-1])[1]
            elif len(fmt) == 5:
                return (self.tmpl.months_leap[val.m-1] if val.L else self.tmpl.months[val.m-1])[0]
            else:
                return (self.tmpl.months_leap[val.m-1] if val.L else self.tmpl.months[val.m-1])[2]
        #case 100: /* 'd' day */
        elif type == 100:
                #switch(fmt.length) {
                        #case 1: case 2: out = val.d; outl = fmt.length; break;
                        #case 3: return days[val.q][0];
                        #default: return days[val.q][1];
                #} break;
            if len(fmt) in (1, 2):
                out = val.d
                outl = len(fmt)
            elif len(fmt) == 3:
                return self.tmpl.days[val.q][0]
            else:
                return self.tmpl.days[val.q][1]
        #case 104: /* 'h' 12-hour */
        elif type == 104:
                #switch(fmt.length) {
                        #case 1: case 2: out = 1+(val.H+11)%12; outl = fmt.length; break;
                        #default: throw 'bad hour format: ' + fmt;
                #} break;
            if len(fmt) in (1, 2):
                out = 1+(val.H+11)%12
                outl = len(fmt)
            else:
                self._value_error('bad hour format: ' + fmt)
        #case 72: /* 'H' 24-hour */
        elif type == 72:
                #switch(fmt.length) {
                        #case 1: case 2: out = val.H; outl = fmt.length; break;
                        #default: throw 'bad hour format: ' + fmt;
                #} break;
            if len(fmt) in (1, 2):
                out = val.H
                outl = len(fmt)
            else:
                self._value_error('bad hour format: ' + fmt)
        #case 77: /* 'M' minutes */
        elif type == 77:
                #switch(fmt.length) {
                        #case 1: case 2: out = val.M; outl = fmt.length; break;
                        #default: throw 'bad minute format: ' + fmt;
                #} break;
            if len(fmt) in (1, 2):
                out = val.M
                outl = len(fmt)
            else:
                self._value_error('bad minute format: ' + fmt)

        #case 115: /* 's' seconds */
        elif type == 115:
                        #if(fmt != 's' && fmt != 'ss' && fmt != '.0' && fmt != '.00' && fmt != '.000') throw 'bad second format: ' + fmt;
            if fmt not in ('s', 'ss', '.0', '.00', '.000'):
                self._value_error('bad second format: ' + fmt)
                        #if(val.u === 0 && (fmt == "s" || fmt == "ss")) return pad0(val.S, fmt.length);
            if val.u == 0 and fmt in ('s', 'ss'):
                return SSF._pad0(val.S, len(fmt))
                        #if(ss0 >= 2) tt = ss0 === 3 ? 1000 : 100;
            if ss0 >= 2:
                tt = 1000 if ss0 == 3 else 100
            else:
                        #else tt = ss0 === 1 ? 10 : 1;
                tt = 10 if ss0 == 1 else 1
                    #ss = Math.round((tt)*(val.S + val.u));
            ss = SSF.round(tt*(val.S + val.u))
                    #if(ss >= 60*tt) ss = 0;
            if ss >= 60*tt:
                ss = 0
                    #if(fmt === 's') return ss === 0 ? "0" : ""+ss/tt;
            if fmt == 's':
                return "0" if ss == 0 else SSF.to_str(ss/tt)
                    #o = pad0(ss,2 + ss0);
            o = SSF._pad0(ss, 2+ss0)
                    #if(fmt === 'ss') return o.substr(0,2);
            if fmt == 'ss':
                return o[0:2]
                    #return "." + o.substr(2,fmt.length-1);
            return '.' + o[2:(2+len(fmt)-1)]
        #case 90: /* 'Z' absolute time */
        elif type == 90:
                #switch(fmt) {
                    #case '[h]': case '[hh]': out = val.D*24+val.H; break;
                    #case '[m]': case '[mm]': out = (val.D*24+val.H)*60+val.M; break;
                    #case '[s]': case '[ss]': out = ((val.D*24+val.H)*60+val.M)*60+Math.round(val.S+val.u); break;
                    #default: throw 'bad abstime format: ' + fmt;
                #} outl = fmt.length === 3 ? 1 : 2; break;
            if fmt in ('[h]', '[hh]'):
                out = val.D*24+val.H
            elif fmt in ('[m]', '[mm]'):
                out = (val.D*24+val.H)*60+val.M
            elif fmt in ('[s]', '[ss]'):
                # WRONG: out = ((val.D*24+val.H)*60+val.M)*60+round(val.S+val.u)
                out = ((val.D*24+val.H)*60+val.M)*60+val.S
            else:
                self._value_error('bad abstime format: ' + fmt)
            outl = 1 if len(fmt) == 3 else 2
        #case 101: /* 'e' era */
        elif type == 101:
                #out = y; outl = 1; break;
            #out = y
            #outl = 1
            e, *_ = era_data(date(y, val.m, max(val.d, 1)), val.e)     # The 'max' is because the date could be 1/0/1900
            out = e
            outl = len(fmt)
        #var outstr = outl > 0 ? pad0(out, outl) : "";
        outstr = SSF._pad0(out, outl) if outl > 0 else ""
        return outstr

    def _write_num(self, type, fmt, val):

        # issues/50 pct1 = r'%'

        # issues/50 def write_num_pct(type, fmt, val):  
            # issues/50 """The underlying number for the percentages should be physically shifted"""
            # issues/50 #var sfmt = fmt.replace(pct1,""), mul = fmt.length - sfmt.length;
            # issues/50 sfmt = re.sub(pct1, "", fmt)
            # issues/50 mul = len(fmt) - len(sfmt)
            # issues/50 return self.write_num(type, sfmt, val * 10 ** (2*mul)) + SSF._fill(self.fmtl.percent_sign,mul);

        def write_num_cm(type, fmt, val):
            """Formats with multiple commas after the decimal point should be shifted by the
               appropiate multiple of 1000 (more magic)"""
            idx = len(fmt) - 1
            #while fmt.charCodeAt(idx-1) === 44) --idx;
            while idx > 0 and ord(fmt[idx-1]) == 44:    # ','
                idx -= 1
            #return write_num(type, fmt.substr(0,idx), val / Math.pow(10,3*(fmt.length-idx)));
            den = 10 ** (3*(len(fmt)-idx))
            if isinstance(val, int) and val % den == 0:
                return self._write_num(type, fmt[0:idx], val // den)
            else:
                return self._write_num(type, fmt[0:idx], val / den)

        def write_num_exp(fmt, val):
            """For exponents, get the exponent and mantissa and format them separately"""
            # issues/79 idx = fmt.find("E") - fmt.find(".") - 1
            pdot = fmt.find(".")        # issues/79
            if pdot >= 0:               # issues/79
                idx = fmt.find("E") - pdot - 1
            else:
                idx = 0
            # For the special case of engineering notation, "shift" the decimal
            #if(re.match(r'^#+0.0E\+0$', fmt)):
            m = re.match(r'^(?P<mantbd>[#?0]+[#?0])(?P<mantad>[.][#?0]*)?E(?P<exps>[-+])(?P<exp>[#?0]+)$', fmt)
            if m:
                if val == 0:
                    #return "0.0E+0"
                    mantad_fmt = m.group('mantad') or ''
                    return write_num_int('n', '0' * len(m.group('mantbd')), 0) + \
                           (write_num_flt('n', mantad_fmt, 0.0) if len(mantad_fmt) > 1 else \
                           (self.fmtl.decimal_point if len(mantad_fmt) == 1 else '')) + \
                           self.fmtl.exponential + \
                           ('+' if m.group('exps') == '+' else '') + \
                           write_num_int('n', m.group('exp'), 0)
                elif val < 0:
                    return self.fmtl.minus_sign + write_num_exp(fmt, -val)
                period = fmt.find("."); 
                if period == -1:
                    period=fmt.find('E')
                ee = math.floor(math.log10(val))%period
                if ee < 0:
                    ee += period
                #o = (val/Math.pow(10,ee)).toPrecision(idx+1+(period+ee)%period);
                o = SSF.toPrecision(val / 10**ee, idx+1+(period+ee)%period)
                if o.find("e") == -1:
                    fakee = math.floor(math.log10(val))
                    #if(o.indexOf(".") === -1) o = o.charAt(0) + "." + o.substr(1) + "E+" + (fakee - o.length+ee);
                    if o.find(".") == -1:
                        o = o[0] + "." + o[1:] + "E+" + str(fakee - len(o)+ee)
                    else:
                        o += "E+" + str(fakee - ee)
                    while o[0:2] == "0.":
                        #o = o.charAt(0) + o.substr(2,period) + "." + o.substr(2+period);
                        o = o[0] + o[2:period+2] + "." + o[2+period:]
                        #o = o.replace(/^0+([1-9])/,"$1").replace(/^0+\./,"0.");
                        o = re.sub(r'^0+([1-9])',r"\1", o)
                        o = re.sub(r'^0+\.',"0.", o)
                    o = re.sub(r'\+-',"-", o)
                
                #o = o.replace(/^([+-]?)(\d*)\.(\d*)[Ee]/,function($$,$1,$2,$3) { return $1 + $2 + $3.substr(0,(period+ee)%period) + "." + $3.substr(ee) + "E"; });
                def sub_f(m): 
                    return m.group(1) + m.group(2) + m.group(3)[0:(period+ee)%period] + "." + m.group(3)[ee:] + "E"
                o = re.sub(r'^([+-]?)(\d*)\.(\d*)[Ee]', sub_f, o)
            else:
                #o = val.toExponential(idx);
                o = ('{:.' + str(idx) + 'e}').format(val)
                # Python returns 1.2e+01 where JavaScript return 1.2e+1 so make this change:
                o = re.sub(r'(e[+-])0(\d)', r'\1\2', o)
            #if(fmt.match(/E\+00$/) && o.match(/e[+-]\d$/)) o = o.substr(0,o.length-1) + "0" + o.charAt(o.length-1);
            if re.search(r'E[+-]00$', fmt) and re.search(r'[Ee][+-]\d$', o):    # issues/73
                o = o[0:-1] + "0" + o[-1]
            #if(fmt.match(/E\-/) && o.match(/e\+/)) o = o.replace(/e\+/,"e");
            if re.search(r'E\-', fmt) and re.search(r'[Ee]\+', o):
                o = re.sub(r'[Ee]\+',"e", o)
            if pdot < 0:                # issues/79
                o = o.replace('.', '')  # issues/79
                e = fmt.find("E")-o.find("e")
            elif '.' not in o:          # issues/79
                o = o.replace('e', '.e') # issues/79
                e = fmt.find(".")-o.find(".")
            else:
                e = fmt.find(".")-o.find(".")
            if e > 0:           # issues/79
                o = hashq(fmt[:e]) + o
            return o.replace("e","E").replace("E", self.fmtl.exponential).replace("+", self.fmtl.plus_sign). \
                    replace("-", self.fmtl.minus_sign).replace('.', self.fmtl.decimal_point)

        # Fractions

        # issues/74 frac1 = re.compile(r'# (\?+)( ?)\/( ?)(\d+)')
        frac1 = re.compile(r'(?P<num>[#0?]+)\/(?P<den>\d+)')  # issues/74

        def write_num_f1(r, aval, sign):    # r is a match object from frac1
            """Handle a fraction from a float number whose absolute value is `aval` and has a specified
            denominator"""
            #var den = parseInt(r[4],10), rr = Math.round(aval * den), base = Math.floor(rr/den);
            # issues/74 r = (r.group(0), r.group(1), r.group(2), r.group(3), r.group(4))
            # issues/74 den = int(r[4])
            den = int(r.group('den'))
            rr = SSF.round(aval * den)
            # issues/74 base = math.floor(rr/den)
            # issues/74 myn = (rr - base*den)
            myn = rr        # issues/74
            myd = den
            #return sign + (base === 0 ? "" : ""+base) + " " + (myn === 0 ? fill(" ", r[1].length + 1 + r[4].length) : pad_(myn,r[1].length) + r[2] + "/" + r[3] + pad0(myd,r[4].length));
            # issues/74 return sign + ("" if base == 0 else str(base)) + " " + \
              # issues/74 (SSF._fill(" ", len(r[1]) + 1 + len(r[4])) if myn == 0 else SSF._pad(myn,len(r[1])) + r[2] + "/" + r[3] + SSF.pad0(myd,len(r[4])))
            ln = len(r.group('num'))
            ld = len(r.group('den'))
            return sign + (SSF._fill(" ", ln + 1 + ld) if myn == 0 else \
              SSF._pad(myn,ln) + "/" + SSF._pad0(myd,ld))        # issues/74

        def write_num_f2(r, aval, sign):    # r is a match object from frac1
            """Handle a fraction from an int number whose absolute value is `aval` and has a specified
            denominator"""
            #return sign + (aval === 0 ? "" : ""+aval) + fill(" ", r[1].length + 2 + r[4].length);
            # issues/74 return sign + ("" if aval == 0 else SSF.to_str(aval)) + SSF._fill(" ", len(r.group(1)) + 2 + len(r.group(4)))
            #return sign + SSF._fill(" ", len(r.group('num')) + 2 + len(r.group('den')))
            return write_num_f1(r, aval, sign)      # format('?/2', 1) == '2/2'

        #dec1 = r'^#*0*\.([0#]+)'
        dec1 = re.compile(r'^(?P<before>[#0?,]*)(?P<point>\.)(?P<after>[#0?]*)$')
        dec0 = re.compile(r'^(?P<before>[#0?,]*)(?P<point>)(?P<after>)$')      # Handle more generic formats
        closeparen = re.compile(r'\).*[0#]')
        phone = re.compile(r'\(###\) ###\\?-####')

        def hashq(st):
            """Fill an empty value with appropriate characters depending on the format given by ``st``:
                0 -> '0'
                ? -> ' '
                # -> ''
            """
            o = ""
            #for(var i = 0; i != str.length; ++i) switch((cc=str.charCodeAt(i))) {
            for i in range(len(st)):
                #switch((cc=str.charCodeAt(i))) {
                #case 35: break;
                ost = ord(st[i])
                if ost == 35:   # '#'
                    pass
                #case 63: o+= " "; break;
                elif ost == 63: # '?'
                    o += " "
                #case 48: o+= "0"; break;
                elif ost == 48: # '0'
                    o += "0"
                #default: o+= String.fromCharCode(cc);
                else:
                    o += st[i]
            #print(f'hashq({st}) = {o})')
            return o

        def rnd(val, d):
            dd = 10**d
            if isinstance(val, int) and d >= 0:
                return str(val)
            return SSF.to_str(SSF.round(val * dd)/dd)

        def dec(val, d):        # pragma nocover: no longer used
            _frac = val - math.floor(val)
            dd = 10**d
            if d < len(str(SSF.round(_frac * dd))):
                return 0
            return SSF.round(_frac * dd)

        def carry(val, d):      # pragma nocover: no longer used
            if d < len(str(SSF.round((val-math.floor(val))*10**d))):
                return 1
            return 0

        def flr(val):       # pragma nocover: no longer used
            if val < 2147483647 and val > -2147483648:
                return str(int(val) if val >= 0 else int(val-1))
            if int(val) == val:     # Try to match the javascript output for 123456822333330000
                o = f'{val:.15e}'
                m = re.match(r'([-]?)(\d)[.](\d*)e[+](\d+)', o)
                if m:       # Should always match, but be safe here!
                    digits = int(m.group(4))+1
                    o = m.group(2)+m.group(3)
                    return m.group(1) + o[:digits] + SSF._fill('0', digits-len(o))
            return str(math.floor(val))

        def substr(s, st, ln):      # JavaScript style      # pragma nocover: no longer used
            return s[st:st+ln]


        def write_num_flt(type, fmt, val):
            # For parentheses, explicitly resolve the sign issue:
            #if(type.charCodeAt(0) === 40 && !fmt.match(closeparen)) {
            if ord(type[0]) == 40 and not re.search(closeparen, fmt):   # pragma nocover - can't get here!
                #var ffmt = fmt.replace(/\( */,"").replace(/ \)/,"").replace(/\)/,"");
                ffmt = re.sub(r'\( *',"", fmt)
                ffmt = re.sub(r' \)',"", ffmt).replace(')',"")
                if val >= 0:
                    return write_num_flt('n', ffmt, val)
                return '(' + write_num_flt('n', ffmt, -val) + ')'
            
            # Helpers are used for:
            # - Percentage values
            # - Trailing commas
            # - Exponentials

            #if(fmt.charCodeAt(fmt.length - 1) === 44) return write_num_cm(type, fmt, val);
            if ord(fmt[-1]) == 44:
                return write_num_cm(type, fmt, val)
            # issues/50 #if(fmt.indexOf('%') !== -1) return write_num_pct(type, fmt, val);
            # issues/50 if fmt.find('%') != -1:
                # issues/50 return write_num_pct(type, fmt, val)
            #if(fmt.indexOf('E') !== -1) return write_num_exp(fmt, val);
            if fmt.find('E') != -1:
                return write_num_exp(fmt, val)

            #if(fmt.charCodeAt(0) === 36) return "$"+write_num_flt(type,fmt.substr(fmt.charAt(1)==' '?2:1),val);
            if ord(fmt[0]) == 36:   #'$'    # pragma nocover - can't get here!
                return "$"+write_num_flt(type, fmt[(2 if fmt[1:2]==' ' else 1):], val)

            aval = abs(val)
            sign = "-" if val < 0 else ""
            #if(fmt.match(/^00+$/)) return sign + pad0r(aval,fmt.length);
            if re.search(r'^00+$', fmt):
                return sign + SSF._pad0r(aval,len(fmt))
            if re.match(r'^[#?]+$', fmt):
                # issues/77 o = SSF.pad0r(val,0)
                o = SSF._pad0r(aval,0)       # issues/77
                if o == "0":
                    o = ""
                # issues/77 return o if len(o) > len(fmt) else hashq(fmt[:len(fmt)-len(o)]) + o
                return sign + (o if len(o) > len(fmt) else hashq(fmt[:len(fmt)-len(o)]) + o)    # issues/77
            
            # Fractions with known denominator are resolved by rounding

            #if((r = fmt.match(frac1))) return write_num_f1(r, aval, sign);
            r = re.search(frac1, fmt)
            if r:
                return write_num_f1(r, aval, sign)

            # A few special general cases can be handled in a very dumb manner

            #if(fmt.match(/^#+0+$/)) return sign + pad0r(aval,fmt.length - fmt.indexOf("0"));
            if re.match(r'^#+0+$', fmt):
                return sign + SSF._pad0r(aval,len(fmt) - fmt.find("0"))
            r = re.match(dec1, fmt)
            if not r:
                r = re.match(dec0, fmt)
            if r:
                comma = ',' in (r.group('before') or '')
                if comma:
                    fmt = fmt.replace(',', '')
                #o = rnd(val, r[1].length).replace(/^([^\.]+)$/,"$1."+hashq(r[1])).replace(/\.$/,"."+hashq(r[1])).replace(/\.(\d*)$/,function($$, $1) { return "." + $1 + fill("0", hashq(r[1]).length-$1.length); });
                after = r.group('after')
                o = rnd(aval, len(after))
                if o == '0':
                    sign = ''
                #o = re.sub(r'^([^\.]+)$',r"\1."+hashq(after), o)
                #o = re.sub(r'\.$',"."+hashq(after), o)
                if r.group('point'):
                    if '.' not in o:
                        o += '.'
                    #o = re.sub(r'\.(\d*)$', lambda m: "."+ m.group(1) + SSF._fill("0", len(hashq(after))-len(m.group(1))), o)
                    o = re.sub(r'\.(\d*)$', lambda m: "."+ m.group(1) + hashq(after[len(m.group(1)):]), o)
                    #return fmt.indexOf("0.") !== -1 ? o : o.replace(/^0\./,".");
                    result = o if fmt.find("0.") != -1 else re.sub(r'^0\.', ".", o)
                    e = fmt.find(".")-result.find(".")
                    if e > 0:           # https://github.com/SheetJS/ssf/issues/65
                        result = hashq(fmt[:e]) + result
                    if comma:
                        rd = result.find(".")
                        result = self.fmtl.commaify(result[:rd]) + self.fmtl.decimal_point + result[rd+1:]
                    else:
                        result = result.replace(".", self.fmtl.decimal_point)
                else:
                    result = o if fmt.find("0") != -1 else re.sub(r'^0', '', o)
                    e = len(fmt) - len(result)
                    if e > 0:           # https://github.com/SheetJS/ssf/issues/65
                        result = hashq(fmt[:e]) + result
                    if comma:
                        result = self.fmtl.commaify(result)
                return sign + result
            
            # The next few simplifications ignore leading optional sigils (`#`)

            #fmt = fmt.replace(/^#+([0.])/, "$1");
            fmt = re.sub(r'^#+([0.])', r'\1', fmt)
            #if((r = fmt.match(/^(0*)\.(#*)$/))) {
            r = re.match(r'^(0*)\.(#*)$', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #return sign + rnd(aval, r[2].length).replace(/\.(\d*[1-9])0*$/,".$1").replace(/^(-?\d*)$/,"$1.").replace(/^0\./,r[1].length?"0.":".");
                result = sign + rnd(aval, len(r.group(2)))
                result = re.sub(r'\.(\d*[1-9])0*$',r".\1", result)
                result = re.sub(r'^(-?\d*)$',r"\1.", result)
                m = re.match(r'^(-?)(\d*)(\..*)$', result)
                if m:       # https://github.com/SheetJS/ssf/issues/65
                    result = m.group(1) + SSF._fill('0', len(r.group(1))-len(m.group(2))) + m.group(2) + m.group(3)
                result = re.sub(r'^0\.',"0"+self.fmtl.decimal_point if len(r.group(1)) else self.fmtl.decimal_point, result)
                return result
            
            #if((r = fmt.match(/^#{1,3},##0(\.?)$/))) return sign + commaify(pad0r(aval,0));
            r = re.match(r'^#{1,3},##0(\.?)$', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                return sign + self.fmtl.commaify(SSF._pad0r(aval,0))
            #if((r = fmt.match(/^#,##0\.([#0]*0)$/))) {
            r = re.match(r'^#,##0\.([#0]*0)$', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #return val < 0 ? "-" + write_num_flt(type, fmt, -val) : commaify(""+(Math.floor(val) + carry(val, r[1].length))) + "." + pad0(dec(val, r[1].length),r[1].length);
                return "-" + write_num_flt(type, fmt, -val) if val < 0 \
                  else self.fmtl.commaify(SSF.to_str(math.floor(val) + carry(val, len(r.group(1))))) + self.fmtl.decimal_point + SSF._pad0(dec(val, len(r.group(1))),len(r.group(1)))
            #if((r = fmt.match(/^#,#*,#0/))) return write_num_flt(type,fmt.replace(/^#,#*,/,""),val);
            r = re.match(r'^#,#*,#0', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                return write_num_flt(type,re.sub(r'^#,#*,',"", fmt),val)

            # The `Zip Code + 4` format needs to treat an interstitial hyphen as a character

            #if((r = fmt.match(/^([0#]+)(\\?-([0#]+))+$/))) {
            r = re.match(r'^([0#]+)(\\?-([0#]+))+$', fmt)
            if r:                       # pragma nocover - covered by the general case
                o = SSF._strrev(write_num_flt(type, re.sub(r'[\\-]',"", fmt), val))
                ri = 0
                #return _strrev(_strrev(fmt.replace(/\\/g,"")).replace(/[0#]/g,function(x){return ri<o.length?o.charAt(ri++):x==='0'?'0':"";}));
                fmt1 = SSF._strrev(fmt.replace('\\',""))
                def sub_ri(m):
                    nonlocal ri
                    if ri < len(o):
                        ri += 1
                        return o[ri-1]
                    elif m.group(0) == '0':
                        return 0
                    return ""
                result = SSF._strrev(re.sub(r'[0#]',sub_ri, fmt1))
                return result
            
            # There's a better way to generalize the phone number and other formats in terms
            # of first drawing the digits, but this selection allows for more nuance

            if re.search(phone, fmt):
                o = write_num_flt(type, "##########", val)
                #return "(" + o.substr(0,3) + ") " + o.substr(3, 3) + "-" + o.substr(6);
                return "(" + o[0:3] + ") " + o[3:6] + "-" + o[6:]
            
            # The frac helper function is used for fraction formats (defined below)

            oa = ""
            #if((r = fmt.match(/^([#0?]+)( ?)\/( ?)([#0?]+)/))) {
            r = re.match(r'^([#0?]+)( ?)\/( ?)([#0?]+)', fmt)
            if r:
                ri = min(len(r.group(4)),7)
                ff = SSF._frac(aval, 10**ri-1, False)
                o = "" + sign
                oa = self._write_num("n", r.group(1), ff[1])
                if oa[-1] == " ":
                    oa = oa[0:-1] + "0"
                o += oa + r.group(2) + "/" + r.group(3)
                oa = SSF._rpad(ff[2],ri);
                if len(oa) < len(r.group(4)):
                    # issues/75 oa = hashq(r.group(4)[len(r.group(4))-len(oa):]) + oa
                    oa += hashq(r.group(4)[len(oa):])       # issues/75
                o += oa;
                return o
            
            #if((r = fmt.match(/^# ([#0?]+)( ?)\/( ?)([#0?]+)/))) {
            r = re.match(r'^# ([#0?]+)( ?)\/( ?)([#0?]+)', fmt) # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                ri = min(max(len(r.group(1)), len(r.group(4))),7)
                ff = SSF._frac(aval, 10**ri-1, True)
                #return sign + (ff[0]||(ff[1] ? "" : "0")) + " " + (ff[1] ? pad_(ff[1],ri) + r[2] + "/" + r[3] + rpad_(ff[2],ri): fill(" ", 2*ri+1 + r[2].length + r[3].length));
                return sign + (SSF.to_str(ff[0]) if ff[0] else ("" if ff[1] else "0")) + " " + \
                  (SSF._pad(ff[1],ri) + r.group(2) + "/" + r.group(3) + SSF._rpad(ff[2],ri) if ff[1] else SSF._fill(" ", 2*ri+1 + len(r.group(2) + r.group(3))))

            # The general class `/^[#0?]+$/` treats the '0' as literal, '#' as noop, '?' as space

            #if((r = fmt.match(/^[#0?]+$/))) {
            r = re.match(r'^[#0?]+$', fmt)  # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                # issues/77 o = SSF._pad0r(val, 0)
                o = SSF._pad0r(aval, 0)           # issues/77
                if len(fmt) <= len(o):
                    # issues/77 return o
                    return sign + o              # issues/77
                # issues/77 return hashq(fmt[:len(fmt)-len(o)]) + o
                return sign + hashq(fmt[:len(fmt)-len(o)]) + o      # issues/77
            
            #if((r = fmt.match(/^([#0?]+)\.([#0]+)$/))) {
            r = re.match(r'^([#0?]+)\.([#0]+)$', fmt)   # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #o = "" + val.toFixed(Math.min(r[2].length,10)).replace(/([^0])0+$/,"$1");
                o = ('{:.' + str(min(len(r.group(2)),10)) + 'f}').format(val)
                o = re.sub(r'([^0])0+$',r"\1", o)
                ri = o.find(".");
                lres = fmt.find(".") - ri
                rres = len(fmt) - len(o) - lres
                return hashq(fmt[:lres] + o + fmt[len(fmt)-rres:]).replace(".", self.fmtl.decimal_point)

            # The default cases are hard-coded.  (@snoopyjc: Not anymore!)

            #if((r = fmt.match(/^00,000\.([#0]*0)$/))) {
            r = re.match(r'^00,000\.([#0]*0)$', fmt)    # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                ri = dec(val, len(r.group(1)))
                #return val < 0 ? "-" + write_num_flt(type, fmt, -val) : commaify(flr(val)).replace(/^\d,\d{3}$/,"0$&").replace(/^\d*$/,function($$) { return "00," + ($$.length < 3 ? pad0(0,3-$$.length) : "") + $$; }) + "." + pad0(ri,r[1].length);
                if val < 0:
                    return "-" + write_num_flt(type, fmt, -val)

                result = self.fmtl.commaify(flr(val))
                result = re.sub(r'^(\d,\d{3})$',r"0\1", result)
                def sub_f(m):
                    lm = len(m.group(0))
                    return "00," + (SSF._pad0(0,3-lm) if lm < 3 else "") + m.group(0)

                result = re.sub(r'^\d*$',sub_f, result)
                result += self.fmtl.decimal_point + SSF._pad0(ri,len(r.group(1)))
                return result
            
            #switch(fmt) {
            #case "###,##0.00": return write_num_flt(type, "#,##0.00", val);
            if fmt == "###,##0.00":     # pragma nocover
                return write_num_flt(type, "#,##0.00", val)
            #case "###,###":
            #case "##,###":
            #case "#,###": var x = commaify(pad0r(aval,0)); return x !== "0" ? sign + x : "";
            if fmt in ("###,###", "##,###", "#,###"):       # pragma nocover
                x = self.fmtl.commaify(SSF._pad0r(aval,0))
                return sign + x if x != "0" else ""
            #case "###,###.00": return write_num_flt(type, "###,##0.00",val).replace(/^0\./,".");
            if fmt == "###,###.00":     # pragma nocover
                result = write_num_flt(type, "###,##0.00", val)
                return re.sub(r'^0\.', self.fmtl.decimal_point, result)
            #case "#,###.00": return write_num_flt(type, "#,##0.00",val).replace(/^0\./,".");
            if fmt == "#,###.00":       # pragma nocover
                result = write_num_flt(type, "#,##0.00", val)
                return re.sub(r'^0\.', self.fmtl.decimal_point, result)
            #default:
            #throw new Error("unsupported format |" + fmt + "|");
            self._value_error("unsupported format |" + fmt + "|")
            return ''

    # Integer Optimizations

        def write_num_cm2(type, fmt, val):
            idx = len(fmt) - 1;
            while idx > 0 and ord(fmt[idx-1]) == 44:    # ','
                idx -= 1
            den = 10**(3*(len(fmt)-idx))
            if val % den == 0:
                return self._write_num(type, fmt[:idx], val // den)
            else:
                return self._write_num(type, fmt[:idx], val / den)

        # issues/50 def write_num_pct2(type, fmt, val):
            # issues/50 sfmt = re.sub(pct1,"",fmt)
            # issues/50 mul = len(fmt) - len(sfmt)
            # issues/50 return self._write_num(type, sfmt, val * 10**(2*mul)) + SSF._fill(self.fmtl.percent_sign,mul)

        def write_num_exp2(fmt, val):
            # issues/79 idx = fmt.find("E") - fmt.find(".") - 1
            pdot = fmt.find(".")        # issues/79
            if pdot >= 0:               # issues/79
                idx = fmt.find("E") - pdot - 1
            else:
                idx = 0
            #if re.match(r'^#+0.0E\+0$', fmt):
            m = re.match(r'^(?P<mantbd>[#?0]+[#?0])(?P<mantad>[.][#?0]*)?E(?P<exps>[-+])(?P<exp>[#?0]+)$', fmt)
            if m:
                if val == 0:
                    #return "0.0E+0"
                    mantad_fmt = m.group('mantad') or ''
                    return write_num_int('n', '0' * len(m.group('mantbd')), 0) + \
                           (write_num_flt('n', mantad_fmt, 0.0) if len(mantad_fmt) > 1 else \
                           (self.fmtl.decimal_point if len(mantad_fmt) == 1 else '')) + \
                           self.fmtl.exponential + \
                           ('+' if m.group('exps') == '+' else '') + \
                           write_num_int('n', m.group('exp'), 0)
                elif val < 0:
                    return "-" + write_num_exp2(fmt, -val);
                period = fmt.find(".")
                if period == -1:
                    period=fmt.find('E')
                ee = math.floor(math.log10(val))%period
                if ee < 0: 
                    ee += period
                #o = (val/Math.pow(10,ee)).toPrecision(idx+1+(period+ee)%period);
                o = SSF.toPrecision(val/10**ee, idx+1+(period+ee)%period)
                #if(!o.match(/[Ee]/)) {
                if not re.search(r'[Ee]', o):
                    fakee = math.floor(math.log10(val))
                    # if(o.indexOf(".") === -1) o = o.charAt(0) + "." + o.substr(1) + "E+" + (fakee - o.length+ee);
                    # else o += "E+" + (fakee - ee);
                    if o.find(".") == -1:
                        o = o[0] + "." + o[1:] + "E+" + str(fakee - len(o)+ee)
                    else:
                        o += "E+" + str(fakee - ee)
                    o = re.sub(r'\+-',"-",o)
                
                #o = o.replace(/^([+-]?)(\d*)\.(\d*)[Ee]/,function($$,$1,$2,$3) { return $1 + $2 + $3.substr(0,(period+ee)%period) + "." + $3.substr(ee) + "E"; });
                def sub_f(m):
                    return m.group(1) + m.group(2) + m.group(3)[:(period+ee)%period] + \
                      "." + m.group(3)[ee:] + "E"
                o = re.sub(r'^([+-]?)(\d*)\.(\d*)[Ee]', sub_f, o)
            else:
                # o = val.toExponential(idx)
                o = ('{:.' + str(idx) + 'e}').format(val)
                # Python returns 1.2e+01 where JavaScript return 1.2e+1 so make this change:
                o = re.sub(r'(e[+-])0(\d)', r'\1\2', o)
            if re.search(r'E[+-]00$', fmt) and re.search(r'[Ee][+-]\d$', o):    # issues/73
                o = o[:-1] + "0" + o[-1]
            if re.search(r'E\-', fmt) and re.search(r'[Ee]\+', o):
                o = re.sub(r'[Ee]\+',"e", o)
            if pdot < 0:                # issues/79
                o = o.replace('.', '')  # issues/79
                e = fmt.find("E")-o.find("e")
            elif '.' not in o:          # issues/79
                o = o.replace('e', '.e') # issues/79
                e = fmt.find(".")-o.find(".")
            else:
                e = fmt.find(".")-o.find(".")
            if e > 0:           # issues/79
                o = hashq(fmt[:e]) + o
            return o.replace("e","E").replace(".", self.fmtl.decimal_point).replace("E", self.fmtl.exponential). \
                    replace("+", self.fmtl.plus_sign).replace("-", self.fmtl.minus_sign)

        def write_num_int(type, fmt, val):
            if not fmt:
                return ''
            if ord(type[0]) == 40 and not re.search(closeparen, fmt):   # pragma nocover - can't get here
                #var ffmt = fmt.replace(/\( */,"").replace(/ \)/,"").replace(/\)/,"");
                ffmt = re.sub(r'\( *',"",fmt).replace(' )',"").replace(')',"")
                if val >= 0: 
                    return write_num_int('n', ffmt, val)
                return '(' + write_num_int('n', ffmt, -val) + ')'
            
            if ord(fmt[-1]) == 44:  # ','
                return write_num_cm2(type, fmt, val)
            # issues/50 if fmt.find('%') != -1: 
                # issues/50 return write_num_pct2(type, fmt, val)
            if fmt.find('E') != -1: 
                return write_num_exp2(fmt, val)
            if ord(fmt[0]) == 36:   # pragma nocover - can't get here
                return "$"+write_num_int(type,fmt[2 if fmt[1:2]==' ' else 1:],val)
            aval = abs(val)
            sign = self.fmtl.minus_sign if val < 0 else ""
            if re.match(r'^00+$', fmt): 
                return sign + SSF._pad0(aval,len(fmt))
            if re.match(r'^[#?]+$', fmt):
                # issues/77  o = SSF.to_str(val)
                o = SSF.to_str(aval)        # issues/77
                if val == 0: 
                    o = ""
                # issues/77 return o if len(o) > len(fmt) else hashq(fmt[:len(fmt)-len(o)]) + o
                return sign + (o if len(o) > len(fmt) else hashq(fmt[:len(fmt)-len(o)]) + o)    # issues/77
            
            #if((r = fmt.match(frac1))) return write_num_f2(r, aval, sign);
            r = re.search(frac1, fmt)
            if r:
                return write_num_f2(r, aval, sign);
            #if(fmt.match(/^#+0+$/)) return sign + pad0(aval,fmt.length - fmt.indexOf("0"));
            if re.match(r'^#+0+$', fmt): 
                return sign + SSF._pad0(aval,len(fmt) - fmt.find("0"))
            #if((r = fmt.match(dec1))) {
            r = re.search(dec1, fmt)
            if not r:
                r = re.match(dec0, fmt)
            if r:
                comma = ',' in (r.group('before') or '')
                if comma:
                    fmt = fmt.replace(',', '')
                #o = (""+val).replace(/^([^\.]+)$/,"$1."+hashq(r[1])).replace(/\.$/,"."+hashq(r[1]));
                after = r.group('after')
                #o = re.sub(r'^([^.]+)$',r"\1."+hashq(after), SSF.to_str(val))
                #o = re.sub(r'\.$',"."+hashq(after), o)
                o = SSF.to_str(aval)
                if r.group('point'):
                    if '.' not in o:
                        o += '.'
                    #o = o.replace(/\.(\d*)$/,function($$, $1) { return "." + $1 + fill("0", hashq(r[1]).length-$1.length); });
                    #o = re.sub(r'\.(\d*)$', lambda m:  "." + m.group(1) + SSF._fill("0", len(hashq(r.group(1)))-len(m.group(1))), o)
                    o = re.sub(r'\.(\d*)$', lambda m: "."+ m.group(1) + hashq(after[len(m.group(1)):]), o)
                    dp = self.fmtl.decimal_point
                    e = fmt.find(".")-o.find(".")
                    if e > 0:           # https://github.com/SheetJS/ssf/issues/65
                        o = hashq(fmt[:e]) + o
                    # return fmt.indexOf("0.") !== -1 ? o : o.replace(/^0\./,".");
                    if comma:
                        od = o.find(".")
                        o = self.fmtl.commaify(o[:od]) + dp + o[od+1:]
                    else:
                        o = o.replace(".", self.fmtl.decimal_point)
                    return sign + (o if fmt.find("0"+dp) != -1 else re.sub(r'^0'+re.escape(dp), dp, o))
                else:
                    e = len(fmt) - len(o)
                    if e > 0:           # https://github.com/SheetJS/ssf/issues/65
                        o = hashq(fmt[:e]) + o
                    if comma:
                        o = self.fmtl.commaify(o)
                    return sign + (o if fmt.find("0") != -1 else re.sub(r'^0', '', o))
            
            fmt = re.sub(r'^#+([0.])', r"\1", fmt)
            r = re.match(r'^(0*)\.(#*)$', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #return sign + (""+aval).replace(/\.(\d*[1-9])0*$/,".$1").replace(/^(-?\d*)$/,"$1.").replace(/^0\./,r[1].length?"0.":".");
                result = re.sub(r'\.(\d*[1-9])0*$',r".\1",SSF.to_str(aval))
                result = re.sub(r'^(-?\d*)$',r"\1.",result)
                m = re.match(r'^(-?)(\d*)(\..*)$', result)
                if m:       # https://github.com/SheetJS/ssf/issues/65
                    result = m.group(1) + SSF._fill('0', len(r.group(1))-len(m.group(2))) + m.group(2) + m.group(3)
                result = re.sub(r'^0\.',"0." if len(r.group(1)) else ".", result)
                return sign + result.replace(".", self.fmtl.decimal_point)
            
            #if((r = fmt.match(/^#{1,3},##0(\.?)$/))) return sign + commaify((""+aval));
            r = re.match(r'^#{1,3},##0(\.?)$', fmt) 
            if r:   # pragma nocover - can't get here - covered by the general case above!
                return sign + self.fmtl.commaify(SSF.to_str(aval))
            #if((r = fmt.match(/^#,##0\.([#0]*0)$/))) {
            r = re.match(r'^#,##0\.([#0]*0)$', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #return val < 0 ? "-" + write_num_int(type, fmt, -val) : commaify((""+val)) + "." + fill('0',r[1].length);
                return "-" + write_num_int(type, fmt, -val) if val < 0 else self.fmtl.commaify(SSF.to_str(val)) + self.fmtl.decimal_point + SSF._fill('0',len(r.group(1)))
            
            #if((r = fmt.match(/^#,#*,#0/))) return write_num_int(type,fmt.replace(/^#,#*,/,""),val);
            r = re.match(r'^#,#*,#0', fmt)
            if r:   # pragma nocover - can't get here - covered by the general case above!
                fmtr = re.sub(r'^#,#*,', "", fmt)
                return write_num_int(type,fmtr,val)

            #if((r = fmt.match(/^([0#]+)(\\?-([0#]+))+$/))) {
            r = re.match(r'^([0#]+)(\\?-([0#]+))+$', fmt)       # Zip+ext like 00000-0000
            if r:           # pragma nocover - covered by the general case
                o = SSF._strrev(write_num_int(type, re.sub('[\\-]',"", fmt), val))
                ri = 0
                #return _strrev(_strrev(fmt.replace(/\\/g,"")).replace(/[0#]/g,function(x){return ri<o.length?o.charAt(ri++):x==='0'?'0':"";}));
                fmt1 = SSF._strrev(fmt.replace('\\',""))
                def sub_f(m):
                    nonlocal ri
                    if ri<len(o):
                        ri += 1
                        return o[ri-1]
                    return '0' if m.group(0)=='0' else ''
                result = SSF._strrev(re.sub(r'[0#]', sub_f, fmt1))
                return result
            
            if re.search(phone, fmt):
                o = write_num_int(type, "##########", val)
                return "(" + o[:3] + ") " + o[3:6] + "-" + o[6:]
            
            oa = ""
            #if((r = fmt.match(/^([#0?]+)( ?)\/( ?)([#0?]+)/))) {
            r = re.match(r'^([#0?]+)( ?)\/( ?)([#0?]+)', fmt)
            if r:
                ri = min(len(r.group(4)),7)
                ff = SSF._frac(aval, 10**ri-1, False)
                o = sign
                oa = self._write_num("n", r.group(1), ff[1])
                #if(oa.charAt(oa.length-1) == " ") oa = oa.substr(0,oa.length-1) + "0";
                if oa[-1] == " ": 
                    oa = oa[:-1] + "0"
                o += oa + r.group(2) + "/" + r.group(3)
                oa = SSF._rpad(ff[2],ri)
                #if(oa.length < r[4].length) oa = hashq(r[4].substr(r[4].length-oa.length)) + oa;
                if len(oa) < len(r.group(4)): 
                    oa = hashq(r.group(4)[len(r.group(4))-len(oa)]) + oa
                o += oa
                return o
            
            #if((r = fmt.match(/^# ([#0?]+)( ?)\/( ?)([#0?]+)/))) {
            r = re.match(r'^# ([#0?]+)( ?)\/( ?)([#0?]+)', fmt) # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                ri = min(max(len(r.group(1)), len(r.group(4))),7)
                ff = SSF._frac(aval, 10**ri-1, True)
                return sign + SSF.to_str(ff[0] or ("" if ff[1] else "0")) + " " + \
                  (SSF._pad(ff[1],ri) + r.group(2) + "/" + r.group(3) + SSF._rpad(ff[2],ri) if ff[1] else SSF._fill(" ", 2*ri+1 + len(r.group(2)) + len(r.group(3))))
            
            #if((r = fmt.match(/^[#0?]+$/))) {
            r = re.match(r'^[#0?]+$', fmt)  # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                o = SSF.to_str(val)
                if len(fmt) <= len(o):
                    return o
                return hashq(fmt[:len(fmt)-len(o)]) + o
            
            #if((r = fmt.match(/^([#0]+)\.([#0]+)$/))) {
            r = re.match(r'^([#0]+)\.([#0]+)$', fmt)    # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #o = "" + val.toFixed(Math.min(r[2].length,10)).replace(/([^0])0+$/,"$1");
                o = ('{:.' + str(min(len(r.group(2)),10)) + 'f}').format(val)
                o = re.sub(r'([^0])0+$',r"\1", o)
                ri = o.find(".")
                lres = fmt.find(".") - ri
                rres = len(fmt) - len(o) - lres
                return hashq(fmt[:lres] + o + fmt[len(fmt)-rres:]).replace(".", self.fmtl.decimal_point)
            
            #if((r = fmt.match(/^00,000\.([#0]*0)$/))) {
            r = re.match(r'^00,000\.([#0]*0)$', fmt)    # pragma nocover
            if r:   # pragma nocover - can't get here - covered by the general case above!
                #return val < 0 ? "-" + write_num_int(type, fmt, -val) : commaify(""+val).replace(/^\d,\d{3}$/,"0$&").replace(/^\d*$/,function($$) { return "00," + ($$.length < 3 ? pad0(0,3-$$.length) : "") + $$; }) + "." + pad0(0,r[1].length);
                if val < 0:
                    result = "-" + write_num_int(type, fmt, -val) 
                else:
                    result = self.fmtl.commaify(SSF.to_str(val))
                    result = re.sub(r'^(\d,\d{3})$',r"0\1", result)
                    def sub_f(m):
                        lm = len(m.group(0))
                        return "00," + (SSF._pad0(0,3-lm) if lm < 3 else "") + m.group(0)
                    result = re.sub(r'^\d*$',sub_f, result) + self.fmtl.decimal_point + SSF._pad0(0,len(r.group(1)))
                return result
            
            #switch(fmt) {
            #case "###,###":
            #case "##,###":
            #case "#,###": var x = commaify(""+aval); return x !== "0" ? sign + x : "";
            #default:
                #if(fmt.match(/\.[0#?]*$/)) return write_num_int(type, fmt.slice(0,fmt.lastIndexOf(".")), val) + hashq(fmt.slice(fmt.lastIndexOf(".")));
            if fmt in ("###,###", "##,###", "#,###"):   # pragma nocover
                x = self.fmtl.commaify(SSF.to_str(aval))
                return sign + x if x != "0" else ""
            elif re.search(r'\.[0#?]*$', fmt):  # pragma nocover
                return write_num_int(type, fmt[:fmt.rfind(".")], val) + hashq(fmt[fmt.rfind("."):]).replace(".", self.fmtl.decimal_point)
            
            self._value_error("unsupported format |" + fmt + "|")
            return ''

        #return function write_num(type, fmt, val) {
        if isinstance(val, bool):
            return ('FALSE','TRUE')[val]

        pcolon = fmt.find(':')      # issues/74
        if pcolon >= 0:          # This is a separator we inserted between the int part and the fraction
            ifmt = fmt[:pcolon]
            if ifmt:
                int_part = int(val)
                frac_part = abs(val - int_part)
                if frac_part != 0:
                    frac = self._write_num(type, fmt[pcolon+1:], frac_part)
                    if re.search(r'\b(\d+)[/]\1\b', frac):        # e.g. 1/1 or 12/12
                        int_part = SSF.round(val)
                        frac_part = 0
                    elif re.search(r'\b0\/', frac):           # e.g. 0/1 or 0/12
                        frac_part = 0
                    else:
                        return self._write_num(type, ifmt, int_part) + ':' + frac
                if frac_part == 0:
                    fmtr = re.sub(r'[/\d]', '?', fmt[pcolon+1:])
                    if int_part == 0:                   # issues/66
                        if ifmt and ifmt[-1] != '0':    # It's a '#' or '?'
                            ifmt = ifmt[:-1] + '0'      # Force a zero output int part
                    return self._write_num(type, ifmt, int_part) + ':' + hashq(fmtr)
            else:
                fmt = fmt[pcolon+1:]        # No integer part

        if int(val) == val and -2147483648 <= val <= 2147483647:
            return write_num_int(type, fmt, val)
        return write_num_flt(type, fmt, val)

    def _split_fmt(self, fmt):
        out = []
        in_str = False
        #for(var i = 0, j = 0; i < fmt.length; ++i) switch((/*cc=*/fmt.charCodeAt(i))) {
        i = 0
        j = 0
        while i < len(fmt):
        #case 34: /* '"' */
            if ord(fmt[i]) == 34:
                in_str = not in_str
            elif in_str:            # Fix for https://github.com/SheetJS/ssf/issues/53
                pass
        #case 95: case 42: case 92: /* '_' '*' '\\' */
            elif ord(fmt[i]) in (95, 42, 92):
                i += 1
        #case 59: /* ';' */
            elif ord(fmt[i]) == 59:
                out.append(fmt[j:i])
                j = i+1
            i += 1
        
        out.append(fmt[j:])
        if in_str:
            self._value_error("Format |" + fmt + "| unterminated string ")
        return out

    _split = _split_fmt
    # abstime = r'\[[HhMmSs\u0E0A\u0E19\u0E17]*\]'
    _abstime = re.compile(r'\[[HhMmSs\u0E0A\u0E19\u0E17]+\]')        # Needs to have at least 1 char in the brackets

    def _escape_dots(self, fmt):            # https://github.com/SheetJS/ssf/issues/68
        out = []
        in_str = False
        in_esc = False
        in_brk = False
        dots = 0
        for c in fmt:
            if in_esc:
                out.append(c)
                in_esc = False
            elif in_brk:
                out.append(c)
                if c == ']':
                    in_brk = False
            elif c == '"':
                in_str = not in_str
                out.append(c)
            elif in_str:
                out.append(c)
            elif c == '[':
                in_brk = True
                out.append(c)
            elif c in ('_', '*', '\\'):
                in_esc = not in_esc
                out.append(c)
            elif c == '.':
                dots += 1
                if dots >= 2:
                    out.append('\\')
                out.append(c)
            else:
                out.append(c)
        return ''.join(out)

    @staticmethod
    def fmt_is_date(fmt):
        """Returns True iff this ``fmt`` a date format"""
        fmtt = fmt.title()
        if fmtt in ('Date', 'Short Date', 'Long Date', 'Time'):
            return True
        if fmtt in ('General', 'Number', 'Currency', 'Accounting', 'Percentage',
                'Fraction', 'Scientific', 'Text'):
            return False
        i = 0
        c = ""
        o = ""
        while i < len(fmt):
            #switch((c = fmt.charAt(i))) {
            c = fmt[i]
            #case 'G': if(isgeneral(fmt, i)) i+= 6; i++; break;
            if c == 'G':
                if SSF._isgeneral(fmt, i):
                    i += 7
                    continue
            #case '"': for(;(/*cc=*/fmt.charCodeAt(++i)) !== 34 && i < fmt.length;){/*empty*/} ++i; break;
            elif c == '"':
                j = fmt.find('"', i+1)
                if j > i:
                    i = j+1
                else:           # Bad fmt
                    i += 1
                continue
            #case '\\': i+=2; break;
            elif c == '\\':
                i += 2
                continue
            #case '_': i+=2; break;
            elif c == '_':
                i += 2
                continue
            #case '@': ++i; break;
            elif c == '@':
                i += 1
                continue
            #case 'B': case 'b':
            elif c in ('B', 'b'):
                if fmt[i+1:i+2] in ("1", "2"):
                    return True
                    #/* falls through */
            #case 'M': case 'D': case 'Y': case 'H': case 'S': case 'E':
                    #/* falls through */
            #case 'm': case 'd': case 'y': case 'h': case 's': case 'e': case 'g': return True;
            if c in ('B', 'b', 'M', 'D', 'Y', 'H', 'S', 'E', 'm', 'd', 'y', 'h', 's', 'e', 'g'):
                return True
            #case 'A': case 'a': case '上':
            elif c in ('A', 'a', '上'):
                if fmt[i:i+3].upper() == "A/P":
                    return True
                if fmt[i:i+5].upper() in ("AM/PM", "上午/下午"):
                    return True
                i += 1
            #case '[':
            elif c == '[':
                #o = c
                #while(fmt.charAt(i++) !== ']' && i < fmt.length) o += fmt.charAt(i);
                j = fmt.find(']', i+1)
                if j < 0:
                    return False        # Bad format
                o = fmt[i:j+1]
                if re.match(SSF._abstime, o):
                    return True
                i = j+1
            #case '.':
                #/* falls through */
            #case '0': case '#':
            elif c in('.', '0', '#'):
                #while(i < fmt.length && ("0#?.,E+-%".indexOf(c=fmt.charAt(++i)) > -1 || (c=='\\' && fmt.charAt(i+1) == "-" && "0#".indexOf(fmt.charAt(i+2))>-1))){/* empty */}
                while i < len(fmt):
                    i += 1
                    c = fmt[i:i+1]
                    if "0#?.,E+-%".find(c) > -1 or \
                        (c=='\\' and fmt[i+1:i+2] == "-" and "0#".find(fmt[i+2:i+3])>-1):
                        continue
            #case '?': while(fmt.charAt(++i) === c){/* empty */} break;
            elif c == '?':
                i += 1
                while fmt[i:i+1] == c:
                    i += 1
            #case '*': ++i; if(fmt.charAt(i) == ' ' || fmt.charAt(i) == '*') ++i; break;
            elif c == '*':
                i += 1
                if fmt[i:i+1] in (' ', '*'):
                    i += 1
            #case '(': case ')': ++i; break;
            elif c in ('(', ')'):
                i += 1
            #case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
            elif c in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                #while(i < fmt.length && "0123456789".indexOf(fmt.charAt(++i)) > -1){/* empty */} break;
                i += 1
                while fmt[i:i+1].isdigit():
                    i += 1
            #case ' ': ++i; break;
            elif c == ' ':
                i += 1
            #default: ++i; break;
            else:
                i += 1
                
        return False;

    is_date = fmt_is_date

    def _replace_numbers(self, ostr, is_date=False, is_general=False):
        """Handle [DBNumN] and [$-xx......] number formats"""
        def replace_num(ostr, numbers):
            """Numbers is in the format: 0..9, exp, comma_sep, 10, 100, 1000, 10000, etc"""
            DIGITS, EXPP, EXPN, COMMA, TEN = range(5)
            digits = numbers[DIGITS]
            powers = numbers[TEN:]
            zero = digits[0]
            one = digits[1]
            three = digits[3]
            four = digits[4]
            ten = numbers[TEN]
            minus = numbers[EXPP][0] if numbers[EXPP] else '-'
            point = numbers[EXPP][2] if numbers[EXPP] else '.'
            exp_plus = numbers[EXPP][numbers[EXPP].find(three)+1:numbers[EXPP].find(four)] if numbers[EXPP] else 'E+'
            exp_minus = numbers[EXPN][numbers[EXPN].find(three)+1:numbers[EXPN].find(four)] if numbers[EXPN] else 'E-'
            exp_ = exp_plus[:-1] if exp_plus[1] == '+' else exp_plus
            comma = numbers[COMMA][2] if numbers[COMMA] else ','

            def replace_digits(ostr):
                if not ostr:
                    return ''
                dg = []
                for o in ostr:
                    ndx = ord(o) - ord('0')
                    if 0 <= ndx <= 9:
                        o = digits[ndx]
                    elif o == '-':
                        o = minus
                    elif o == '.':
                        o = point
                    elif o == ',':
                        o = comma
                    dg.append(o)
                return ''.join(dg)

            def replace_powers(ostr):
                """Handle languages that have separate digits for 10, 100, etc"""
                if not ostr:
                    return ''
                if not is_general and not is_date:      # We only replace powers in General formats and dates
                    return replace_digits(ostr)
                lo = len(ostr)
                if lo > len(powers):
                    return replace_powers(ostr[:len(powers)]) + replace_powers(ostr[len(powers):])
                digit = ostr[0]
                prefix = digits[ord(digit)-ord('0')]
                if digit == '0':
                    return replace_powers(ostr[1:])     # Eat zeros
                elif lo == 1:
                    return prefix
                elif digit == '1' and is_date and powers[lo-2][0] == one:
                    return powers[lo-2][1:] + replace_powers(ostr[1:])    # Change "one ten" to "ten" in dates
                elif digit == '1':
                    return powers[lo-2] + replace_powers(ostr[1:])     # Some languages represent "one hundred" as "hundred"
                else:
                    return prefix + powers[lo-2] + replace_powers(ostr[1:])

            if 'E' in ostr:     # Exponential
                ostr = ostr.replace('E+', 'e').replace('E-', 'x').replace('E', exp_).replace('e', exp_plus).replace('x', exp_minus)
                return replace_digits(ostr)

            if ten[-1] != zero:     # We have a '10' character
                m = re.match(r'^(?P<sign>[+-])?(?P<int>\d+)?(?:(?P<fraction>\.\d*)?)$', ostr)
                if not m:
                    return replace_digits(ostr)
                int_part = m.group('int')
                if int_part and int_part[0] == '0':     # Leading 0 - don't use powers
                    return replace_digits(m.group('sign')) + replace_digits(m.group('int')) + replace_digits(m.group('fraction'))
                return replace_digits(m.group('sign')) + replace_powers(m.group('int')) + replace_digits(m.group('fraction'))
            else:
                return replace_digits(ostr)
            return ostr

        if self.fmtl.dbnum:     # Handle [DBNumX]
            key = f'{self.fmtl.dbnum},{self.tmpl.locale_name}'
            if SSF_LOCALE.dbnum_map and key in SSF_LOCALE.dbnum_map:
                dbnums = SSF_LOCALE.dbnum_map[key]
                ostr = replace_num(ostr, dbnums)
        elif self.tmpl.numbers_xx:  # Handle [$-xxyyzzzz]
            key = self.tmpl.numbers_xx
            if SSF_LOCALE.numbers_map and key in SSF_LOCALE.numbers_map:
                numbers = SSF_LOCALE.numbers_map[key]
                ostr = replace_num(ostr, numbers)
        return ostr

    def _eval_fmt(self, fmt, v, opts, flen, wid, c_start, c_end, align):
        out = []
        o = ""
        i = 0
        c = ""
        lst='t'
        hr='H'
        dt = None
        got_g = False
        is_text = False
        has_fill = False
        abstime = False
        color_start = None
        color_start_rgb = None
        dots = 0                # https://github.com/SheetJS/ssf/issues/68
        #/* Tokenize */
        while i < len(fmt):
            #switch((c = fmt.charAt(i))) {
            c = fmt[i]
            #case 'G': /* General */
            if c == 'G':
                if not SSF._isgeneral(fmt, i): 
                    self._value_error('unrecognized character ' + c + ' in ' +fmt)
                out.append(SimpleNamespace(t='G', v='General'))
                i+=7
                continue
            #case '"': /* Literal text */
            elif c == '"':
                #for(o="";(cc=fmt.charCodeAt(++i)) !== 34 && i < fmt.length;) o += String.fromCharCode(cc);
                #out[out.length] = {t:'t', v:o}; ++i; break;
                j = fmt.find('"', i+1)
                if j < i:
                    self._value_error('unterminated string in ' + fmt)
                    j = len(fmt)
                out.append(SimpleNamespace(t='t', v=fmt[i+1:j]))
                i = j+1
                continue
            #case '\\': var w = fmt.charAt(++i), t = (w === "(" || w === ")") ? w : 't';
            elif c == '\\':
                i += 1
                w = fmt[i:i+1]
                if len(w) == 0:
                    self._value_error('invalid "\\" escape in ' + fmt)
                t = w if w in ('(', ')') else 't'
                out.append(SimpleNamespace(t=t, v=w))
                i += 1
                continue
            # The underscore character represents a space of the size of the next character, so eat that one too
            #case '_': out[out.length] = {t:'t', v:" "}; i+=2; break;
            elif c == '_':
                out.append(SimpleNamespace(t='t', v=" "))
                i += 2
                if i > len(fmt):
                    self._value_error('invalid "_" in ' + fmt)
                continue
            #case '@': /* Text Placeholder */
            elif c == '@':
                if isinstance(v, bool):
                    out.append(SimpleNamespace(t='T', v=('FALSE','TRUE')[v]))
                else:
                    is_text = True
                    out.append(SimpleNamespace(t='T', v=str(v)))
                i += 1
                continue
            # `B1` and `B2` specify which calendar to use, while `b` is the buddhist year.  It
            # acts just like `y` except the year is shifted
            #case 'B': case 'b':
            elif c in ('B', 'b'):
                if fmt[i+1:i+2] in ("1", "2"):
                    if dt is None: 
                        dt=self._parse_date_code(v, opts, fmt[i+1:i+2] == "2")
                        if dt is None:
                            #return ""
                            return SSF._pounds(wid)
                    out.append(SimpleNamespace(t='X', v=fmt[i:i+2]))
                    lst = c
                    i+=2
                    continue
                #/* falls through */
            #case 'M': case 'D': case 'Y': case 'H': case 'S': case 'E':
            if c in ('B', 'M', 'D', 'Y', 'H', 'S', 'E'):
                c = c.lower();
                #/* falls through */
            #case 'm': case 'd': case 'y': case 'h': case 's': case 'e': case 'g':
            if c in ('b', 'm', 'd', 'y', 'h', 's', 'e', 'g'):
                if v < 0: 
                    #return ""
                    return SSF._pounds(wid)
                if dt is None:
                    dt=self._parse_date_code(v, opts) 
                    if dt is None:
                        #return ""
                        return SSF._pounds(wid)
                if c == 'g':
                    got_g = True
                o = c; 
                i += 1
                while i < len(fmt) and fmt[i].lower() == c: 
                    o+=c
                    i += 1
                if c == 'm' and lst.lower() == 'h': 
                    c = 'M'
                if c == 'h': 
                    c = hr
                if c == 'y' and got_g:
                    c = 'e'                 # Change 'y' to 'e' (era) after seeing a 'g'
                    o = o.replace('y', 'e')
                out.append(SimpleNamespace(t=c, v=o))
                lst = c
                continue
            #case 'A': case 'a': case '上':
            elif c in ('A', 'a', '上'): 
                q=SimpleNamespace(t=c, v=c)
                if dt is None:
                    dt=self._parse_date_code(v, opts)
                # The rule regarding `A/P` and `AM/PM` is that if they show up
                # in the format then _all_ instances of `h` are considered 12-hour and not 24-hour
                # format (even in cases like `hh AM/PM hh hh hh`)
                if fmt[i:i+3].upper() == "A/P": 
                    if dt is not None:
                        if dt.H < 12:   # Morning   # https://github.com/SheetJS/ssf/issues/8
                            q.v = self.tmpl.a.lower() if c == 'a' else self.tmpl.a.upper()  # https://github.com/SheetJS/ssf/issues/54
                        else:           # Afternoon
                            q.v = self.tmpl.p.lower() if fmt[i+2] == 'p' else self.tmpl.p.upper()   # https://github.com/SheetJS/ssf/issues/54
                    q.t = 'T'
                    hr='h'
                    i+=3
                elif fmt[i:i+5].upper() == "AM/PM":
                    if dt is not None:
                        q.v = self.tmpl.pm if dt.H >= 12 else self.tmpl.am    # https://github.com/SheetJS/ssf/issues/8
                    q.t = 'T'
                    i+=5
                    hr='h'
                elif fmt[i:i+5].upper() == "上午/下午": 
                    if dt is not None:
                        q.v = "下午" if dt.H >= 12 else "上午"
                    q.t = 'T'
                    i+=5
                    hr='h'
                else:
                    q.t = "t"
                    i += 1
                if dt is None and q.t == 'T': 
                    #return ""
                    return SSF._pounds(wid)
                out.append(q)
                lst = c
                continue
            #case '[':
            elif c == '[':
                #o = c;
                #while(fmt.charAt(i++) !== ']' && i < fmt.length) o += fmt.charAt(i);
                #if(o.slice(-1) !== ']') throw 'unterminated "[" block: |' + o + '|';
                j = fmt.find(']', i+1)
                if j < 0:
                    self._value_error('unterminated "[" block: |' + o + '|')
                    i += 1
                    continue
                o = fmt[i:j+1]
                i = j+1
                if re.match(SSF._abstime, o):
                    if dt is None: 
                        dt=self._parse_date_code(v, opts, abstime=True)
                        abstime = True
                        if dt is None:
                            #return ""
                            return SSF._pounds(wid)
                        # The pseudo-type `Z` is used to capture absolute time blocks like [hh]
                        out.append(SimpleNamespace(t='Z', v=o.lower()))
                        lst = o[1]
                elif o.find("$") > -1:
                    if self.locale_support:
                        m = re.match(r'\[\$([^-]*)\-(?:([0-9A-Fa-f]+)|((?:[A-Za-z][A-Za-z0-9_-]+(?:,[0-9A-Fa-f]+)?)|(?:,[0-9A-Fa-f]+)))\]', o)      # [$USD-409] optional currency string-locale
                        if m:
                            if m.group(2):
                                xxyyzzzz = int(m.group(2), 16)  # https://stackoverflow.com/questions/54134729/what-does-the-130000-in-excel-locale-code-130000-mean
                                xx = (xxyyzzzz >> 24) & 0x7f
                                self.fmt_calendar_code = (xxyyzzzz >> 16) & 0x7f
                                locale_id = xxyyzzzz & 0xffff
                                if SSF_LOCALE.lcid_map and locale_id in SSF_LOCALE.lcid_map:
                                    lcid = SSF_LOCALE.lcid_map[locale_id]
                                    if lcid[0] == '*':      # These do a locale-based substitution of the format
                                        if 'time' in lcid:
                                            fmt = fmt[:i] + self.fmtl.time_format
                                        else:
                                            fmt = fmt[:i] + self.fmtl.long_date_format
                                    else:
                                        # Locales specified in format codes do NOT override the decimal_point or
                                        # the thousands_sep:
                                        self.tmpl = self._get_locale(locale_id, 
                                            decimal_separator=self.fmtl.decimal_point, 
                                            thousands_separator=self.fmtl.thousands_sep,
                                            calendar_code=self.fmt_calendar_code)
                                else:
                                    self._value_error(f"Cannot handle locale {locale_id:X} in {o}")
                            else:   # [$-en-US]
                                locale_split = m.group(3).split(',', 1)         # Issue #8
                                xx = None
                                self.fmt_calendar_code = 0
                                if len(locale_split) == 2:                      # Issue #8
                                    xxyy = int(locale_split[-1], 16)
                                    xx = (xxyy >> 8) & 0x7f
                                    self.fmt_calendar_code = xxyy & 0x7f
                                if locale_split[0]:                             # Issue #8
                                    self.tmpl = self._get_locale(locale_split[0],
                                            decimal_separator=self.fmtl.decimal_point, 
                                            thousands_separator=self.fmtl.thousands_sep,
                                            calendar_code=self.fmt_calendar_code)

                            if self.fmtl.dbnum or xx:
                                self.tmpl = copy(self.tmpl)
                                self.tmpl.dbnum = self.fmtl.dbnum
                                self.tmpl.numbers_xx = xx
                                
                            #currency_string = m.group(1)
                            #if currency_string:
                                #self.fmtl = copy(self.fmtl)
                                #self.fmtl.currency_symbol = currency_string


                    #o = (o.match(/\$([^-\[\]]*)/)||[])[1]||"$";
                    m = re.search(r'\$([^-\[\]]*)', o)
                    if m:
                        o = m.group(1)
                    else:
                        o = "$"
                    if not SSF.fmt_is_date(fmt): 
                        out.append(SimpleNamespace(t='t',v=o))
                elif SSF._negcond(re.match(SSF._cfregex2, o)):    # https://github.com/SheetJS/ssf/issues/52
                    v = abs(v)      # If this specifies absolutely a negative conditional, then eat the sign of the value
                elif re.match(r'^\[DBNum[123]\]$', o, re.I):
                    self.fmtl = copy(self.fmtl) # Because we cache it
                    self.fmtl.dbnum = int(o[6])
                elif c_start is not None:       # Handle colors if they pass us a c_start
                    m = re.match(self.color_pat, o, re.I)
                    if m:
                        color = m.group(1).replace(' ', '').title()
                        if color in self.color_map:
                            rgb = self.rgb_colors[self.color_map[color]]
                            #out.append(SimpleNamespace(t='t', v=c_start.format(color, rgb=rgb)))
                            color_start = color
                            color_start_rgb = rgb

                continue
            #/* Numbers */
            # Number blocks (following the general pattern `[0#?][0#?.,E+-%]*`) are grouped
            # together.  Literal hyphens are swallowed as well.  Since `.000` is a valid
            # term (for tenths/hundredths/thousandths of a second), it must be handled separately
            #case '.':
            elif c == '.':
                if dt is not None:      # Handle ss.000 in date formats
                    o = c
                    i += 1
                    while i < len(fmt):
                        c = fmt[i]
                        if c == '0':
                            o += c
                            i += 1
                        else:
                            break
                    out.append(SimpleNamespace(t='s', v=o))
                    continue
                else:                   # issues/68
                    dots += 1
                    if dots >= 2:
                        return self._eval_fmt(self._escape_dots(fmt), v, opts, flen, wid, c_start, c_end, align)
                #/* falls through */
            #case '0': case '#':
            # issues/74 if c in ('.', '0', '#'):
            if c in ('.', '0', '#', '?'):   # issues/74
                o = c
                #while(++i < fmt.length && "0#?.,E+-%".indexOf(c=fmt.charAt(i)) > -1) o += c;
                i += 1
                got_E = False       # Issue #11
                while i < len(fmt):
                    c = fmt[i]
                    # issues/50 if "0#?.,E+-%".find(c) > -1:
                    if "0#?.,E+-/".find(c) > -1:        # issues/50, issues/74
                        # Issue #11: Only grab a plus or minus after an E, else it's not part of the number format
                        if c == 'E':
                            got_E = True
                        if c in ('+', '-') and not got_E:
                            break
                        o += c
                        i += 1
                        if c == '.':            # issues/68
                            dots += 1
                            if dots >= 2:
                                return self._eval_fmt(self._escape_dots(fmt), v, opts, flen, wid, c_start, c_end, align)

                    else:
                        break
                out.append(SimpleNamespace(t='n', v=o))
                continue
            elif c == '/':          # issues/60: Handle stuff in between the '?'s and the '/' for fractions
                out.append(SimpleNamespace(t='/', v='/'))
                i += 1
            elif c == '%':      # issues/50
                if isinstance(v, int) or isinstance(v, float):
                    v *= 100
                out.append(SimpleNamespace(t='t', v=c))
                i += 1
            ## The fraction question mark characters present their own challenges.  For example, the
            ## number 123.456 under format `|??| /  |???| |???| foo` is `|15432| /  |125| |   | foo`:
            ##case '?':
            #elif c == '?':
                #o = c
                ##while(fmt.charAt(++i) === c) o+=c;
                #i += 1
                #while fmt[i:i+1] == c:
                    #o += c
                    #i += 1
                #out.append(SimpleNamespace(t=c, v=o))
                #lst = c
                #continue

            # OLD: Due to how the CSV generation works, asterisk characters are discarded.  TODO:
            # communicate this somehow, possibly with an option
            # NEW: Handle "*" for repeated chars if wid is given
            #case '*': ++i; if(fmt.charAt(i) == ' ' || fmt.charAt(i) == '*') ++i; break; // **
            elif c == '*':
                i += 1
                w = fmt[i:i+1]
                if len(w) == 0:
                    self._value_error('invalid "*" in ' + fmt)
                if wid == None:
                    if w in (' ', '*'):
                        i += 1
                else:       # Repeat to fill wid
                    out.append(SimpleNamespace(t='*', v=w))
                    has_fill = True
                    i += 1
                continue
            # The open and close parens `()` also has special meaning (for negative numbers)
            #case '(': case ')': out[out.length] = {t:(flen===1?'t':c), v:c}; ++i; break;
            elif c in ('(', ')'):
                out.append(SimpleNamespace(t='t' if flen == 1 else c, v=c))
                i += 1
                continue
            # The nonzero digits show up in fraction denominators
            #case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
            elif c in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                #o = c; while(i < fmt.length && "0123456789".indexOf(fmt.charAt(++i)) > -1) o+=fmt.charAt(i);
                j = i+1
                while fmt[j:j+1].isdigit():
                    j += 1
                o = fmt[i:j]
                out.append(SimpleNamespace(t='D', v=o))
                i = j
                continue
            # The default magic characters are listed in subsubsections 18.8.30-31 of ECMA376
            #case ' ': out[out.length] = {t:c, v:c}; ++i; break;
            elif c == ' ':
                out.append(SimpleNamespace(t=c, v=c))
                i += 1
                continue
            #case '$': out[out.length] = {t:'t', v:'$'}; ++i; break;
            elif c == '$':
                out.append(SimpleNamespace(t='t', v='$'))
                i += 1
                continue
            #default:
            else:
                # Issue #12 if ",$-+/():!^&'~{}<>=€acfijklopqrtuvwxzP".find(c) == -1:
                    # Issue #12 self._value_error(f'unrecognized character {c} ({ord(c)}) in {fmt}')
                out.append(SimpleNamespace(t='t', v=c))
                i += 1
                continue

        lalign = align.lower() if align else ''
        if wid and lalign != 'center':
            if (lalign == 'left' or (is_text and lalign != 'right')) and not has_fill: # Left justify text
                out.append(SimpleNamespace(t='*', v=' '))
            elif not isinstance(v, bool) or lalign == 'right': # Right justify if wid is specified and not text
                out = [SimpleNamespace(t='*', v=' ')] + out

        #/* Scan for date/time parts */
        """In order to identify cases like `MMSS`, where the fact that this is a minute
        appears after the minute itself, scan backwards.  At the same time, we can
        identify the smallest time unit (0 = no time, 1 = hour, 2 = minute, 3 = second)
        and the required number of digits for the sub-seconds"""

        bt = 0
        ss0 = 0
        ssm = None
        lst='t'
        b2 = False
        for i in reversed(range(len(out))):
            #switch(out[i].t) {
            oit = out[i].t
            #case 'h': case 'H': out[i].t = hr; lst='h'; if(bt < 1) bt = 1; break;
            if oit in ('h', 'H'):
                out[i].t = hr
                lst='h'
                if bt < 1:
                    bt = 1
                continue
            #case 's':
            elif oit == 's':
                #if((ssm=out[i].v.match(/\.0+$/))) ss0=Math.max(ss0,ssm[0].length-1);
                ssm = re.search(r'\.0+$', out[i].v)
                if ssm:
                    ss0=max(ss0,len(ssm.group(0))-1)
                if bt < 3: 
                    bt = 3
            #/* falls through */
            #case 'd': case 'y': case 'M': case 'e': lst=out[i].t; break;
            if oit in ('s', 'd', 'y', 'M', 'e'):
                lst=out[i].t
                continue
            #case 'm': if(lst === 's') { out[i].t = 'M'; if(bt < 2) bt = 2; } break;
            elif oit == 'm':
                if lst == 's':
                    out[i].t = 'M'
                    if bt < 2:
                        bt = 2
                continue
            #case 'X': /*if(out[i].v === "B2");*/
            elif oit == 'X':
                b2 = (out[i].v[1] == '2')
                continue
            #case 'Z':
            elif oit == 'Z':
                bt = 1
                continue
        
        # WRONG: /* time rounding depends on presence of minute / second / usec fields */
        # Time rounding depends on the length of the usec field
        #switch(bt) {
        #case 0: break;
        #case 1:
        if bt != 0:
            dt.u = SSF.round(dt.u, ss0)
            if dt.u >= 1 or dt.u <= -1:  
                v = (((dt.D*24+dt.H)*60+dt.M)*60+dt.S+dt.u) / 86400.0
                dt=self._parse_date_code(v, opts, b2, abstime)
                if dt is None:
                    return SSF._pounds(wid)

        #/* replace fields */
        # Since number groups in a string should be treated as part of the same whole,
        # group them together to construct the real number string
        nstr = ""
        is_number = False
        if isinstance(v, bool):
            is_number = True            # Treat boolean like a number
        num_written = False
        has_fraction = False        # issues/74
        #Can't use 'for' loop because we modify 'i' in the loop: for i in range(len(out)):
        i = 0
        while i < len(out):
            #switch(out[i].t) {
            t = out[i].t
            #case 't': case 'T': case ' ': case 'D': break;
            if t in ('t', 'T', ' ', 'D'):
                i += 1
            #case 'X': out[i].v = ""; out[i].t = ";"; break;
            elif t == 'X':
                out[i].v = ""
                out[i].t = ";"
                i += 1
            #case 'd': case 'm': case 'y': case 'h': case 'H': case 'M': case 's': case 'e': case 'b': case 'Z':
            elif t in ('d', 'm', 'y', 'h', 'H', 'M', 's', 'e', 'b', 'Z', 'g'):
                is_number = True
                value = self._write_date(ord(t), out[i].v, dt, ss0)
                if t == 'y' or len(out[i].v) < 3:   # Don't replace numbers in mmm, mmmm, ddd, dddd
                    value = self._replace_numbers(value, is_date=True if t != 'y' or len(out[i].v) != 4 else False)
                out[i].v = value
                num_written = True
                out[i].t = 't'
                i += 1
            #case 'n': case '?':
            # issues/74 elif t in ('n', '?'):
            elif t == 'n':      # issues/74 - we don't separate '?' anymore
                # issues/74 jj = i+1
                # issues/74 c = out[jj].t if jj < len(out) and out[jj] else ''
                # issues/74 while(jj < len(out) and out[jj] is not None and ( \
                  # issues/74 c == "?" or c == "D" or \
                  # issues/74 ((c == " " or c == "t") and jj+1 < len(out) and out[jj+1] is not None and (out[jj+1].t == '?' or out[jj+1].t == "t" and out[jj+1].v == '/')) or \
                  # issues/74 (out[i].t == '(' and (c == ' ' or c == 'n' or c == ')')) or \
                  # issues/74 (c == 't' and (out[jj].v == '/' or out[jj].v == ' ' and jj+1 < len(out) and out[jj+1] is not None and out[jj+1].t == '?')))):
                    # issues/74 out[i].v += out[jj].v
                    # issues/74 out[jj] = SimpleNamespace(v="", t=";")
                    # issues/74 jj += 1
                    # issues/74 if jj < len(out) and out[jj]:
                        # issues/74 c = out[jj].t
                
                nstr += out[i].v                    # issues/74
                jj = i+1                            # issues/74: Combine all number pieces
                while jj < len(out):
                    if out[jj].t in ('n', 'D', '/'): # Found another number piece, specific denominator, or slash
                        if '/' in out[jj].v:        # issues/74
                            if out[jj].t == 'n':
                                out = out[:jj] + [SimpleNamespace(t=':',v='')] + out[jj:] # Insert marker
                                jj += 1
                                nstr += ':'             # Separate int part from fraction for later
                                has_fraction = True
                            else:       # For '/', we have to find the prior number part and put the ':' before it!
                                for kk in reversed(range(jj)):
                                    if out[kk].t == 'n':
                                        lv = len(out[kk].v)
                                        out = out[:kk] + [SimpleNamespace(t=':',v='')] + out[kk:] # Insert marker
                                        jj += 1
                                        nstr = nstr[:-lv] + ':' + nstr[-lv:]
                                        has_fraction = True
                                        break
                                else:
                                    out[jj].t = 't'     # Change this to a text '/'
                                    i = jj
                                    break
                        nstr += out[jj].v
                        i = jj
                    jj += 1

                i += 1                              # issues/74
                is_number = True
                # issues/74 nstr += out[i].v
                # issues/74 i = jj-1
            #elif t == '/':          # issue/60
                #if nstr and ':' not in nstr:
                    ## We have to backtrack here because we already merged the prior number
                    ## character in with the rest, and we need to insert the ':' before it:
                    #for jj in reversed(range(i)):
                        #if out[jj].t == 'n':
                            #lv = len(out[jj].v)
                            #nstr = nstr[:len(nstr)-lv] + ':' + nstr[len(nstr)-lv:]
                            #out[i].t = 'n'  # Change this to a number piece, handled above, and don't increment i
                            #break
                    #else:
                        #out[i].t = 't'      # Change to text literal '/'
                        #i += 1
            #case 'G': out[i].t = 't'; out[i].v = general_fmt(v,opts); break;
            elif t == 'G':
                out[i].t = 't'
                myv = (-v if (isinstance(v, int) or isinstance(v, float)) and v<0 and flen > 1 else v)  # issues/70
                # issues/70 out[i].v = self._replace_numbers(self._general_fmt(v, opts), is_general=True)
                out[i].v = self._replace_numbers(self._general_fmt(myv, opts), is_general=True)          # issues/70
                num_written = True
                i += 1
            else:
                i += 1

        # Next, process the complete number string

        vv = ""
        if len(nstr) > 0:
            if ord(nstr[0]) == 40: #/* '(' */       # pragma nocover - can't really get here!
                myv = (-v if v<0 and ord(nstr[0]) == 45 else v)
                ostr = self._write_num('n', nstr, myv)
                num_written = True
            else:
                myv = (-v if v<0 and flen > 1 else v)
                ostr = self._write_num('n', nstr, myv)
                num_written = True
                if myv < 0 and out[0] and out[0].t == 't':
                    ostr = ostr[1:]
                    out[0].v = self.fmtl.minus_sign + out[0].v
                
            ostr = self._replace_numbers(ostr)

            jj=len(ostr)-1
            # Find the first decimal point
            decpt = len(out)
            for i in range(len(out)):
                if out[i] is not None and out[i].t != 't' and out[i].v.find(".") > -1:
                    decpt = i
                    break
            lasti=len(out)
            # If there is no decimal point or exponential, the algorithm is straightforward
            if decpt == len(out) and ostr.find(self.fmtl.exponential) == -1:
                blanked_end = None          # issues/60
                blanked_start = None
                found_non_blank = False
                slash_loc = -1
                pcolon = ostr.find(':')
                for i in reversed(range(len(out))):
                    # issues/74 if out[i] is None or 'n?'.find(out[i].t) == -1: 
                    if out[i] is None or 'nD/:'.find(out[i].t) == -1:     # issues/74
                        continue
                    if out[i].t == ':':      # Marker which starts the fraction part
                        if jj>=0 and lasti<len(out): 
                            out[lasti].v = ostr[pcolon+1:jj+1] + out[lasti].v
                            jj = pcolon-1
                    if '/' in out[i].v:
                        slash_loc = i
                    if jj>=len(out[i].v)-1: 
                        jj -= len(out[i].v) 
                        out[i].v = ostr[jj+1:jj+1+len(out[i].v)]
                    elif jj < 0: 
                        out[i].v = ""
                    else: 
                        out[i].v = ostr[:jj+1]
                        jj = -1
                    out[i].t = 't'
                    if out[i].v.isspace():          # issues/60
                        if blanked_end is None:
                            blanked_end = i
                            blanked_start = i
                        elif not found_non_blank:
                            blanked_start = i
                    elif blanked_end is not None:
                        found_non_blank = True
                        blanked_start = i+1
                    lasti = i
                
                if jj>=0 and lasti<len(out): 
                    out[lasti].v = ostr[:jj+1] + out[lasti].v

                if blanked_start is not None and blanked_start <= slash_loc <= blanked_end:   # issues/60
                    # If we blanked out the fraction, take out it's neighbors too
                    for i in range(blanked_start, blanked_end+1):
                        out[i].v = ' ' * len(out[i].v)

            # Otherwise we have to do something a bit trickier
            
            elif decpt != len(out) and ostr.find(self.fmtl.exponential) == -1:
                jj = ostr.find(self.fmtl.decimal_point)-1
                for i in reversed(range(decpt+1)):
                    if out[i] is None or 'n?'.find(out[i].t) == -1: 
                        continue
                    j=out[i].v.find(".")-1 if out[i].v.find(".")>-1 and i==decpt else len(out[i].v)-1
                    vv = out[i].v[j+1:].replace(".", self.fmtl.decimal_point)
                    #for(; j>=0; --j) {
                    for j in reversed(range(j+1)):
                        if jj>=0 and (out[i].v[j] == "0" or out[i].v[j] == "#"): 
                            vv = ostr[jj] + vv
                            jj -= 1
                    
                    out[i].v = vv
                    out[i].t = 't'
                    lasti = i
                
                if jj>=0 and lasti<len(out): 
                    out[lasti].v = ostr[:jj+1] + out[lasti].v
                jj = ostr.find(self.fmtl.decimal_point)+1
                dp = self.fmtl.decimal_point
                for i in range(decpt, len(out)):
                    if out[i] is None or ('n?('.find(out[i].t) == -1 and i != decpt): 
                        continue
                    j=out[i].v.find(dp)+1 if out[i].v.find(dp)>-1 and i==decpt else 0
                    dp = "."
                    vv = out[i].v[:j]
                    #for(; j<out[i].v.length; ++j) {
                    for j in range(j, len(out[i].v)):
                        if jj<len(ostr): 
                            vv += ostr[jj]
                            jj += 1
                    out[i].v = vv
                    out[i].t = 't'
                    lasti = i
            elif ostr.find(self.fmtl.exponential) > 0:      # issues/67
                # TODO: Line up the '.' like we do above
                pexp = ostr.find(self.fmtl.exponential)
                lenexp = len(ostr[pexp:])
                jj = len(ostr)
                first_n = None
                for i in range(len(out)):
                    if out[i].t == 'n':
                        first_n = i
                        break
                for i in reversed(range(len(out))):
                    if out[i].t == 'n':
                        pe = out[i].v.find('E')
                        lv = len(out[i].v)
                        if pe >= 0:
                            lv += lenexp - len(out[i].v[pe:])   # We may have more (or less) digits, e.g. E-14 vs E+0 fmt
                        j = jj - lv
                        j = max(j, 0)
                        if i == first_n:        # When we scan back to the first one, grab the rest
                            j = 0
                        out[i].v = ostr[j:jj]
                        out[i].t = 't'
                        jj = j
                
        # The magic in the next line is to ensure that the negative number is passed as
        # positive when there is an explicit hyphen before it (e.g. `#,##0.0;-#,##0.0`)

        for i in range(len(out)):
            if out[i] is not None and 'n?'.find(out[i].t)>-1:
                myv = (-v if flen >1 and v < 0 and i>0 and out[i-1].v == self.fmtl.minus_sign else v)
                out[i].v = self._write_num(out[i].t, out[i].v, myv)
                num_written = True
                out[i].t = 't'

        if not num_written and (isinstance(v, float) or isinstance(v, int)) and v < 0 and \
            flen == 1:      # https://github.com/SheetJS/ssf/issues/59
            # Pre-pend the minus sign if we haven't otherwise written the number
            # Handles the case from test_valid where the format is " Excellent" and excel
            # gives a result of '- Excellent' for negative numbers.  Doesn't do this if
            # an explicit second format for negative numbers is given.
            out = [SimpleNamespace(t='t', v = self.fmtl.minus_sign)] + out

        # Fill the width with the right-most "*" element, or the "*" element we added at the front to right-justify the output
        width = 0
        if wid is not None:
            # See how much room we have for '*' elements
            for o in out:
                if o is not None and o.t != '*':
                    width += len(o.v)

            delta = wid - width
            if ((isinstance(v, bool) and not lalign) or lalign == 'center') and not has_fill:      # Bools are centered unless we have a fill specified
                lpad = math.ceil(delta/2)
                rpad = delta - lpad
                out = [SimpleNamespace(t='t', v=' ' * lpad)] + out + [SimpleNamespace(t='t', v=' ' * rpad)]
            else:
                for o in reversed(out):
                    if o is not None and o.t == '*':
                        o.v *= delta        # Repeat the char (or make it '' if delta <= 0)
                        delta = 0

        # Now we just need to combine the elements

        retval = ""
        for i in range(len(out)):
             if out[i] is not None: 
                 retval += out[i].v

        if wid is not None and is_number and len(retval) > wid:
            retval = '#' * wid

        # Handle colors last as to not mess up the actual value

        if color_start:
            try:
                if c_start:
                    retval = c_start.format(color_start, rgb=color_start_rgb) + retval
                if c_end:
                    retval += c_end.format(color_start, rgb=color_start_rgb)
            except Exception:
                pass        # Silently ignore bad color start/end formats, etc

        return retval;

    _eval = _eval_fmt;
    #cfregex = re.compile(r'\[[=<>]')
    _cfregex2 = re.compile(r'\[(=|>[=]?|<[>=]?)(-?\d+(?:\.\d*)?)\]')

    @staticmethod
    def _chkcond(v, rr):      # rr is a match object
        if rr is None: 
            return False
        thresh = float(rr.group(2))
        op = rr.group(1)
        #switch(rr[1]) {
        #case "=":  if(v == thresh) return True; break;
        if op == "=":
            if v == thresh:
                return True
        #case ">":  if(v >  thresh) return True; break;
        elif op == ">":
            if v > thresh:
                return True
        #case "<":  if(v <  thresh) return True; break;
        elif op == "<":
            if v < thresh:
                return True
        #case "<>": if(v != thresh) return True; break;
        elif op == "<>":
            if v != thresh:
                return True
        #case ">=": if(v >= thresh) return True; break;
        elif op == ">=":
            if v >= thresh:
                return True
        #case "<=": if(v <= thresh) return True; break;
        elif op == "<=":
            if v <= thresh:
                return True
        return False

    @staticmethod
    def _negcond(rr):         # rr is a match object
        """Is this a negative conditional.  Fixes https://github.com/SheetJS/ssf/issues/52"""
        if rr is None:
            return False
        thresh = float(rr.group(2))
        op = rr.group(1)
        if op == "=":
            if thresh < 0:
                return True
        elif op == "<":
            if thresh <= 0:
                return True
        elif op == "<=":
            if thresh < 0:
                return True
        return False

    @staticmethod
    def _allnonnegcond(rr):         # rr is a match object
        """Is this conditional True for all non-negative numbers?  Fixes https://github.com/SheetJS/ssf/issues/78"""
        if rr is None:
            return False
        thresh = float(rr.group(2))
        op = rr.group(1)
        if op == ">":
            if thresh < 0:
                return True
        elif op == ">=":
            if thresh <= 0:
                return True
        return False

    def _choose_fmt(self, f, v):
        fmt = self._split_fmt(f)
        l = len(fmt)
        lat = fmt[-1].find("@")
        if l<4 and lat>-1: 
            l -= 1
        if len(fmt) > 4: 
            self._value_error("cannot find right format for |" + "|".join(fmt) + "|")
        #if(typeof v !== "number") return [4, fmt.length === 4 || lat>-1?fmt[fmt.length-1]:"@"];
        if isinstance(v, bool) or not isinstance(v, (int, float)):      # isinstance(True, int) is True!!
            return [4, fmt[-1] if len(fmt) == 4 or lat>-1 else "@"]
        #switch(fmt.length) {
        lf = len(fmt)
        #case 1: fmt = lat>-1 ? ["General", "General", "General", fmt[0]] : [fmt[0], fmt[0], fmt[0], "@"]; break;
        if lf == 1:
            fmt = ["General", "General", "General", fmt[0]] if lat>-1 else [fmt[0], fmt[0], fmt[0], "@"]
        #case 2: fmt = lat>-1 ? [fmt[0], fmt[0], fmt[0], fmt[1]] : [fmt[0], fmt[1], fmt[0], "@"]; break;
        elif lf == 2:
            fmt = [fmt[0], fmt[0], fmt[0], fmt[1]] if lat>-1 else [fmt[0], fmt[1], fmt[0], "@"]
        #case 3: fmt = lat>-1 ? [fmt[0], fmt[1], fmt[0], fmt[2]] : [fmt[0], fmt[1], fmt[2], "@"]; break;
        elif lf == 3:
            fmt = [fmt[0], fmt[1], fmt[0], fmt[2]] if lat>-1 else [fmt[0], fmt[1], fmt[2], "@"]
        #case 4: break;
        
        ff = fmt[0] if v > 0 else fmt[1] if v < 0 else fmt[2]
        m1 = re.search(SSF._cfregex2, fmt[0])
        m2 = re.search(SSF._cfregex2, fmt[1])
        if not m1 and not m2:               # issues/70
            return [l, ff]
        if v > 0 and not m1:                # issues/70: If the first format is not conditional
            return [l, ff]                  # issues/70  and it matches, then use it
        if m1 or m2:                        # issues/70
            if SSF._chkcond(v, m1):
                return [1, fmt[0]]      # let negcond() determine if we use the sign
            elif SSF._chkcond(v, m2):
                return [1, fmt[1]]      # let negcond() determine if we use the sign
            elif not m1 and v > 0:
                return [l, fmt[0]]
            elif not m2 and v < 0:
                if lf >= 3 or SSF._allnonnegcond(m1): # issues/78
                    return [l, fmt[1]]
                else:
                    return [1, fmt[1]]
            elif lf >= 3:
                return [1, fmt[2]]      # always display the sign
            elif v < 0:
                self._pound_sand = True
            return [l, fmt[2 if m1 is not None and m2 is not None else 1]]
        
        return [l, ff]

    @staticmethod
    def is_text_fmt(fmt):       # pragma nocover  (not currently used)
        """Is this a text format?"""
        if '@' not in fmt:
            return False
        in_str = False
        i = 0
        while i < len(fmt):
            c = fmt[i]
            if c == '\\':
                i += 1
            elif c == '"':
                in_str = not in_str
            elif in_str:
                pass
            elif c == '@':
                return True
            i += 1
        return False

    def locale_prefix(self, locale):        # pragma nocover   (Not used anymore)
        """Returns the appropriate [$-zzzz] locale prefix for the given ``locale``."""
        if locale is not None and self.locale_support:
            if isinstance(locale, str):
                locale = locale.strip()
                if locale in SSF_LOCALE.lcid_reverse_map:
                    locale = SSF_LOCALE.lcid_reverse_map[locale]
                else:
                    try:
                        sep = '-' if '-' in locale else '_'
                        _ = Locale.parse(locale, sep=sep)    # raises babel.core.UnknownLocaleError if not recognized
                        nxt = SSF_LOCALE.lcid_max + 1
                        SSF_LOCALE.lcid_max = nxt
                        SSF_LOCALE.lcid_map[nxt] = locale           # Add a new one
                        SSF_LOCALE.lcid_reverse_map[locale] = nxt
                        locale = nxt
                    except Exception:
                        self._value_error(f'Unknown Locale {locale}')
                        return ''
            return f'[$-{locale:X}]'
        return ''

    def _localize_table_from_locale(self, locale_name, prior_locale_names=None):
        """Add extra values to the table of integers to formats based on the locale"""
        if prior_locale_names is not None:
            for prior_locale_name in prior_locale_names:
                for key in SSF_LOCALE.table_map.get(prior_locale_name, {}):
                    self.table_fmt.pop(key, None)

        for key in SSF_LOCALE.table_map.get(locale_name, {}):
            self.table_fmt[key] = SSF_LOCALE.table_map[locale_name][key]


    def _get_locale(self, locale, decimal_separator=None, thousands_separator=None, update_table=False, calendar_code=None):
        #print(f'_get_locale({locale}, "{decimal_separator}", "{thousands_separator}", {update_table}, {calendar_code})')
        if not self.locale_support:
            return self.curl

        if locale is None:
            if update_table:
                self._localize_table_from_locale(None, prior_locale_names=[self.curl.locale_name, self.fmtl.locale_name])
            locale = self.curl.locale_name

        if isinstance(locale, SSF_LOCALE):
            locale = locale.locale_name

        s_l = str(locale)
        if decimal_separator == 'inherit':
            decimal_separator = self.curl.decimal_point
        if thousands_separator == 'inherit':
            thousands_separator = self.curl.thousands_sep
        s_l += decimal_separator if decimal_separator else ''
        s_l += thousands_separator if thousands_separator else ''
        s_l += str(calendar_code) if calendar_code is not None else ''
        if s_l in self._locale_cache:
            return self._locale_cache[s_l]

        try:
            result = SSF_LOCALE(locale=locale, decimal_separator=decimal_separator, thousands_separator=thousands_separator, calendar_code=calendar_code)
        except Exception as e:
            self._value_error(e)
            result = SSF_LOCALE(locale_support=self.locale_support, locale=None, decimal_separator=decimal_separator, thousands_separator=thousands_separator)
        if update_table:
            self._localize_table_from_locale(result.locale_name, prior_locale_names=[self.curl.locale_name, self.fmtl.locale_name])
        self._locale_cache[s_l] = result
        if SSF_LOCALE.lcid_reverse_map and s_l in SSF_LOCALE.lcid_reverse_map:
            self._locale_cache[str(SSF_LOCALE.lcid_reverse_map[s_l])] = result

        return result

    def _get_currency_format(self, places, negative_numbers, use_thousands_separator=False, accounting=False):
        """Internal routine to compute an appropriate format for formatting currency.  ``places`` specifies the
        number of places after the decimal - if None, then the default is used.  ``negative_numbers`` specifies
        how to format negative numbers.  It can be None, which uses the locale-specified positioning, 
        a minus sign, `Red`, which formats in red without a minus sign, `parens` which formats in parenthesis, 
        or `Redparens`, which does both red and parenthesis.  
        For currencies, these additional ``negative_numbers`` formats are supported: 
        
        * `<<-` - The sign should precede the value and currency symbol (`-` does this too)
        * `>>-` - The sign should follow the value and currency symbol
        * `<-`  - The sign should immediately precede the value
        * `>-`  - The sign should immediately follow the value
        
        If ``use_thousands_separator``, then a locale-based comma
        is used to group the digits before the decimal point.  If ``accounting`` is true then an appropriate accounting format is used.
        """
        result = []
        for val in (-1, 1, 0, 'a'):     # First 2 are switched so we can check the negative case
            if val == -1:
                cs_precedes = self.fmtl.n_cs_precedes
                sep_by_space = self.fmtl.n_sep_by_space
                sign_posn = self.fmtl.n_sign_posn
                sign = self.fmtl.negative_sign
            else:
                cs_precedes = self.fmtl.p_cs_precedes
                sep_by_space = self.fmtl.p_sep_by_space
                sign_posn = self.fmtl.p_sign_posn
                sign = self.fmtl.positive_sign
            if sign_posn == lcl.CHAR_MAX:
                sign_posn = 1
            if places is None:
                places = self.fmtl.frac_digits
            if val == -1:
                nnl = ''
                if negative_numbers is None and not accounting:
                    negative_numbers = '-'
                if negative_numbers is not None:
                    nnl = negative_numbers.lower()
                    neg_map = {'-': 1, '<<-': 1, '>>-': 2, '<-': 3, '>-': 4, 'paren': 0, 'parens': 0, 
                            '()': 0, 'redparens': 0, 'redparen': 0, 'red()': 0, '(': 0, 'red(': 0}
                    sign_posn = neg_map.get(nnl, sign_posn)
            ndx = (sign_posn << 2) + (cs_precedes << 1) + sep_by_space  # 0..19
            cs = '[$' + self.fmtl.currency_symbol + ']'
            prefix_map = {0:'(', 1:'(', 2:'('+cs, 3:'('+cs+' ',
                          4:sign, 5:sign, 6:sign+cs, 7:sign+cs+' ',
                          8:'', 9:'', 10:cs, 11:cs+' ',
                          12:sign, 13:sign, 14:cs+sign, 15:cs+' '+sign,
                          16:'', 17:'', 18:cs, 19:cs+' '}
            suffix_map = {0:cs+')', 1:' '+cs+')', 2:')', 3:')',
                          4:cs, 5:' '+cs, 6:'', 7:'',
                          8:cs+sign, 9:' '+cs+sign, 10:sign, 11:sign,
                          12:cs, 13:' '+cs, 14:'', 15:'',
                          16:sign+cs, 17:sign+' '+cs, 18:sign, 19:sign}
            # Handle accounting formats and ( ... ).  Handle 0 which can be displayed as '-'.
            # Currency: $#,##0.00
            # Currency with (...) for negative: $#,##0.00_);($#,##0.00)
            # Accounting: _($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)
            # Accounting with space: _ [$₹-445] * #,##0.00_ ;_ [$₹-445] * -#,##0.00_ ;_ [$₹-445] * "-"??_ ;_ @_ 
            # Accounting with Euro on right: _-* #,##0.00 [$€-483]_-;-* #,##0.00 [$€-483]_-;_-* "-"?? [$€-483]_-;_-@_-
            # Ditto:                         _ * #,##0.00_) [$€-1]_ ;_ * (#,##0.00) [$€-1]_ ;_ * "-"??_) [$€-1]_ ;_ @_ 
            # With '-' on right:             _ * #,##0.00_-[$₹-44D]_ ;_ * #,##0.00-[$₹-44D]_ ;_ * "-"??_-[$₹-44D]_ ;_ @_ 
            fmt = '0'
            if use_thousands_separator or use_thousands_separator is None:
                fmt = '#,##0'
            if places > 0:
                fmt += '.' + '0' * min(places, 30)
            prefix = prefix_map.get(ndx, prefix_map[7]).replace('[$$]', '$')
            suffix = suffix_map.get(ndx, suffix_map[7])

            def create_space_for_sign():
                nonlocal result, prefix, suffix, accounting
                if self.fmtl.negative_sign in result[0][0]:   # Negative prefix
                    if accounting:
                        prefix = '_' + self.fmtl.negative_sign + prefix
                elif self.fmtl.negative_sign in result[0][2]:   # Negative suffix
                    np = result[0][2].find(self.fmtl.negative_sign)
                    if np == 0:     # '-' at the start of the suffix
                        suffix = '_' + self.fmtl.negative_sign + suffix
                    else:           # '-' at the end of the suffix
                        suffix += '_' + self.fmtl.negative_sign

            if val == -1:
                if accounting:
                    if '(' in prefix:
                        prefix = re.sub(r'^[(]([^_]+)( ?)$', r'_(\1* (', prefix)    # Float $ out before (
                        suffix = re.sub(r'^([^)]+)[)]$', r')\1', suffix)            # Float $ out after )
                    else:
                        prefix = prefix.replace(sign, sign+'* ')
                if 'red' in nnl:
                    prefix = '[Red]' + prefix
            elif val == 1:
                if ')' in result[0][2]:
                    suffix += '_)'
                else:
                    create_space_for_sign()
                if accounting:
                    if '(' in result[0][0]:
                        prefix = '_(' + prefix
                    fmt = '* ' + fmt
            elif val == 0:
                if ')' in result[0][2]:
                    suffix += '_)'
                else:
                    create_space_for_sign()
                if accounting:
                    if '(' in result[0][0]:
                        prefix = '_(' + prefix
                    fmt = '* "-"??'
            else:       # Text
                fmt = '@'
                if ')' in result[0][2]:
                    prefix = '_('
                    suffix = '_)'
                else:
                    prefix = suffix = ''
                    create_space_for_sign()

            result.append((prefix, fmt, suffix))
        result[0], result[1] = (result[1], result[0])       # Swap the first 2
        r = ';'.join([r[0]+r[1]+r[2] for r in result])
        r = re.sub(r'^([^;]+);-\1;\1;@$', r'\1', r)         # Simplify result if all the same
        return r

    def get_format(self, type='General', places=None, use_thousands_separator=None, 
            negative_numbers=None, fraction_denominator=-1, positive_sign_exponent=True, locale=None):
        """Get an appropriate format for the ``locale`` either specified here or the locale of
        the ``ssf`` object.  The ``type`` is one of General, Number, Currency, Accounting,
        Date, Short Date, Long Date, Time, Percentage, Fraction, Scientific, or Text (in any case).
        If ``places`` is not None and this is a number format, then this specifies the
        number of decimal places, else a default is used.  Also for number formats,
        ``use_thousands_separator`` determines if the locale-specified thousands separator
        is used.  For currency and accounting formats, ``use_thousands_separator`` defaults
        to `True`.  In addition, ``negative_numbers`` specifies how to format negative numbers.
        It can be None, which uses a default format depending on the type (normally '-'),
        or `-`, which always uses a minus sign, `Red`, which formats in red without a minus 
        sign, `parens` which formats in parenthesis, or `Redparens`, which does both red and
        parenthesis.  You can also specify `()` as a synonym for `parens`.

        For currencies, these additional ``negative_numbers`` formats are supported: 
        
        * ``<<-`` The sign should precede the value and currency symbol (``-`` does this too)
        * ``>>-`` The sign should follow the value and currency symbol
        * ``<-``  The sign should immediately precede the value
        * ``>-``  The sign should immediately follow the value
        
        For Fraction formats, the ``fraction_denominator`` specifies the
        denominator to be used for the fraction.  If it is negative, then it instead
        specifies how many digits to use in the numerator.  If it is zero, then
        a ValueError is raised.

        For Scientific formats, ``positive_sign_exponent`` determines if a positive
        sign is displayed for positive exponents.  The default is True."""

        self.fmtl = self.curl       # Locale
        if self.locale_support and locale is not None:
            self.fmtl = SSF_LOCALE(locale=locale)
        type = type.title()
        if fraction_denominator != -1:
            type = 'Fraction'
        if type == 'Number':
            prefix = '#,##0' if use_thousands_separator else '0'
            if places is None:
                places = 2
            if places <= 0:
                result = prefix
            else:
                result = prefix + '.' + '0' * min(places, 30)
            negative_numbers = negative_numbers.lower() if negative_numbers is not None else '-'
            if 'red' in negative_numbers and ('paren' in negative_numbers or '(' in negative_numbers):
                return '_(' + result + '_);[Red](' + result + ')'
            elif 'red' in negative_numbers:
                return result + ';[Red]' + result
            elif 'paren' in negative_numbers or '(' in negative_numbers:
                return '_(' + result + '_);(' + result + ')'
            else:
                return result
        elif type == 'Currency':
            return self._get_currency_format(places, negative_numbers, use_thousands_separator)
        elif type == 'Accounting':
            return self._get_currency_format(places, negative_numbers, use_thousands_separator, accounting=True)
        elif type in ('Date', 'Short Date'):
            result = self.fmtl.short_date_format
            if result == 'm/dd/yyyy' and self._opts.dateNF:
                result = self._opts.dateNF
            return result
        elif type == 'Long Date':
            return "[$-F800]dddd, mmmm dd, yyyy"
        elif type == 'Time':
            return '[$-F400]h:mm:ss AM/PM'
        elif type == 'Percentage':
            if places is None:
                places = 2
            if places <= 0:
                return '0%'
            return '0.' + '0' * min(places, 30) + '%'
        elif type == 'Fraction':
            prefix = '#,###' if use_thousands_separator else '#'
            if fraction_denominator < 0:
                qm = '?' * min(-fraction_denominator, 30)
                return prefix + ' ' + qm + '/' + qm
            elif fraction_denominator > 0:
                fd = str(fraction_denominator)
                qm = '?' * len(fd)
                return prefix + ' ' + qm + '/' + fd
            else:
                ps = self._pound_sand
                self._value_error('Fraction format with fraction_denominator=0')
                self._pound_sand = ps
                return '"##########"'
        elif type == 'Scientific':
            if places is None:
                places = 2
            if positive_sign_exponent:
                return '0' + ('.' if places > 0 else '') + '0' * max(min(places, 30), 0) + 'E+00'
            else:
                return '0' + ('.' if places > 0 else '') + '0' * max(min(places, 30), 0) + 'E-00'
        elif type == 'Text':
            return '@'
        return 'General'

    _formats = {'Number', 'Currency', 'Accounting', 'Date', 'Short Date', 'Long Date', 'Time',
            'Percentage', 'Fraction', 'Scientific', 'Text'}

    def format(self, fmt, v, width=None, align=None, locale=None, decimal_separator=None, thousands_separator=None):
        """Format a value ``v`` according to the spreadsheet format in ``fmt`` with field ``width`` with alignment
        ``align``.  If ``width`` is not specified, then the `default_width` from the `ssf` object is used.  
        The ``align`` can be specified as 'left', 'right', 'center' or None.  If ``align`` is None, the 
        alignment is defaulted by the type of the value and the format.  Text is left aligned, numbers and dates are
        right aligned, and bool's are centered.  If the format is a text format (``@``), then the default is left
        aligned for all types of values.  If ``locale`` is not None and the ``ssf`` object supports locale, then
        this locale is used as the default locale if none is otherwise specified in the format.  The ``decimal_separator``
        and ``thousands_separator`` come from the specified locale, or the locale of the `ssf` object if None.  If
        specified, they override the default.  If they are specified as `inherit`, then the corresponding values of
        the `ssf` object are used even if a ``locale`` is specified here.  Note that any locale specified in
        the format itself does not change these separator values, to be consistent with spreadsheet implementations.
        """
        o = self._opts
        c_start = self.color_pre
        c_end = self.color_post
        if width is None:
            width = self._default_width
        #self.tmpl = self.fmtl = self.curl       # Locale
        if self._pound_sand and locale is None:     # We have a bad locale and errors='pounds'
            if width is not None:
                return '#' * width
            return '##########'

        self.fmtl = self._get_locale(locale, decimal_separator=decimal_separator, thousands_separator=thousands_separator, update_table=True)
        self.tmpl = self.fmtl   # This one can be overridden by a [$-zzzz] specification and affects date formatting only

        sfmt = ""
        fmt = self.autocorrect_format(fmt)       # Issue #3

        #switch(typeof fmt) {
        #case "string":
        if isinstance(fmt, str):
            if (fmt == "m/d/yy" or fmt == "m/d/yyyy") and o.dateNF: 
                sfmt = o.dateNF
            elif fmt.title() in SSF._formats:
                sfmt = self.get_format(fmt, locale=locale)
            else: 
                sfmt = fmt
        #case "number":
        elif isinstance(fmt, int):
            sfmt = None
            if fmt == 14 and o.dateNF: 
                sfmt = o.dateNF
            else:
                try:
                    sfmt = (o.table or self.table_fmt)[fmt]
                except (KeyError, IndexError):
                    pass
            if sfmt is None:
                try:
                    sfmt = (o.table and o.table[SSF._default_map[fmt]]) or self.table_fmt[SSF._default_map[fmt]]
                except (KeyError, IndexError):
                    pass
            if sfmt is None:
                try:
                    sfmt = SSF._default_str[fmt]
                except (KeyError, IndexError):
                    sfmt = "General"
        
        try:
            #issues/48 if self.isgeneral(sfmt,0): 
                #issues/48 return self._general_fmt(v, o, width, align=align)
            ov = v      # issues/48
            if SSF.fmt_is_date(sfmt) and isinstance(v, str):
                try:
                    v = date_parse(v)
                except Exception:
                    pass
            if isinstance(v, date) or isinstance(v, tm) or isinstance(v, timedelta): 
                v = self._datenum_local(v, o.date1904)
            f = self._choose_fmt(sfmt, v)
            if self._isgeneral(f[1]): 
                #issues/48 return self._general_fmt(v, o, width, '@' in sfmt, align)
                return self._general_fmt(ov, o, width, '@' in sfmt, align)   # issues/48
            #center = False
            #if isinstance(v, bool):
                #if v:
                    #v = "TRUE" 
                #else:
                    #v = "FALSE"
                #center = True
            if v == '' or v is None:
                return SSF._fill(' ', width)
            return self._eval_fmt(f[1], v, o, f[0], width, c_start, c_end, align)
        finally:
            if self._pound_sand:     # We have a bad format/value and errors='pounds'
                self._pound_sand = False
                if width is not None:
                    return '#' * width
                return '##########'

    def get_day_names(self):
        """Returns a 7-tuple containing 2-tuples of the abbreviation and full-day name,
        with Monday first"""
        return tuple(self.curl.days[1:] + self.curl.days[:1])

    def set_day_names(self, days):
        """Given an iterable of length 7 as ``days``, each of which containing a tuple of the abbreviation and
        full-day name, with Monday first, set this as the values to be returned for ddd and dddd formats,
        respectfully."""
        try:
            tup = tuple(days)
            if len(tup) != 7:
                raise ValueError
        except Exception:
            self._value_error('set_day_names needs an iterable of 7 values')
            return

        for t in tup:
            try:
                if isinstance(t, str) or len(t) < 2:
                    raise ValueError()
            except Exception:
                self._value_error(f'set_day_names needs a tuple for each of the 7 entries')
                return
            for e in t:
                if not isinstance(e, str):
                    self._value_error(f'set_day_names needs a tuple of strings for each of the 7 entries')
                    return
        self.curl.days = tup[6:] + tup[:6]

    def get_month_names(self):
        """Returns a 13-tuple containing 3-tuples of the single-letter abbreviation,
        the abbreviation, and the full-month name.  The entry at index 0 is None."""
        return tuple([None] + self.curl.months)

    def set_month_names(self, months):
        """Given an iterable of length 13 as ``months``, each of which containing a 3-tuple of
        the single-letter abbreviation, the abbreviation, and the full-month name, set this
        as the values to be returned for mmmmm, mmm, and mmmm formats, respectfully.  The
        first element is not used, so that the first month has index = 1."""
        try:
            tup = tuple(months)
            if len(tup) != 13:
                raise ValueError
        except Exception:
            self._value_error('set_month_names needs an iterable of 13 values')
            return

        for t in tup[1:]:
            try:
                if isinstance(t, str) or len(t) < 3:
                    raise ValueError()
            except Exception:
                self._value_error(f'set_month_names needs a tuple for each of the 13 entries, except the first')
                return
            for e in t:
                if not isinstance(e, str):
                    self._value_error(f'set_month_names needs a tuple of strings for each of the 13 entries, except the first')
                    return
        self.curl.months = tup[1:]

    def load_entry(self, fmt, idx=None):
        """Loads a single format entry specified by ``fmt`` into the mapping table.  If
        ``idx`` is specified, then that is used as the table index, else the first free
        entry is used.  The index used is returned."""
        #if(typeof idx != 'number') {
            #idx = +idx || -1;
        if not isinstance(idx, int):
            try:
                idx = int(idx)
            except Exception:
                idx = -1

            for i in range(0x0188):
                if i not in self.table_fmt:   
                    if idx < 0:  
                        idx = i
                        continue
                if self.table_fmt.get(i) == fmt: 
                    idx = i
                    break
            if idx < 0: 
                idx = 0x187
        
        self.table_fmt[idx] = fmt
        return idx

    load = load_entry
    #_table = table_fmt
    def get_table(self):
        """Returns the mapping table (a dict) from ints to format strings"""
        return self.table_fmt

    def load_table(self, tbl):
        """Given a dict of table indexes and values in ``tbl``, load it for use by the formatter"""
        for i,v in tbl.items():
            self.load_entry(v, i)

    def autocorrect_format(self, fmt):
        """Run some automatic corrections on the given format, and return the corrected format"""
        if fmt is None:
            return "General"
        if isinstance(fmt, int):
            return fmt

        if not fmt:
            return ''

        format_map = {'shortdate': "Short Date", 'longdate': "Long Date"}

        if ';' in fmt:
            return ';'.join([self.autocorrect_format(f) for f in fmt.split(';')])

        escapes = []

        def preserve_escapes(s):
            """Take any _, *, \\, or "..." escapes out of string `s`, returning a new string"""
            nonlocal escapes

            escapes = []
            out = []
            in_str = False
            in_esc = False
            in_brk = False
            def escape_it(c):
                ln = len(escapes)
                out.append(chr(0) + chr((ln>>4)&0xf) + chr(ln & 0xf))
                escapes.append(c)
            for c in s:
                if in_esc:
                    escapes[-1] += c
                    in_esc = False
                elif in_brk:
                    escapes[-1] += c
                    if c == ']':
                        in_brk = False
                elif c == '"':
                    in_str = not in_str
                    escape_it(c)
                elif in_str:
                    escapes[-1] += c
                elif c == '[':
                    in_brk = True
                    escape_it(c)
                elif c in ('_', '*', '\\'):
                    in_esc = not in_esc
                    escape_it(c)
                else:
                    out.append(c)
            return ''.join(out)

        def restore_escapes(s):
            """Restore any _, *, \\, or "..." escapes back from string `s`, returning a new string"""
            nonlocal escapes
            out = []
            i = 0
            while i < len(s):
                c = s[i]
                if c == chr(0):
                    ndx = (ord(s[i+1])<<4) | ord(s[i+2])
                    out.append(escapes[ndx])
                    i += 2
                else:
                    out.append(c)
                i += 1
            escapes = []
            return ''.join(out)

        def rfind_any(s, chars):
            """Find the right-most occurence of any of the characters in string `chars` and return
            it's index in s.  Else return -1"""
            char_set = set(chars)
            for i in reversed(range(len(s))):
                c = s[i]
                if c in char_set:
                    return i
            return -1

        fsl = fmt.strip().lower()
        if fsl in format_map:
            return format_map[fsl]

        if 'e' in fmt:
            def change_e(m):
                return m.group(0).replace('e', 'E')
            return re.sub(r'(?:[0#?.]e)|(?:e[0#?+0-])', change_e, fmt)
        elif 'E' in fmt:
            if re.search(r'(?:[0#?.]E)|(?:E[0#?+0-])', fmt):  # In a numeric context
                return fmt
            fmt = preserve_escapes(fmt)
            fmt = fmt.replace('E', 'e')
            return restore_escapes(fmt)
        else:
            pdot = fmt.find('.')
            if pdot >= 0 and ',' in fmt[pdot+1:]:
                # Only preserve escapes if this is a potential candidate for change
                fmt2 = preserve_escapes(fmt)
                pdot = fmt2.find('.')
                last_number_fmt = rfind_any(fmt2, "0#?")
                if last_number_fmt > pdot and ',' in fmt2[pdot+1:last_number_fmt]:
                    part1 = fmt2[:pdot+1]
                    part2 = fmt2[pdot+1:last_number_fmt+1]
                    part3 = fmt2[last_number_fmt+1:]
                    p2l = len(part2)
                    part2 = part2.replace(',', '')
                    commas = p2l - len(part2)
                    fmt2 = part1 + part2 + (',' * commas) + part3
                    return restore_escapes(fmt2)
        return fmt

#SSF.init_table = init_table;
#SSF.format = format;

if __name__ == '__main__':      # pragma nocover
    pass
    #ssf = SSF()
    #print(ssf.get_format('Accounting'))
