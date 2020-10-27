#!/home/jorost/venv/bin/python
from ssf import SSF
import cgi
import cgitb
import json
#import base64
from urllib.parse import quote
cgitb.enable()
#cgi.test()
cgi.parse()
form=cgi.FieldStorage()
ssf = SSF(color_pre="<span style='color: #{rgb};'>", color_post="</span>")
locale = form.getfirst('locale', default=None)
if locale == 'None':
    locale = None
getfmt = form.getfirst('getfmt', default=None)
if getfmt is not None:
    places = None
    thousands_sep = None
    negative = None
    positive_sign_exponent = False
    for key in form.keys():
        if 'places' in key:
            places = form.getfirst(key, default=None)
            if places is not None and places.isdigit():
                places = int(places)
        elif 'thousands' in key:
            thousands_sep = True
        elif 'negative' in key:
            negative = form.getfirst(key, default=None)
        elif 'positive' in key:
            positive_sign_exponent = True
    result = ssf.get_format(type=getfmt, places=places, use_thousands_separator=thousands_sep,
            negative_numbers=negative, positive_sign_exponent=positive_sign_exponent, locale=locale)
else:
    fmt = form.getfirst('fmt', '')
    val = form.getfirst('val', '')
    try:
        val = float(val)
    except Exception:
        pass
    
    width = form.getfirst('width', default=None)
    if width is not None and width.isdigit():
        width = int(width)
    else:
        width = None
    result = ssf.format(fmt, val, width=width, locale=locale)

print("Content-Type: text/plain; charset=UTF-8")
print()
print(quote(result))
