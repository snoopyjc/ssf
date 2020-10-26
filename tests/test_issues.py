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

def test_issue_7():
    assert ssf.format('#', 1e24) == '1000000000000000000000000'
    assert ssf.format('#', -1e24) == '-1000000000000000000000000'
    assert ssf.format('#', 100000000000000000000000) == '100000000000000000000000'
    assert ssf.format('#', 123456789012345678901234) == '123456789012345678901234'
    assert ssf.format('#', -100000000000000000000000) == '-100000000000000000000000'
