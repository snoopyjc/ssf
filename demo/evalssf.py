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
locale = form.getfirst('locale', default=None)
if locale == 'None':
    locale = None
ssf = SSF()

#print("Content-Type: application/json; charset=UTF-8")
print("Content-Type: text/plain; charset=UTF-8")
print()
result = ssf.format(fmt, val, width=width, locale=locale)
#print(json.dumps(dict(result=result)))
#print(result)
#print(base64.encodebytes(result.encode('utf-8')))
print(quote(result))
