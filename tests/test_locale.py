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
    assert ssfe.format('[$-409]#,###.00', 1000000, locale='de-DE') == '1.000.000,00'    # Format does NOT override locale arg for ,.
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
    # Issue #9: Test eras:
    assert ssfj.format('g gg ggg e', '1/1/1900') == 'M 明 明治 33'
    assert ssfj.format('g gg ggg e', '7/29/1912') == 'M 明 明治 45'
    assert ssfj.format('g gg ggg e', '7/30/1912') == 'T 大 大正 1'
    assert ssfj.format('g gg ggg e', '12/24/1926') == 'T 大 大正 15'
    assert ssfj.format('g gg ggg e', '12/25/1926') == 'S 昭 昭和 1'
    assert ssfj.format('g gg ggg e', '1/7/1989') == 'S 昭 昭和 64'
    assert ssfj.format('g gg ggg e', '1/8/1989') == 'H 平 平成 1'
    assert ssfj.format('[$-ja-JP-x-gannen]g gg ggg e', '1/8/1989') == 'H 平 平成 元'
    assert ssfj.format('g gg ggg e', '4/30/2019') == 'H 平 平成 31'
    assert ssfj.format('g gg ggg e', '5/1/2019') == 'R 令 令和 1'
    assert ssfj.format('g gg ggg e', '1/1/2020') == 'R 令 令和 2'
    assert ssfj.format('[$-ja-JP-x-gannen]g gg ggg e', '5/1/2019') == 'R 令 令和 元'
    assert ssfj.format('[$-ja-JP-x-gannen]g gg ggg e', '1/1/2020') == 'R 令 令和 2'

    # Test [$-lg-CN,xxyy] and [$-xxyyzzzz]
    assert ssfe.format(r'[$-4000439]h:mm:ss\ AM/PM;@', 12.3456789) == '८:१७:४७ पूर्वाह्न'
    assert ssfe.format(r'[$-hi-IN,400]h:mm:ss\ AM/PM;@', 12.3456789) == '८:१७:४७ पूर्वाह्न'
    assert ssfe.format(r'[$-4010439]d/m/yyyy\ h:mm\ AM/PM;@', 12.3456789) == '१२/१/१९०० ८:१७ पूर्वाह्न'
    assert ssfe.format(r'[$-hi-IN,401]d/m/yyyy\ h:mm\ AM/PM;@', 12.3456789) == '१२/१/१९०० ८:१७ पूर्वाह्न'
    assert ssfj.format(r'[$-D000409]h:mm\ AM/PM;@', 12.3456789) == '๘:๑๗ AM'
    assert ssfe.format(r'[$-,D00]h:mm\ AM/PM;@', 12.3456789) == '๘:๑๗ AM'

    ssfex = SSF(locale='en-US', decimal_separator='!!', thousands_separator='@')
    assert ssfex.format('#,###.00', 1000000) == '1@000@000!!00'
    assert ssfex.format('#,###.00', 1000000, locale='de-DE') == '1.000.000,00'
    assert ssfex.format('#,###.00', 1000000, locale='de-DE', decimal_separator='inherit',
            thousands_separator='inherit') == '1@000@000!!00'
    assert ssfex.format('#,###.00', 1000000, width=13) == '1@000@000!!00'
    assert ssfex.format('#,###.00', 1000000, width=12) == '#' * 12

