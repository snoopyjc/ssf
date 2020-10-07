from ssf import SSF

ssf = SSF(locale='en-US')

def test_get_format_general():
    assert ssf.get_format() == 'General'

def test_get_format_number():
    assert ssf.get_format('number') == '0.00'
    assert ssf.get_format('number', places=2) == '0.00'
    assert ssf.get_format('number', places=0) == '0'
    assert ssf.get_format('number', places=3) == '0.000'
    assert ssf.get_format('number', places=8) == '0.00000000'
    assert ssf.get_format('NUMBER', use_thousands_separator=True) == '#,##0.00'
    assert ssf.get_format('NUMBER', places=2, use_thousands_separator=True) == '#,##0.00'
    assert ssf.get_format('NUMBER', places=0, use_thousands_separator=True) == '#,##0'
    assert ssf.get_format('NUMBER', places=6, use_thousands_separator=True) == '#,##0.000000'
    assert ssf.get_format('Number', negative_numbers='red') == '0.00;[Red]0.00'
    assert ssf.get_format('Number', negative_numbers='redparen') == '_(0.00_);[Red](0.00)'
    assert ssf.get_format('Number', negative_numbers='red,paren') == '_(0.00_);[Red](0.00)'
    assert ssf.get_format('Number', negative_numbers='red()') == '_(0.00_);[Red](0.00)'
    assert ssf.get_format('Number', negative_numbers='paren') == '_(0.00_);(0.00)'
    assert ssf.get_format('Number', negative_numbers='parens') == '_(0.00_);(0.00)'
    assert ssf.get_format('Number', negative_numbers='()') == '_(0.00_);(0.00)'
    assert ssf.get_format('Number', use_thousands_separator=True, negative_numbers='()') == '_(#,##0.00_);(#,##0.00)'
    assert ssf.get_format('Number', places=0, use_thousands_separator=True, negative_numbers='()') == '_(#,##0_);(#,##0)'

ssff = SSF(locale='fi-FI')      # Welcome to Finland
#ssfa = SSF(locale=0x44D)

def test_get_format_currency():
    assert ssf.get_format('Currency') == '$#,##0.00'
    assert ssf.get_format('Currency', use_thousands_separator=True) == '$#,##0.00'
    assert ssf.get_format('Currency', use_thousands_separator=False) == '$0.00'
    assert ssf.get_format('Currency', negative_numbers='()') == '$#,##0.00_);($#,##0.00);$#,##0.00_);_(@_)'
    assert ssf.get_format('Currency', negative_numbers='red()') == '$#,##0.00_);[Red]($#,##0.00);$#,##0.00_);_(@_)'
    assert ssf.get_format('Currency', negative_numbers='<<-') == '$#,##0.00'
    assert ssf.get_format('Currency', negative_numbers='-') == '$#,##0.00'
    assert ssf.get_format('Currency', negative_numbers='>>-') == '$#,##0.00_-;$#,##0.00-;$#,##0.00_-;@_-'
    assert ssf.get_format('Currency', negative_numbers='<-') == '$#,##0.00;$-#,##0.00;$#,##0.00;@'
    assert ssf.get_format('Currency', negative_numbers='>-') == '$#,##0.00_-;$#,##0.00-;$#,##0.00_-;@_-'
    assert ssff.get_format('Currency') == '#,##0.00 [$€]'       # Euro at end with prior space
    assert ssf.get_format('Currency', locale='fi-FI') == '#,##0.00 [$€]'

def test_get_format_accounting():
    assert ssf.get_format('Accounting') == '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
    assert ssf.get_format('Accounting', use_thousands_separator=True) == '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
    assert ssf.get_format('Accounting', negative_numbers='()', use_thousands_separator=True) == '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
    assert ssff.get_format('Accounting') == '_-* #,##0.00 [$€];-* #,##0.00 [$€];_-* "-"?? [$€];_-@' # Euro at end
    # The locale on my PC is messed up for this one!  assert ssfa.get_format('Accounting') == ' * #,##0.00_-[$₹]; * #,##0.00-[$₹]; * "-"??_-[$₹]; @'

def test_get_format_dates():
    assert ssf.get_format('Date') == 'm/dd/yyyy'
    assert ssf.get_format('Short Date') == 'm/dd/yyyy'
    assert ssf.get_format('Long Date') == "[$-F800]dddd, mmmm dd, yyyy"
    assert ssf.get_format('Time') == '[$-F400]h:mm:ss AM/PM'

def test_get_format_percentage():
    assert ssf.get_format('PeRcEnTaGe') == '0.00%'
    assert ssf.get_format('Percentage', places=2) == '0.00%'
    assert ssf.get_format('Percentage', places=0) == '0%'
    assert ssf.get_format('Percentage', places=1) == '0.0%'
    assert ssf.get_format('Percentage', places=7) == '0.0000000%'

def test_get_format_fraction():
    assert ssf.get_format('Fraction') == '# ?/?'
    assert ssf.get_format('Fraction', fraction_denominator=-2) == '# ??/??'
    assert ssf.get_format(fraction_denominator=-2) == '# ??/??'
    assert ssf.get_format('Fraction', fraction_denominator=-5) == '# ?????/?????'
    assert ssf.get_format('Fraction', fraction_denominator=1) == '# ?/1'
    assert ssf.get_format('Fraction', fraction_denominator=5) == '# ?/5'
    assert ssf.get_format('Fraction', fraction_denominator=99) == '# ??/99'
    assert ssf.get_format('Fraction', fraction_denominator=1024) == '# ????/1024'
    assert ssf.get_format('Fraction', fraction_denominator=0) == '"##########"'

def test_get_format_scientific():
    assert ssf.get_format('scientific') == '0.00E+00'
    assert ssf.get_format('scientific', places=2, positive_sign_exponent=True) == '0.00E+00'
    assert ssf.get_format('scientific', places=4, positive_sign_exponent=True) == '0.0000E+00'
    assert ssf.get_format('scientific', places=2, positive_sign_exponent=False) == '0.00E-00'
    assert ssf.get_format('scientific', places=3, positive_sign_exponent=False) == '0.000E-00'

def test_get_format_text():
    assert ssf.get_format('Text') == '@'

