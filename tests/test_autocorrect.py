from ssf import SSF
ssf = SSF()

def test_autocorrect_format():
    assert ssf.format('0E0', 1e2) == '1E+2'
    assert ssf.format('0e0', 1e2) == '1E+2'
    assert ssf.format('0.E-0', 1e2) == '1.E2'
    assert ssf.format('0.e-0', 1e2) == '1.E2'
    assert ssf.format('"e"0e0', 1e2) == 'e1E+2'
    assert ssf.format('E', 1) == '1900'
    assert ssf.format(r'\EE', 1) == 'E1900'
    assert ssf.format('#.##,,', 1E7) == '10.'
    assert ssf.format('#.,##,', 1E7) == '10.'
    assert ssf.format('ShortDate', 1) == ssf.format('Short Date', 1)
    assert ssf.format('longDate', 1) == ssf.format('Long Date', 1)
    assert ssf.format('.m,m,', 1) == '1.1,1,'
