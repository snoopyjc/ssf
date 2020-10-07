#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
from .number import Number
#var fs = require('fs');
#var data = fs.readFileSync('./test/comma.tsv','utf8').split("\n");
with open('tests/comma.tsv', 'r', encoding='utf-8') as d:
    data = d.read().split("\n")

ssf = SSF()

#
#function doit(w, headers) {
def doit(w, headers):
#  it(headers[w], function() {
#    for(var j=1;j<data.length;++j) {
    for j in range(1, len(data)):
#      if(!data[j]) continue;
        if not data[j]:
            continue
#      var d = data[j].replace(/#{255}/g,"").split("\t");
        d = data[j].replace('\255', "").split("\t")
        actual = None
#      var expected = d[w].replace("|", ""), actual;
        expected = d[w].replace("|", "")
#      try { actual = SSF.format(headers[w], Number(d[0]), {}); } catch(e) { }
        try:
            actual = ssf.format(headers[w], Number(d[0]))
        except Exception as e:
            print(f'Exception {e} on ssf.format({headers[w]}, {Number(d[0])})')
        assert actual == expected and d[w][0] != '|'
#      if(actual != expected && d[w][0] !== "|") throw new Error([actual, expected, w, headers[w],d[0],d].join("|"));
#    }
#  });
#}
#describe('comma formats', function() {
#  var headers = data[0].split("\t");
def test_comma():
    headers = data[0].split("\t")
    for w in range(1, len(headers)):
        doit(w, headers)
#  for(var w = 1; w < headers.length; ++w) doit(w, headers);
#});
