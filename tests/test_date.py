#/* vim: set ts=2: */
#/*jshint -W041 */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
import math
import random
import re
from datetime import timedelta, datetime
import gzip
ssf = SSF()
SKIP=500
START_SKIPPING_AT=50
#var fs = require('fs'), assert = require('assert');
#var dates = fs.readFileSync('./test/dates.tsv','utf8').split("\n");
with gzip.open('tests/dates.tsv.gz', 'rt', encoding='utf-8') as d:
    dates = d.read().split("\n")
#var date2 = fs.readFileSync('./test/cal.tsv',  'utf8').split("\n");
with gzip.open('tests/cal.tsv.gz', 'rt', encoding='utf-8') as d:
    date2 = d.read().split("\n")
#var times = fs.readFileSync('./test/times.tsv','utf8').split("\n");
# Added more columns to times2.tsv for timedelta testing
with gzip.open('tests/times2.tsv.gz', 'rt', encoding='utf-8') as d:
    times = d.read().split("\n")

epoch_1904 = datetime(1904, 1, 1)
epoch_1900 = datetime(1899, 12, 31)
epoch_1900_minus_1 = datetime(1899, 12, 30)

def to_datetime(xldate, datemode=False):
    if datemode:
        epoch = epoch_1904
    else:
        if xldate < 60:
            epoch = epoch_1900
        else:
            # Workaround Excel 1900 leap year bug by adjusting the epoch.
            epoch = epoch_1900_minus_1

    days = int(xldate)
    fraction = xldate - days

    seconds = int(round(fraction * 86400000.0))
    seconds, milliseconds = divmod(seconds, 1000)

    result = epoch + timedelta(days, seconds, 0, milliseconds)
    if days == 0:
        return result.time()
    elif seconds == 0 and milliseconds == 0:
        return result.date()
    return result

def close_enuf(d1, d2):
    if d1 == d2:
        return
    m1 = re.match(r'^(.*?)(\d+[.]\d+)(.*)$', d1)
    m2 = re.match(r'^(.*?)(\d+[.]\d+)(.*)$', d2)
    if not m1 or not m2:
        assert d1 == d2        # Failed
    assert m1.group(1) == m2.group(1)
    assert m1.group(3) == m2.group(3)
    assert abs(float(m1.group(2)) - float(m2.group(2))) <= 0.1000000001

#function doit(data) {
def doit(data):
#  var step = Math.ceil(data.length/100), i = 1;
    step = math.ceil(len(data)/100)
    i = 1
#  var headers = data[0].split("\t");
    headers = data[0].split("\t")
#  for(var j = 0; j <= 100; ++j) it(String(j), function() {
    for j in range(101):
#    for(var k = 0; k <= step; ++k,++i) {
        for k in range(step+1):
#      if(data[i] == null || data[i].length < 3) return;
            if i > START_SKIPPING_AT:
                i += random.randint(0, SKIP)        # Skip ahead a few
            if i >= len(data):
                return
            if data[i] is None or len(data[i]) < 3:
                return
#      var d = data[i].replace(/#{255}/g,"").split("\t");
            d = data[i].replace('\255', "").split("\t")
#      for(var w = 1; w < headers.length; ++w) {
            for w in range(1, len(headers)):
#        var expected = d[w], actual = SSF.format(headers[w], parseFloat(d[0]), {});
                expected = d[w]
                #print(f'ssf.format({headers[w]}, {float(d[0])})')
                fd0 = float(d[0])
                actual = ssf.format(headers[w], fd0)
#        if(actual != expected) throw new Error([actual, expected, w, headers[w],d[0],d,i].join("|"));
                assert actual == expected
#        actual = SSF.format(headers[w].toUpperCase(), parseFloat(d[0]), {});
                #print(f'ssf.format({headers[w].upper()}, {float(d[0])})')
                actual = ssf.format(headers[w].upper(), fd0)
#        if(actual != expected) throw new Error([actual, expected, w, headers[w].toUpperCase(),d[0],d,i].join("|"));
                assert actual == expected
                if headers[w][0] == '[':    # Timedelta format
                    actual = ssf.format(headers[w], timedelta(days=fd0))
                    assert actual == expected
                elif 60 <= fd0 < 61:
                    pass        # Skip the Excel bug bad 2/29/1900 date
                else:
                    actual = ssf.format(headers[w], to_datetime(fd0))
                    close_enuf(actual, expected)

            i += 1
