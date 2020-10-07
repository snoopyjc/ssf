#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
ssf = SSF(errors='raise')
import warnings
import re

#var fs = require('fs');
#var data = fs.readFileSync('./test/valid.tsv','utf8').split("\n");
with open('tests/valid2.tsv', 'r', encoding="utf-8") as d:
    data = d.read().split("\n")


#var _data = [0, 1, -2, 3.45, -67.89, "foo"];
#_data = [0, 1, -2, 3.45, -67.89, "foo"]
def floatit(d):
    try:
        return float(d)
    except Exception:
        return d

def unescape(s):
    """Excel save as tsv escaped all '"' chars - undo that!"""
    if len(s) < 2:
        return s
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('""', '"')
    return s

_data = [floatit(d) for d in data[0].split('\t')[1:]]
#function doit(d) {
def doit(d):
#  it(d[0], function() {
#    for(var w = 0; w < _data.length; ++w) {
    for w in range(len(_data)):
#      SSF.format(d[0], _data[w]);
        #print(f'ssf.format({d[0]}, {_data[w]})')
        known_issue = None
        if re.match(r'#\d+', d[-1]) or d[-1] == '#Excel':
            known_issue = d[-1]
        actual = ssf.format(unescape(d[0]), _data[w])
        expected = unescape(d[w+1])
        if known_issue and actual != expected:
            warnings.warn(f'For ssf.format({unescape(d[0])}, {_data[w]}), "{actual}" != "{expected}" due to issue {known_issue}')
            continue
        if actual != expected:
            with open('valid.out', 'w', encoding="utf-8") as o:
                print(f'ssf.format({unescape(d[0])}, {_data[w]}) = (actual/expected)', file=o)
                print(actual, file=o)
                print(expected, file=o)
        assert actual == expected

#    }
#  });
#}
#describe('valid formats', function() {
def test_valid():
#  for(var j=0;j<data.length;++j) {
    for j in range(1, len(data)):       # Skip header
#    if(!data[j]) return;
        if not data[j]:
            return
#    doit(data[j].replace(/#{255}/g,"").split("\t"));
        doit(data[j].replace('\255', "").split("\t"))
#  }
#});
