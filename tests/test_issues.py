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
    import requests

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
        assert ssfi.format('Accounting', 12.98) == ' 13 kr.'
        assert ssfu.format('#,###.00', 1234.56, locale='de-DE') == '1.234,56'
    finally:
        monkeypatch.setattr(locale, 'setlocale', real_setlocale)
    
def test_issue_11():
    assert ssf.format('[$kr]#,##0.00_-;[Red][$kr]#,##0.00-;[$kr]#,##0.00_-;@_-', -3.14) == 'kr3.14-'

def test_issue_12():
    ssfa = SSF(locale='ar', errors='raise')
    assert ssfa.format('Short Date', 3.14159) == '03\u200f/1\u200f/00'
