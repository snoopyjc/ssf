
# Test that we fixed all the issues reported for ssf.js
# See https://github.com/SheetJS/ssf/issues

from ssf import SSF

ssf = SSF()

def test_issue_8():     # International support
    assert ssf.format('#,###.00', 1000000, locale='de-DE') == '1.000.000,00'
    assert ssf.format('#,###.00', 1000000, locale='fr-FR') == '1\u202f000\u202f000,00'
    assert ssf.format('#,###.00', 1000000, locale='hi_IN') == '10,00,000.00'

def test_issue_11():
    ssfc = SSF(color_pre='<color name="{}" rgb="#{rgb}">', color_post='</color {}>')
    assert ssfc.format('0', 0) == '0'
    assert ssfc.format('[Red]0', 0) == '<color name="Red" rgb="#FF0000">0</color Red>'
    assert ssfc.format('[Color2]0', 0) == '<color name="Color2" rgb="#FFFFFF">0</color Color2>'
    assert ssfc.format('[Color 2]0', 0) == '<color name="Color2" rgb="#FFFFFF">0</color Color2>'

def test_issue_12():
    assert ssf.format('#,###.??;(#,###.??);0', 1234.1) == '1,234.1 '
    assert ssf.format('#.0?0?#?#?#?#', 0) == '.0 0    '

def test_issue_13():
    assert ssf.format('#,##.??;(#,##.??);0', 1234.1) == '1,234.1 '
    assert ssf.format('h am/pm', '1pm') == '1 PM'

def test_issue_14():
    ssfnf = SSF(dateNF='m/d/yy')
    assert ssfnf.format(14, '12/31/1999') == '12/31/99'

def test_issue_21():
    cases = [
            (0.12, ('$0,000.00', '$0,000.12'),
             ('$#,000.00', '$000.12'), ('$#,#00.00', '$00.12'), ('$#,##0.00', '$0.12'), ('$#,###.00', '$.12')),
            (1.23, ('$0,000.00', '$0,001.23'),
             ('$#,000.00', '$001.23'), ('$#,#00.00', '$01.23'), ('$#,##0.00', '$1.23'), ('$#,###.00', '$1.23')),
            (12.34, ('$0,000.00', '$0,012.34'),
             ('$#,000.00', '$012.34'), ('$#,#00.00', '$12.34'), ('$#,##0.00', '$12.34'), ('$#,###.00', '$12.34')),
            (123.45, ('$0,000.00', '$0,123.45'),
             ('$#,000.00', '$123.45'), ('$#,#00.00', '$123.45'), ('$#,##0.00', '$123.45'), ('$#,###.00', '$123.45')),
            (-0.12, ('$0,000.00', '-$0,000.12'),
             ('$#,000.00', '-$000.12'), ('$#,#00.00', '-$00.12'), ('$#,##0.00', '-$0.12'), ('$#,###.00', '-$.12')),
             ]

    for case in cases:
        val = case[0]
        for fmt, expected in case[1:]:
            actual = ssf.format(fmt, val)
            assert actual == expected

def test_issue_30():
    assert ssf.format('0.0#', 15.06) == '15.06'

def test_issue_31():
    assert ssf.format('###0 "Million" 000 "Thousand" 0 "Hundred" 00', 123456789) == '123 Million 456 Thousand 7 Hundred 89'
    assert ssf.format(';($0.0)', -200) == '($200.0)'

def test_issue_32():
    assert ssf.format('hh:mm:ss', 0.001388773) == '00:02:00'

def test_issue_35():
    assert ssf.format('$#,###.00##', 1.1111) == '$1.1111'

def test_issue_36():
    assert ssf.format('#,##0.00', 1234.56, decimal_separator=',', thousands_separator=' ') == '1 234,56'

def test_issue_37():
    assert ssf.format('[$-40c]dddd, mmmm d, yyyy', '9/26/2020') == 'samedi, septembre 26, 2020'

def test_issue_48():
    assert ssf.format("General;General;-;General", 0) == '-'

def test_issue_49():
    assert ssf.format("[red]-##,#", 0) == '-'
    assert ssf.format("[red]-#,###", 1) == '-1'

def test_issue_50():
    assert ssf.format('#,##0.0000%', 0.123/100) == '0.1230%'
    assert ssf.format('#,##0.0000 %', 0.123/100) == '0.1230 %'
    assert ssf.format('%#,##0.0000 %', 0.123/100/100) == '%0.1230 %'

def test_issue_52():
    assert ssf.format('[<=-1000000]("$"#,##0.0,,"M")', -1000000) == '($1.0M)'
    assert ssf.format('[<=-1000000]("$"#,##0.0,,"M");', -1000000) == '($1.0M)'

def test_issue_53():
    assert ssf.format('"a"0.###', 3.14159) == 'a3.142'
    assert ssf.format('";"0.###', 3.14159) == ';3.142'