#      }
#    }
#  });
#}
#
#describe('time formats', function() {
def test_time_formats():
#  doit(process.env.MINTEST ? times.slice(0,4000) : times);
    doit(times)
#});
#
#describe('date formats', function() {
def test_date_formats():
#  doit(process.env.MINTEST ? dates.slice(0,4000) : dates);
    doit(dates)
#  if(0) doit(process.env.MINTEST ? date2.slice(0,1000) : date2);
#  it('should fail for bad formats', function() {
def test_bad_date_formats():
#    var bad = [];
    bad = ['hhh', 'HHH', 'hhmmm', 'hhMMM', 'sss', 'ss.0000', '[hm]', '[ms]', '[sm]', '[sh]', '[hs]']
#    var chk = function(fmt){ return function(){ SSF.format(fmt,0); }; };
    ssfi = SSF(errors='ignore')
    ssfe = SSF(errors='raise')
    def chk(fmt):
        ssfi.format(fmt, 0)     # Error should be ignored
        try:
            #print(f'ssf.format({fmt}, 0)')
            ssfe.format(fmt, 0)
            return False
        except Exception:
            return True
            
    for fmt in bad:
        assert chk(fmt)
#    bad.forEach(function(fmt){assert.throws(chk(fmt));});
#  });
#});

def test_date_rounding():
    """ https://github.com/SheetJS/ssf/issues/32 """
    dt = 4018.99999998843
    cases = [("mm/dd/yyyy hh:mm:ss.000", "12/31/1910 23:59:59.999"),
             ("mm/dd/yyyy hh:mm:ss.00", "01/01/1911 00:00:00.00"),
             ("mm/dd/yyyy hh:mm:ss.0", "01/01/1911 00:00:00.0"),
             ("mm/dd/yyyy hh:mm:ss", "01/01/1911 00:00:00"),
             ("mm/dd/yyyy hh:mm", "01/01/1911 00:00"),
             ("mm/dd/yyyy hh", "01/01/1911 00"),
             ("[hh]:mm:ss.000", "96455:59:59.999"),
             ("[hh]:mm:ss.00", "96456:00:00.00"),
             ("[hh]:mm:ss.0", "96456:00:00.0"),
             ("[hh]:mm:ss", "96456:00:00"),
             ("[hh]:mm", "96456:00"),
             ("[hh]", "96456"),
             ("[mm]:ss.000", "5787359:59.999"),
             ("[mm]:ss.00", "5787360:00.00"),
             ("[mm]:ss.0", "5787360:00.0"),
             ("[mm]:ss", "5787360:00"),
             ("[ss].000", "347241599.999"),
             ("[ss].00", "347241600.00"),
             ("[ss].0", "347241600.0"),
             ("[ss]", "347241600"),
             ("General", "4019"),
             ]

    for case in cases:
        fmt, expected = case
        assert ssf.format(fmt, dt) == expected

    assert ssf.format('[ss]', -0.9999999) == '-86400'

def test_is_date():
    assert ssf.is_date('Date')
    assert ssf.is_date('date')
    assert ssf.is_date('DATE')
    assert ssf.is_date('Short Date')
    assert ssf.is_date('Long Date')
    assert ssf.is_date('Time')
    assert ssf.is_date('time')
    assert ssf.is_date('yyyy')
    assert ssf.is_date('hh')
    assert ssf.is_date('m')
    assert ssf.is_date('g')
    assert ssf.is_date('e')
    assert ssf.is_date('[hh]')
    assert ssf.is_date('[m]')
    assert ssf.is_date('[ss]')
    assert ssf.is_date('s;;;@')
    assert not ssf.is_date('Currency')
    assert not ssf.is_date('Fraction')
    assert not ssf.is_date('General')
    assert not ssf.is_date('Text')
    assert not ssf.is_date('TEXT')
    assert not ssf.is_date('0')
    assert not ssf.is_date('@')
    assert not ssf.is_date('?/?')
    assert not ssf.is_date('0.0E+00')
    assert not ssf.is_date('[Red]')
    assert not ssf.is_date('[Class]')
    assert not ssf.is_date('[]')
