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
