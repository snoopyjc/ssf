from ssf import SSF
ssf = SSF(errors='raise')

def test_get_set_days():
    dn = ssf.get_day_names()
    assert isinstance(dn, tuple)
    assert dn == (('Mon', 'Monday'),
            ('Tue', 'Tuesday'),
            ('Wed', 'Wednesday'),
            ('Thu', 'Thursday'),
            ('Fri', 'Friday'),
            ('Sat', 'Saturday'),
            ('Sun', 'Sunday'))

    ssf.set_day_names([['MO', 'MON'],
        ('TU', 'TUE'), ['WE', 'WED'],
        ('TH', 'THU'), ['FR', 'FRI'],
        ('SA', 'SAT'), ['SU', 'SUN']])

    assert ssf.format('ddd dddd', '10/3/2020') == 'SA SAT'
    assert ssf.format('ddd dddd', '10/4/2020') == 'SU SUN'
    assert ssf.format('ddd dddd', '10/5/2020') == 'MO MON'
    assert ssf.format('ddd dddd', '10/6/2020') == 'TU TUE'
    assert ssf.format('ddd dddd', '10/7/2020') == 'WE WED'
    assert ssf.format('ddd dddd', '10/8/2020') == 'TH THU'
    assert ssf.format('ddd dddd', '10/9/2020') == 'FR FRI'

    try:
        ssf.set_day_names(2)
        assert False        # Failed
    except ValueError:
        pass

    try:
        ssf.set_day_names((1, 2, 3, 4, 5, 6, 7))
        assert False        # Failed
    except ValueError:
        pass

def test_get_set_months():
    mn = ssf.get_month_names()
    assert isinstance(mn, tuple)
    assert mn == (None, ('J', 'Jan', 'January'), ('F', 'Feb', 'February'), ('M', 'Mar', 'March'),
            ('A', 'Apr', 'April'), ('M', 'May', 'May'), ('J', 'Jun', 'June'), ('J', 'Jul', 'July'), 
            ('A', 'Aug', 'August'), ('S', 'Sep', 'September'), ('O', 'Oct', 'October'), 
            ('N', 'Nov', 'November'), ('D', 'Dec', 'December'))

    ssf.set_month_names(mn[:-1] + (('X', 'DE', 'DEC'),) )

    assert ssf.format('mmmmm mmm mmmm', '12/3/2020') == 'X DE DEC'

    try:
        ssf.set_month_names(2)
        assert False        # Failed
    except ValueError:
        pass

    try:
        ssf.set_month_names((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
        assert False        # Failed
    except ValueError:
        pass
        
def test_get_load_table():
    t = ssf.get_table()
    assert t[0] == 'General'
    assert t[1] == '0'
    assert t[14] == 'm/d/yyyy'
    assert t[49] == '@'

    ssf.load_table({104:'yyyy-mm-dd', 105:'0.0'})
    assert ssf.format(104, '10/6/2020') == '2020-10-06'
    assert ssf.format(105, 3.4) == '3.4'

    assert ssf.load('0') == 1
    assert ssf.load('mmm mmmm') == 5        # Will be inserted at 5
    assert ssf.load('@') == 49

    assert ssf.format(5, '10/6/2020') == 'Oct October'