def test_issue_54():
    assert ssf.format('h:mm A/P"m"', 3.14159) == '3:23 Am'
    assert ssf.format('h:mm A/p"m"', 3.14159) == '3:23 Am'
    assert ssf.format('h:mm a/P"m"', 3.14159) == '3:23 am'
    assert ssf.format('h:mm a/p"m"', 3.14159) == '3:23 am'

    assert ssf.format('h:mm A/P"m"', 3.14159+0.5) == '3:23 Pm'
    assert ssf.format('h:mm a/P"m"', 3.14159+0.5) == '3:23 Pm'
    assert ssf.format('h:mm A/p"m"', 3.14159+0.5) == '3:23 pm'
    assert ssf.format('h:mm a/p"m"', 3.14159+0.5) == '3:23 pm'

def test_issue_55():
    assert ssf.format(14, '1/01/1999') == '1/1/1999'
    assert ssf.format(22, '1/01/1999 1:01am') == '1/1/1999 1:01'
    assert ssf.format(37, 1234) == '1,234 '
    assert ssf.format(38, 1234) == '1,234 '
    assert ssf.format(39, 1234) == '1,234.00 '
    assert ssf.format(40, 1234) == '1,234.00 '
    assert ssf.format(39, 1234.56) == '1,234.56 '
    assert ssf.format(40, 1234.56) == '1,234.56 '
    assert ssf.format(47, (9*60+8.5)/86400) == '09:08.5'
    assert ssf.format(55, '1/01/1999', locale='ko-KR') == '1999/01/01'

ssfc = SSF(color_pre='{}:')

def test_issue_57():
    assert ssf.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', -25) == '25'
    assert ssf.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 0) == '0'
    assert ssf.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 4) == '4'
    assert ssf.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 25) == '25'
    assert ssf.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 'hi') == 'hi'
    assert ssfc.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', -25) == 'Red:25'
    assert ssfc.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 0) == 'Green:0'
    assert ssfc.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 4) == 'Green:4'
    assert ssfc.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 25) == 'Blue:25'
    assert ssfc.format('[Red][<=-25]General;[Blue][>=25]General;[Green]General;[Yellow]General', 'hi') == 'Yellow:hi'

def test_issue_58():
    for d in (0, 1, 2, 3, 59, 60, 61):
        assert ssf.format('b2ddd', d) == ssf.format('ddd', d)
        # This calendar doesn't actually work!!  assert ssf.format('b2yyyy', d) == '1317'

def test_issue_59():
    assert ssf.format('A"TODO"', 1) == 'ATODO'
    assert ssf.format('A"TODO"', -1) == '-ATODO'
    assert ssf.format('A"TODO"', 0) == 'ATODO'
    assert ssf.format('A"TODO"', 'TODO') == 'TODO'

    assert ssf.format('\\r', 1) == 'r'
    assert ssf.format('\\r', -1) == '-r'
    assert ssf.format('\\r', 0) == 'r'
    assert ssf.format('\\r', 'TODO') == 'TODO'

def test_issue_60():
    assert ssf.format('#"abded"\\ ??/??', 12.3456789) == '12abded 28/81'
    assert ssf.format('? "a" / "b" ?', 0.5) == '1 a / b 2'
    assert ssf.format('? "a" / "b" 2', 0.5) == '1 a / b 2'
    assert ssf.format('# "h" ? "a" / "b" ?', 1.4) == '1 h 2 a / b 5'
    assert ssf.format('# "h" ? "a" / "b" ?', -1.4) == '-1 h 2 a / b 5'
    assert ssf.format('# "h" ? "a" / "b" ?', 1) == '1            '
    assert ssf.format('# "h" ? "a" / "b" ?', -1) == '-1            '

def test_issue_61():
    assert ssf.format(r'???\/???', 123.45) == '   /123'
    assert ssf.format(r'# ??\/??', -12.3456789) == '-   /12'
    # This is an error: assert ssf.format(r'???/', 123.45) == '123/'
    # So is this:       assert ssf.format(r'/???', 123.45) == '/123'

def test_issue_62():
    cases = [
            ('##0.0E+0',
                {0: '000.0E+0', 1: '1.0E+0', 5: '5.0E+0', 10: '10.0E+0', 89: '89.0E+0', 89.1: '89.1E+0',
                 100: '100.0E+0', 1000: '1.0E+3', 10000: '10.0E+3', 100000: '100.0E+3', 1000000: '1.0E+6'}),
            ('##0.0E-0',
                {0: '000.0E0', 1: '1.0E0', 5: '5.0E0', 10: '10.0E0', 89: '89.0E0', 89.1: '89.1E0',
                 100: '100.0E0', 1000: '1.0E3', 10000: '10.0E3', 100000: '100.0E3', 1000000: '1.0E6'}),
            ('##0.0E+00',
                {0: '000.0E+00', 1: '1.0E+00', 5: '5.0E+00', 10: '10.0E+00', 89: '89.0E+00', 89.1: '89.1E+00',
                 100: '100.0E+00', 1000: '1.0E+03', 10000: '10.0E+03', 100000: '100.0E+03', 1000000: '1.0E+06'}),
            ('##0.0E-00',
                {0: '000.0E00', 1: '1.0E00', 5: '5.0E00', 10: '10.0E00', 89: '89.0E00', 89.1: '89.1E00',
                 100: '100.0E00', 1000: '1.0E03', 10000: '10.0E03', 100000: '100.0E03', 1000000: '1.0E06'}),
            ]

    for case in cases:
        fmt = case[0]
        for val, expected in case[1].items():
            actual = ssf.format(fmt, val)
            assert actual == expected

