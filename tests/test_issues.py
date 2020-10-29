from ssf import SSF
ssf = SSF()

def test_issue_1():
    assert ssf.format('g', 1) == ''
    assert ssf.format('gg', 1) == ''
    assert ssf.format('ggg', 1) == ''
    assert ssf.format('ge', 1) == '1900'
    assert ssf.format('gee', 1) == '1900'
    assert ssf.format('geee', 1) == '1900'
    assert ssf.format('geeee', 1) == '1900'

def test_issue_5():
    try:
        import requests
    except Exception:
        return      # v0.2.2: Ok to skip this test if we don't have requests

    resp = requests.get('http://www.snoopyjc.org/ssf/')
    assert '<select id="category"' in resp.text

def test_issue_7():
    assert ssf.format('#', 1e24) == '1000000000000000000000000'
    assert ssf.format('#', -1e24) == '-1000000000000000000000000'
    assert ssf.format('#', 100000000000000000000000) == '100000000000000000000000'
    assert ssf.format('#', 123456789012345678901234) == '123456789012345678901234'
    assert ssf.format('#', -100000000000000000000000) == '-100000000000000000000000'

def test_issue_10(monkeypatch):
    import locale

    try:        # v0.2.2
        locale.setlocale(locale.LC_ALL, 'en-US')        # This raises locale.Error on linux
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        return              # Only do this test on Windoze!!

    real_setlocale = locale.setlocale

    def mock_setlocale(typ, locale):
        """Act like the Unix version of setlocale - don't accept
        any 2-letter locales and don't accept any '-'"""
        #print(f'mock_setlocale({typ}, {locale})')
        if not locale:
            return locale
        if len(locale) == 2 or '-' in locale:
            raise ValueError("Bad Linux Locale")
        if locale == 'dutch':
            real_setlocale(typ, 'nl')
        elif locale == 'icelandic':
            real_setlocale(typ, 'is')
        elif locale == 'de_DE':
            real_setlocale(typ, 'de-DE')
        return locale

    monkeypatch.setattr(locale, 'setlocale', mock_setlocale)
    try:
        ssfu = SSF(locale='nl')
        assert ssfu.format('Currency', 1.98) == '\u20AC 1,98'
        ssfi = SSF(locale='is')
        assert ssfi.format('Accounting', 12.98) == ' 13 kr'
        assert ssfu.format('#,###.00', 1234.56, locale='de-DE') == '1.234,56'
    finally:
        monkeypatch.setattr(locale, 'setlocale', real_setlocale)
    
def test_issue_11():
    assert ssf.format('[$kr]#,##0.00_-;[Red][$kr]#,##0.00-;[$kr]#,##0.00_-;@_-', -3.14) == 'kr3.14-'

def test_issue_12():
    ssfa = SSF(locale='ar', errors='raise')
    assert ssfa.format('Short Date', 3.14159) == '03\u200f/1\u200f/00'

def test_issue_13(monkeypatch):
    import locale

    real_setlocale = locale.setlocale

    def mock_setlocale(typ, locale):
        assert False        # Shouldn't come here!

    monkeypatch.setattr(locale, 'setlocale', mock_setlocale)
    try:
        ssfu = SSF(locale='nl')
        assert ssfu.format('Currency', 1.98) == '\u20AC 1,98'
        ssfi = SSF(locale='is')
        assert ssfi.format('Accounting', 12.98) == ' 13 kr'
        assert ssfu.format('#,###.00', 1234.56, locale='de-DE') == '1.234,56'
    finally:
        monkeypatch.setattr(locale, 'setlocale', real_setlocale)

def test_issue_14():
    from dateutil.parser import parse
    from datetime import date, timedelta

    adjusted = {0x03, 0x05, 0x07}
    converted = {0x06, 0x08, 0x0E, 0x11, 0x12, 0x13, 0x17}
    def assert_delta_1(ymd, ymd_prior):
        assert (ymd[0] == ymd_prior[0] and ymd[1] == ymd_prior[1] and ymd[2] == ymd_prior[2] + 1) or \
            (ymd[0] == ymd_prior[0] and ymd[1] == ymd_prior[1] +1 and ymd[2] == 1) or \
            (ymd[0] == ymd_prior[0] + 1 and ymd[1] == 1 and ymd[2] == 1)

    for cal in range(0x20):
        prior = date(1899,12,31)
        ymd_prior = None
        for dt in range(61):
            fmt = f'[$-{cal:02X}0000]yyyy-mm-dd'
            result = ssf.format(fmt, dt)
            if cal in converted:
                if dt == 0 or dt == 60:
                    assert result == ssf.format(fmt, dt+1)
                else:
                    r_split = result.split('-')
                    ymd = list(map(int, r_split))
                    if ymd_prior:
                        assert_delta_1(ymd, ymd_prior)
                    ymd_prior = ymd
            elif cal in adjusted:
                if dt == 0 or dt == 60:
                    nxt = ssf.format(fmt, dt+1)
                    assert_delta_1(list(map(int, nxt.split('-'))), list(map(int, result.split('-'))))
                else:
                    ymd = list(map(int, result.split('-')))
                    if ymd_prior:
                        assert_delta_1(ymd, ymd_prior)
                    ymd_prior = ymd
            else:
                if dt == 0 and result == '1900-01-00':
                    continue
                elif dt == 60 and result == '1900-02-29':
                    continue
                else:
                    dtr = parse(result).date()
                    assert dtr == prior + timedelta(days=1)
                    prior = dtr




