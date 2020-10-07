from ssf import SSF

def test_locale_simple():
    """Start by just testing a few simple cases"""
    ssfe = SSF(locale='en-US')
    assert ssfe.format('#,###.00', 1000000) == '1,000,000.00'
    assert ssfe.format('#,###.00', 1000000, decimal_separator=',', thousands_separator='.') == '1.000.000,00'
    assert ssfe.format('#,###.00', 1000000, decimal_separator='!') == '1,000,000!00'
    assert ssfe.format('#,###.00', 1000000, decimal_separator='!', thousands_separator='@') == '1@000@000!00'
    assert ssfe.format('#,###.00', 1000000, locale='en-US') == '1,000,000.00'
    assert ssfe.format('#,###.00', 1000000, locale='de-DE') == '1.000.000,00'
    assert ssfe.format('#,###.00', 1000000, locale='fr-FR') == '1\u202f000\u202f000,00'
    assert ssfe.format('#,###.00', 1000000, locale='hi_IN') == '10,00,000.00'
    assert ssfe.format('#,###.00', 1000000) == '1,000,000.00'
    assert ssfe.format('[$-409]#,###.00', 1000000, locale='de-DE') == '1.000.000,00'    # Format does NOT override argument for ,.
    assert ssfe.format('dddd, mmmm d, yyyy', '9/26/2020') == 'Saturday, September 26, 2020'
    assert ssfe.format('[$-409]dddd, mmmm d, yyyy', '9/26/2020', locale='fr-FR') == 'Saturday, September 26, 2020'
    assert ssfe.format('Currency', 1000.98) == '$1,000.98'
    assert ssfe.format('Currency', 1000.98, locale='de-DE') == '1.000,98 €'     # Euros

    ssfd = SSF(locale='de-DE')
    assert ssfd.format('#,###.00', 1000000, locale='en-US') == '1,000,000.00'
    assert ssfd.format('#,###.00', 1000000) == '1.000.000,00'
    assert ssfe.format('#,###.00', 1000000, decimal_separator='!', thousands_separator='@') == '1@000@000!00'
    assert ssfd.format('#,###.00', 1000000, locale='de-DE') == '1.000.000,00'
    assert ssfd.format('#,###.00', 1000000, locale='fr-FR') == '1\u202f000\u202f000,00'
    assert ssfd.format('#,###.00', 1000000, locale='hi_IN') == '10,00,000.00'
    assert ssfd.format('#,###.00', 1000000) == '1.000.000,00'
    assert ssfd.format('[$-409]#,###.00', 1000000) == '1.000.000,00'    # Format does NOT override default for ,.
    assert ssfd.format('[$-409]#,###.00', 1000000, locale='hi_IN') == '10,00,000.00'    # Format does NOT override ,.
    assert ssfd.format('[$-409]dddd, mmmm d, yyyy', '9/26/2020') == 'Saturday, September 26, 2020'
    assert ssfd.format('[$-409]dddd, mmmm d, yyyy', '9/26/2020', locale='fr-FR') == 'Saturday, September 26, 2020'
    assert ssfd.format('dddd, mmmm d, yyyy', '9/26/2020') == 'Samstag, September 26, 2020'
    assert ssfd.format('dddd, mmmm d, yyyy', '9/26/2020', locale='fr-FR') == 'samedi, septembre 26, 2020'
    assert ssfd.format('[$-40C]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'
    assert ssfd.format('[$-40c]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'
    assert ssfd.format('dddd, mmmm d, yyyy', '10/26/2020') == 'Montag, Oktober 26, 2020'

    ssfj = SSF(locale='ja-JP')
    assert ssfj.format('#,###.00', 1000000, locale='en-US') == '1,000,000.00'
    assert ssfj.format('#,###.00', 1000000) == '1,000,000.00'
    assert ssfj.format('#,###.00', 1000000, locale='de-DE') == '1.000.000,00'
    assert ssfj.format('#,###.00', 1000000, locale='fr-FR') == '1\u202f000\u202f000,00'
    assert ssfj.format('#,###.00', 1000000, locale='hi_IN') == '10,00,000.00'
    assert ssfj.format('#,###.00', 1000000) == '1,000,000.00'
    assert ssfj.format('[$-409]#,###.00', 1000000) == '1,000,000.00'
    assert ssfj.format('[$-409]#,###.00', 1000000, locale='hi_IN') == '10,00,000.00'    # Format does NOT override ,.
    assert ssfj.format('[$-409]dddd, mmmm d, yyyy', '9/26/2020') == 'Saturday, September 26, 2020'
    assert ssfj.format('[$-409]dddd, mmmm d, yyyy', '9/26/2020', locale='fr-FR') == 'Saturday, September 26, 2020'
    assert ssfj.format('dddd, mmmm d, yyyy', '9/26/2020') == '土曜日, 9月 26, 2020'
    assert ssfj.format('dddd, mmmm d, yyyy', '9/26/2020', locale='fr-FR') == 'samedi, septembre 26, 2020'
    assert ssfj.format('[$-40C]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'
    assert ssfj.format('[$-40c]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'
    assert ssfj.format('[$-fr-FR]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'
    assert ssfj.format('[$-FR_fr]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'
    assert ssfj.format('[DBNum1]0', 123) == '一二三'
    assert ssfj.format('[DBNum1]0', 987654) == '九八七六五四'
    assert ssfj.format('[DBNum2]0', 123) == '壱弐参'
    assert ssfj.format('[DBNum3]0', 123) == '１２３'
    assert ssfj.format('[DBNum1][$-404]0', 0) == '○'
    assert ssfj.format('[DBNum1][$-412]0', 0) == '０'

    ssfex = SSF(locale='en-US', decimal_separator='!!', thousands_separator='@')
    assert ssfex.format('#,###.00', 1000000) == '1@000@000!!00'
    assert ssfex.format('#,###.00', 1000000, locale='de-DE') == '1.000.000,00'
    assert ssfex.format('#,###.00', 1000000, locale='de-DE', decimal_separator='inherit',
            thousands_separator='inherit') == '1@000@000!!00'
    assert ssfex.format('#,###.00', 1000000, width=13) == '1@000@000!!00'
    assert ssfex.format('#,###.00', 1000000, width=12) == '#' * 12

def test_normalize_locale():
    ssf = SSF(locale='EN')
    assert ssf.locale == 'en'

    ssf = SSF(locale='en-us')
    assert ssf.locale == 'en-US'

    ssf = SSF(locale='En-Us')
    assert ssf.locale == 'en-US'

    ssf = SSF(locale='EN-us')
    assert ssf.locale == 'en-US'

    ssf = SSF(locale='en_us')
    assert ssf.locale == 'en-US'

    ssf = SSF(locale='zh_hans')
    assert ssf.locale == 'zh-Hans'

    ssf = SSF(locale='Qps_PLOCM')
    assert ssf.locale == 'qps-plocm'

    ssf = SSF(locale='CA_ES-valencia')
    assert ssf.locale == 'ca-ES_valencia'

    ssf = SSF(locale='SR_LATN-CS')
    assert ssf.locale == 'sr-Latn_CS'

    ssf = SSF(locale='Ff-latn-sn')
    assert ssf.locale == 'ff-Latn_SN'

    ssf = SSF(locale='es-es-tradnl')
    assert ssf.locale == 'es-ES_tradnl'

def test_no_locale():
    ssf = SSF(locale_support=False)
    assert ssf.format('#,##0', 1234) == '1,234'
    assert ssf.format('#,##0', 12345678) == '12,345,678'
    assert ssf.format('0', 12345678) == '12345678'
    assert ssf.format(14, '1/01/2020') == '1/1/2020'

    ssf.format('mmmm', '1/1/2020') == 'January'
    ssf.format('mmmm', '1/1/2020', locale='fr-FR') == 'January'
    ssf.format('[$-40C]mmmm', '1/1/2020') == 'January'

def test_bad_locale():
    try:
        ssf = SSF(locale='oops', errors='raise')
        assert False
    except ValueError as e:
        assert str(e) == 'Locale oops not found!'

    ssf = SSF(locale='oops', errors='pounds')
    assert ssf.format('0', 1, width=1) == '#'

    ssf = SSF(locale='oops', errors='ignore')
    assert ssf.format('0', 1) == '1'
    assert ssf.format(14, '1/02/2020') == '1/2/2020'