def test_issue_64():
    assert ssf.format('?.?', 1) == '1. '
    assert ssf.format('?.?', 1.2) == '1.2'

def test_issue_65():
    assert ssf.format('000.0', 1) == '001.0'
    assert ssf.format('000.#', 1) == '001.'
    assert ssf.format('000.0', 1.2) == '001.2'
    assert ssf.format('000.#', 1.2) == '001.2'

def test_issue_66():
    assert ssf.format('# ?/10', 0) == '0     '

def test_issue_67():
    assert ssf.format('0"abde".0"??"000E+00', 12.3456789) == '1abde.2??346E+01'
    assert ssf.format('0"abde".0"??"000E+0', 12.3456789) == '1abde.2??346E+1'
    assert ssf.format('0"abde".0"??"000E+00', -12.3456789) == '-1abde.2??346E+01'
    assert ssf.format('0"abde".0"??"000E-00', -12.3456789) == '-1abde.2??346E01'
    assert ssf.format('0"abde".0"??"000E-0', -12.3456789) == '-1abde.2??346E1'
    assert ssf.format('0"abde".0"??"000E-00', -12.3456789E-2) == '-1abde.2??346E-01'
    assert ssf.format('0"abde".0"??"000E+00', -12.3456789E-2) == '-1abde.2??346E-01'
    assert ssf.format('0"abde".0"??"000E+0', -12.3456789E-2) == '-1abde.2??346E-1'

def test_issue_68():
    assert ssf.format('00.00.00.000', 12.3456789) == '12.34.56.789'

def test_issue_69():
    ssfe = SSF(errors='raise')
    try:
        ssf.format('HH[MM]', 0)
        assert False
    except Exception:
        pass
    try:
        ssf.format('HH[M]', 0)
        assert False
    except Exception:
        pass

def test_issue_70():
    assert ssf.format(r'[<=9999999]###\-####;\(###\)\ ###\-####', -12.3) == '--12'  # yes, this is right!
    assert ssf.format('[=0]?;#,##0.00', -12.3) == '-12.30'
    assert ssfc.format('[Red]General;[Blue][>=0]General', 10) == 'Red:10'
    assert ssfc.format('[Red]General;[Blue][>=0]General', 0) == 'Blue:0'
    assert ssfc.format('[Red]General;[Blue][>=0]General', -10) == '##########'
    assert ssfc.format('[Red]General;[Blue][>=0]General;', 10) == 'Red:10'
    assert ssfc.format('[Red]General;[Blue][>=0]General;', 0) == 'Blue:0'
    assert ssfc.format('[Red]General;[Blue][>=0]General;', -10) == '-'
    assert ssfc.format('[Red][=0]General;[Blue]General;[Green]General', 10) == 'Green:10'
    assert ssfc.format('[Red][=0]General;[Blue]General;[Green]General', 0) == 'Red:0'
    assert ssfc.format('[Red][=0]General;[Blue]General;[Green]General', -10) == 'Blue:10'
    assert ssfc.format('[Red]General;[Blue][>=-10]General', 10) == 'Red:10'
    assert ssfc.format('[Red]General;[Blue][>=-10]General', 0) == 'Blue:0'
    assert ssfc.format('[Red]General;[Blue][>=-10]General', -10) == 'Blue:-10'

def test_issue_71():
    assert ssf.format('[HH]', -12) == '-288'
    assert ssf.format('[HH]', -11.999999) == '-288'
    assert ssf.format('[HH]', -11.99999) == '-287'

def test_issue_72():
    assert ssf.format(r'\c\c\c?????0"aaaa"0"bbbb"000000.00%', -12.3456789) == '-ccc     0aaaa0bbbb001234.57%'

def test_issue_73():
    assert ssf.format("##0.0E-00", 1) == '1.0E00'
    assert ssf.format("##0.0E-00", 1.2) == '1.2E00'

def test_issue_74():
    assert ssf.format('#,### ?/10', 1000.1) == '1,000 1/10'

def test_issue_75():
    assert ssf.format('"s"??/?????????"e"', 0.123251512342345) == 's480894/3901729  e'

def test_issue_76():
    assert ssf.format('?/???', 0.5) == '1/2  '
    assert ssf.format('# ?/???', 0.5) == ' 1/2  '

def test_issue_77():
    assert ssf.format('#????', -12.3) == '-  12'
    assert ssf.format('#????', -12) == '-  12'

def test_issue_78():
    with open('tests/ssf78.tsv', 'r') as t78:
        data = t78.read().splitlines()

    row1 = data[0].split('\t')[2:]
    for i, c in enumerate(row1, start=2):
        for row in data[1:]:
            spl = row.split('\t')
            fmt = spl[0].format(c)
            actual = ssf.format(fmt, int(spl[1]))
            expected = spl[i]
            assert actual == expected
