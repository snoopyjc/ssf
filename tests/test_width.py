from ssf import SSF
ssf = SSF()
from datetime import date
import os
import re

def test_width():

    def is_centered(s):
        left = len(s) - len(s.lstrip())
        right = len(s) - len(s.rstrip())
        return (abs(left-right) <= 1)

    for width in range(30):
        # Right justified
        actual = ssf.format('General', 1, width=width)
        expected = (' ' * (width-1)) + '1' if width > 0 else ''
        assert actual == expected

        actual = ssf.format('General', -1.5, width=width)
        expected = (' ' * (width-4)) + '-1.5'
        if width <= 1:
            expected = '#' * width
        elif width < 4:
            expected = (' ' * (width-2)) + '-2'
        assert actual == expected

        actual = ssf.format('General', 9.999, width=width)
        expected = (' ' * (width-5)) + '9.999'
        if width <= 1:
            expected = '#' * width
        elif width < 5:
            expected = (' ' * (width-2)) + '10'
        assert actual == expected

        actual = ssf.format('General', date(2000, 1, 1), width=width)
        expected = (' ' * (width-8)) + '1/1/2000'
        if width < len('1/1/2000'):
            expected = '#' * width
        assert actual == expected

        actual = ssf.format('ss', -2, width=width)
        expected = '#' * width
        assert actual == expected

        actual = ssf.format('General', 'a', width=width, align='right')
        expected = (' ' * (width-1)) + 'a'
        assert actual == expected

        actual = ssf.format('@', 'a', width=width, align='right')
        expected = (' ' * (width-1)) + 'a'
        assert actual == expected

        # Left justified
        actual = ssf.format('General', 'a', width=width)
        expected = 'a' + (' ' * (width-1))
        assert actual == expected

        actual = ssf.format('@', 'a', width=width)
        expected = 'a' + (' ' * (width-1))
        assert actual == expected

        actual = ssf.format('@', 1, width=width)
        expected = '1' + (' ' * (width-1)) if width > 0 else ''
        assert actual == expected

        actual = ssf.format('0', 1, width=width, align='left')
        expected = '1' + (' ' * (width-1)) if width > 0 else ''
        assert actual == expected

        actual = ssf.format('General', 1, width=width, align='left')
        expected = '1' + (' ' * (width-1)) if width > 0 else ''
        assert actual == expected

        actual = ssf.format('@', -1.5, width=width)
        expected = '-1.5' + (' ' * (width-4))
        if width <= 1:
            expected = '#' * width
        elif width < 4:
            expected = '-2' + (' ' * (width-2))
        assert actual == expected

        actual = ssf.format('@', 9.999, width=width)
        expected = '9.999' + (' ' * (width-5))
        if width <= 1:
            expected = '#' * width
        elif width < 5:
            expected = '10' + (' ' * (width-2))
        assert actual == expected

        # Centered
        for fmt in ('General', '0', '@'):
            actual = ssf.format(fmt, 1, width=width, align='center')
            assert len(actual) == width
            if width >= 1:
                assert '1' in actual
            assert is_centered(actual)

        for fmt in ('General', '@', '"a"@'):
            actual = ssf.format(fmt, True, width=width)
            value = 'TRUE'
            if fmt[0] == '"':
                value = 'aTRUE'
            lv = len(value)
            if width < lv:
                assert actual == '#' * width
            else:
                assert len(actual) == max(width, lv)
                assert value in actual
                assert is_centered(actual)

            actual = ssf.format(fmt, False, width=width)
            value = 'FALSE'
            if fmt[0] == '"':
                value = 'aFALSE'
            lv = len(value)
            if width < lv:
                assert actual == '#' * width
            else:
                assert len(actual) == max(width, lv)
                assert value in actual
                assert is_centered(actual)

        # Filled
        actual = ssf.format('*=0', 1, width=width)
        expected = ('=' * (width-1)) + '1' if width > 0 else ''
        assert actual == expected

        actual = ssf.format('*=@', True, width=width)
        expected = ('=' * (width-4)) + 'TRUE' if width >= 4 else '#' * width
        assert actual == expected

        actual = ssf.format('0.0*-', -1.5, width=width)
        expected = '-1.5' + ('-' * (width-4)) if width >= 4 else '#' * width
        assert actual == expected

        actual = ssf.format('*=0.0*-', -1.5, width=width)   # Right-most wins
        expected = '-1.5' + ('-' * (width-4)) if width >= 4 else '#' * width
        assert actual == expected

        actual = ssf.format('@*#', True, width=width)
        expected = 'TRUE' + ('#' * (width-4)) if width >= 4 else '#' * width
        assert actual == expected

def test_general_width():
    values = [0, 1, 1.23456789, 2.345678901234, 9.999999]
    expected = [['abc']]

    gwf = 'tests/general_width.tsv'
    if not os.path.isfile(gwf):
        with open(gwf, 'w') as gw:
            for s in (1, -1):
                for v in values:
                    for e in range(-12, 12+1):
                        if v == 0 and (e != 0 or s != 1):    # There is only 1 zero!
                            continue
                        for w in range(12+1):
                            val = v * 10**e * s
                            actual = ssf.format('General', val, width=w)
                            print(f'{s}\t{v}\t{e}\t{w}\t{actual}', file=gw)
            assert False        # Check all values!
    else:
        with open(gwf, 'r') as gw:
            lines = gw.read().splitlines()

        for lno, line in enumerate(lines, start=1):
            sign, value, exponent, width, expected = line.split('\t')
            val = float(value) * int(sign) * 10**int(exponent)
            if int(val) == val:
                val = int(val)
            iw = int(width)
            actual = ssf.format('General', val, width=iw)
            assert actual == expected
            actual = ssf.format('@', val, width=iw)
            expected = expected.strip()
            expected = expected + (' ' * (iw-len(expected)))    # Left justify in width
            assert actual == expected

def test_default_width():
    ssfw = SSF(default_width=2)
    assert ssfw.format('0', 1) == ' 1'
    assert ssfw.format('@', 1) == '1 '
    assert ssfw.format('General', 1) == ' 1'
    assert ssfw.format('General', 'a') == 'a '
    assert ssfw.format('General', 123) == '##'
