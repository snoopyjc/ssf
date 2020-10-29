from ssf import SSF
from datetime import datetime, date, timedelta, time

ssf = SSF(errors='raise')

def test_code_coverage1():
    """Tests to improve code coverage."""

    # normalize_locale
    assert ssf.format('#,###', 1000, locale='de-DE.extra') == '1.000'
    assert ssf.format('#,###', 1000, locale='de-DE@extra') == '1.000'

    # commaify
    ssfn = SSF(locale_support=False)
    assert ssfn.format('?,???,???', 1000) == '   1,000'
    assert ssfn.format('#,###', 1) == '1'

    # parse_date_code
    assert ssf.format('[hh]', -1+0.00001/86400) == '-24'

    # general_fmt
    assert ssf.format('General', True) == 'TRUE'
    assert ssf.format('General', False) == 'FALSE'
    assert ssf.format('General', True, align='left', width=6) == 'TRUE  '
    assert ssf.format('General', False, align='left', width=9) == 'FALSE    '
    assert ssf.format('General', True, align='right', width=6) == '  TRUE'
    assert ssf.format('General', False, align='right', width=9) == '    FALSE'

    assert ssf.format('General', timedelta(days=1)) == '1'
    assert ssf.format('General', None) == ''
    assert ssf.format('General', None, width=2) == '  '
    assert ssf.format('General', time(12, 0, 0)) == '1/0/1900'
    assert ssf.format('@', time(12, 0, 0)) == '0.5'
    try:
        actual = ssf.format('General', object())
        assert 'object object at' in actual
    except ValueError as e:     # Can't really get here
        assert 'unsupported value' in str(e)

    # write_date
    assert ssf.format('s', 0) == '0'
    assert ssf.format('s', 1/86400) == '1'

    # write_num_exp
    assert ssf.format('###.00E+0', 0) == '000.00E+0'
    assert ssf.format('###.00E+0', 0.0) == '000.00E+0'
    assert ssf.format('###.00E+0', 1.2E-4) == '120.00E-6'

    # write_num_f2
    assert ssf.format('# ?/2', 1) == '1    '
    assert ssf.format('?/2', 1) == '2/2'
    assert ssf.format('?/?', 1) == '1/1'
    assert ssf.format('?/?', 2) == '2/1'

    # write_num_flt / int
    assert ssf.format(r'(###) ###\-####', 2125551212.01) == '(212) 555-1212'
    assert ssf.format(r'(###) ###\-####', 2125551212) == '(212) 555-1212'
    assert ssf.format('00000-0000', 5270101.01) == '00527-0101'
    assert ssf.format('00000-0000', 5270101) == '00527-0101'
    assert ssf.format('0', True) == 'TRUE'
    assert ssf.format('0', False) == 'FALSE'

    # _eval_fmt
    try:
        ssf.format('0"a', 0)
        assert False        # Failed to catch error
    except ValueError as e:
        assert 'unterminated string' in str(e)

    assert ssf.format('b1', -1) == '##########'

    try:
        ssf.format('[red', 0)
        assert False        # Failed to catch error
    except ValueError as e:
        assert 'unterminated' in str(e)

    try:
        ssf.format('[$-12345678]0.00E+00', -1.23E+45)
    except ValueError as e:
        assert 'Cannot handle' in str(e)

    assert ssf.format('[ss]', datetime(9999, 12, 31, 23, 59, 59, 999999)) == '##########'

def test_code_coverage2():
    # _replace_numbers
    assert ssf.format('[$-1E000000]0.00E+00', -1.23E+45) == '-一.二三五百四五'
    assert ssf.format('[$-1E000000]0.00E+00', -1.23E-45) == '-一.二三五万四五'

    # _get_locale
    ssfi = SSF(errors='ignore')
    assert ssfi.format('#,###,###.##', 1000.1, locale='deDE') == '1,000.1'      # Bad locale - ignored

    try:
        ssf.format('#,###,###.##', 1000.1, locale='deDE')
        assert False        # failed
    except Exception as e:
        assert 'Locale' in str(e)

    # format
    ssfe = SSF(locale='deDE', errors='pounds')
    assert ssfe.format('0', 0) == '##########'

    assert ssf.format(1024, 1025) == '1025'     # Incorrect format number defaults to General

    ssfp = SSF(errors='#')
    assert ssfp.format('[red', 0) == '##########'

    # SSF_CALENDAR

    try:
        ssf.format('[$-7F0000]yyyy', 100)
        assert False
    except ValueError:
        pass

    # _escape_dots

    assert ssf.format(r'[Red]\x"abc"0.0.0.0', 1234.567) == 'xabc1234.5.6.7'

    # set_day_names

    try:
        ssf.set_day_names(['Monday', 'Tuesday'])
        assert False    # Failed
    except ValueError:
        pass

    try:
        ssf.set_day_names(["1", "2", "3", "4", "5", "6", "7"])
        assert False    # Failed
    except ValueError:
        pass

    try:
        ssf.set_day_names([1, 2, 3, 4, 5, 6, 7])
        assert False    # Failed
    except ValueError:
        pass

    try:
        ssf.set_day_names([(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7)])
        assert False    # Failed
    except ValueError:
        pass

    # set_month_names

    try:
        ssf.set_month_names(['Jan', 'Feb'])
        assert False    # Failed
    except ValueError:
        pass

    try:
        ssf.set_month_names([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        assert False    # Failed
    except ValueError:
        pass

    try:
        ssf.set_month_names([0, ("J", "Jan"), ("F", "Feb"), ("M", "Mar"), ("A", "Apr"),
            ("M", "May"), ("J", "Jun"), ("J", "Jul"), ("A", "Aug"), ("S", "Sep"),
            ("O", "Oct"), ("N", "Nov"), ("D", "Dec")])  # Missing the long version
        assert False    # Failed
    except ValueError:
        pass

    try:
        ssf.set_month_names([0, (1,1,1), (2,2,2), (3,3,3), (4,4,4), (5,5,5), (6,6,6), (7,7,7), (8,8,8), (9,9,9),
            (10,10,10), (11,11,11), (12,12,12)])
        assert False    # Failed
    except ValueError:
        pass