def test_alternate_calendars_1():
    ssff = SSF(locale='fr-FR', errors='raise')

    # Gregorian Calendar - United States - 02: Everything's in English
    assert ssff.format('[$-2040c]dddd mmmm d, yyyy', 43836) == 'Monday January 6, 2020'

    # Japanese (era) calendar 03
    assert ssff.format('[$-30091]dddd mmmm d, yyyy ge', 43836) == 'Monday January 6, 2 R2'
    assert ssff.format('[$-30091]g gg ggg e', 43865) == 'R 令 令和 2'
    assert ssff.format('[$-30091]b2g gg ggg e', 43865) == 'R 令 令和 2'

    # Taiwan Calendar 04
    assert ssff.format('[$-40001]ddd mmm d, yyyy', 43923) == 'Thu Apr 2, 2020'
    assert ssff.format('[$-4040C]dddd mmm d, yyyy', 43894) == '星期三 三月 4, 2020'

    # Korean Calendar 05
    assert ssff.format('[$-24050012]dddd mmm d, yyyy', 43952) == '금요일 5 一, 四三五三'
    assert ssff.format('[$-50009]m/d/yyyy', 43836) == '1/6/4353'

    # Hijri - Arab Lunar Calendar 06
    assert ssff.format('[$-60009]dddd,ddd,mmmm,mmm,mmmmm,m', 43894) == "AlArbia'a,AlArbia'a,Rajab,Rajab,R,7"
    assert ssff.format('[$-60402]dddd,ddd,mmmm,mmm,mmmmm,m', 43952) == 'AlJumaa,AlJumaa,Ramadan,Ramadan,R,9'
    assert ssff.format('[$-6040C]dddd mmm d, yyyy', 44053) == 'lundi Zoul Hijjah 20, 1441'  # Excel gives 21 for this one, but all online converters give 20!

def test_alternate_calendars_2():
    ssff = SSF(locale='fr-FR', errors='raise')

    # Thai Buddhist - 07

    assert ssff.format('[$-7000C]dddd mmmm d, yyyy', 44169) == 'ศุกร์ ธันวาคม 4, 2563'
    assert ssff.format('[$-0D07000C]dddd mmmm d, yyyy', 44169) == 'ศุกร์ ธันวาคม ๔, ๒๕๖๓'
    assert ssff.format('[$-0D07000C]dddd mmmm d, yyyy', 44200) == 'จันทร์ มกราคม ๔, ๒๕๖๔'

    # Jewish - 08 and 08_leap

    # Non leap year:
    assert ssff.format('[$-80009]dddd mmm d, yyyy', 43836) == 'Yom Sheni Tevet 9, 5780'
    assert ssff.format('[$-24080012]dddd mmm d, yyyy', 43894) == "Yom Revi'i Adar 八, 五七八０"
    assert ssff.format('[$-8000D]dddd,ddd,mmmm,mmm,mmmmm,m d yy', 43865) == 'יום שלישי,ג,שבט,שבט,שבט,5 9 80'
    assert ssff.format('[$-80402]dddd mmmm d, yyyy', 43923) == 'Yom Chamishi Nisan 8, 5780'
    assert ssff.format('[$-8008C]dddd mmm d, yyyy', 44111) == "Yom Revi'i Tishrei 19, 5781"
    # Leap year:
    assert ssff.format('[$-8000D]dddd mmmm d, yyyy', 44571) == 'יום שני שבט 8, 5782'
    assert ssff.format('[$-8000C]dddd mmmm d, yyyy', 44600) == 'Yom Shlishi AdarI 7, 5782'      # Leap month
    assert ssff.format('[$-8000C]dddd mmmm m/d/yy', 44629) == "Yom Revi'i AdarII 7/6/82"
    assert ssff.format('[$-8000A]dddd mmm mm/dd/yyyy', 44817) == 'Yom Shlishi Elul 13/17/5782'  # 13th month
    assert ssff.format('[$-82C09]dddd mmmm yyyy-mm-dd', 44846) == "Yom Revi'i Tishrei 5783-01-17"   # Wrap-around to month 1

    # Gregorian French - 09
    assert ssff.format('[$-90409]dddd mmmm d, yyyy', 43865) == 'mardi février 4, 2020'

    # Gregorian Arabic - 0A
    assert ssff.format('[$-A000C]dddd mmmm yyyy-mm-dd', 43836) == 'الإثنين كانون الثاني 2020-01-06'
    assert ssff.format('[$-AFC23]dddd,ddd,mmmm,mmm,mmmmm,m', 44169) == 'الجمعة,الجمعة,كانون الأول,كانون الأول,ك,12'

    # Gregorian Transliterated English - 0B

    assert ssff.format('[$-B0009]dddd mmmm d, yyyy', 43836) == 'الإثنين يناير 6, 2020'

    # Gregorian Transliterated French - 0C

    assert ssff.format('[$-240C0012]dddd,ddd,mmmm,mmm,mmmmm,m-d-yyyy', 43952) == 'الجمعة,الجمعة,مايو,مايو,م,五-一-二０二０'

def test_alternate_calendars_3():
    ssff = SSF(locale='fr-FR', errors='raise')

    # Lunar 0E

    # Non leap year:
    assert ssff.format('[$-E0009]dddd,ddd,mmmm,mmm,mmmmm,m/d/yyyy', 43659) == '土曜日,土,六月,六月,六,6/11/2019'
    assert ssff.format('[$-E0001]dddd,ddd,mmmm,mmm,mmmmm,m', 43840) == 'Friday,Fri,December,Dec,D,12'
    assert ssff.format('[$-E0001]dddd,ddd,mmmm,mmm,mmmmm,m', 43869) == 'Saturday,Sat,January,Jan,J,1'
    assert ssff.format('[$-1B0E0411]dddd mmmm d, yyyy', 43659) == '土曜日 六月 十一, 二〇一九'
    # Leap year:
    assert ssff.format('[$-E0009]dddd mmm dd, yyyy', 43856) == '日曜日 正月 02, 2020'
    assert ssff.format('[$-1E0E0404]dddd,ddd,mmmm,mmm,mmmmm,m-d-yyyy', 44190) == '金曜日,金,十二月,十二月,十,十二-十一-二○二○'    #12th month
    assert ssff.format('[$-1E0E0404]dddd,ddd,mmmm,mmm,mmmmm,m-d-yyyy', 44219) == '土曜日,土,十二月,十二月,十,十三-十一-二○二○'    #13th month

    # Lunar 11

    # Non leap year:
    assert ssff.format('[$-110001]ddd mmm d yyyy', 43840) == 'Fri Dec 16 2019'
    assert ssff.format('[$-110001]ddd mmm d yyyy', 43869) == 'Sat Jan 15 2020'
    # Leap year:
    assert ssff.format('[$-11FC23]mm-dd-yyyy', 44190) == '12-11-2020'
    assert ssff.format('[$-11FC23]mm-dd-yyyy', 44219) == '13-11-2020'
    
    # Lunar 12

    # Non leap year:
    assert ssff.format('[$-120010]yyyy-mm-dd', 43840) == '2019-12-16'
    assert ssff.format('[$-120010]yyyy-mm-dd', 43869) == '2020-01-15'
    # Leap year:
    assert ssff.format('[$-1E127804]yyyy mm dd', 44190) == '二○二○ 十二 十一'   #12th month
    assert ssff.format('[$-1E127804]yyyy mm dd', 44219) == '二○二○ 十三 十一'   #13th month

def test_alternate_calendars_4():
    ssff = SSF(locale='fr-FR', errors='raise')

    # Chinese Lunar 13
    # Non leap year:
    assert ssff.format('[$-137C92]yyyy-mm-dd', 43840) == '2019-12-16'
    assert ssff.format('[$-137C92]yyyy-mm-dd', 43869) == '2020-01-15'
    # Leap year:
    assert ssff.format('[$-137C92]yyyy-mm-dd', 44190) == '2020-12-11'
    assert ssff.format('[$-137C92]yyyy-mm-dd', 44219) == '2020-13-11'

    # UM_AL_QURA 17
    assert ssff.format('[$-171809]dddd mmmm d, yyyy', 43836) == 'AlEthnien Jamada El Oula 11, 1441'
    

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


