#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
ssf = SSF()
#var fs = require('fs');
#var data = fs.readFileSync('./test/exp.tsv','utf8').split("\n");
with open('tests/exp.tsv', 'r', encoding='utf-8') as d:
    data = d.read().split("\n")
#function doit(d, headers) {
def doit(d, headers):
#  it(d[0], function() {
#    for(var w = 1; w < headers.length; ++w) {
    for w in range(1, len(headers)):
#      var expected = d[w].replace("|", ""), actual;
        expected = d[w].replace("|", "")
#      try { actual = SSF.format(headers[w], parseFloat(d[0]), {}); } catch(e) { }
        try:
            actual = ssf.format(headers[w], float(d[0]))
        except Exception as e:
            print(f'test_exp: Exception on ssf.format({headers[w]}, {d[0]}): {e}')
            actual = None
#      if(actual != expected && d[w].charAt(0) !== "|") throw new Error([actual, expected, w, headers[w],d[0],d].join("|"));
        assert actual == expected or d[w][0] == "|"
#    }
#  });
#}
#describe('exponential formats', function() {
def test_exponential_formats():
#  var headers = data[0].split("\t");
    headers = data[0].split("\t")
#  for(var j=1;j<data.length;++j) {
    for j in range(1, len(data)):
#    if(!data[j]) return;
        if not data[j]:
            return
#    doit(data[j].replace(/#{255}/g,"").split("\t"), headers);
        doit(data[j].replace('\255', '').split("\t"), headers)
#  }
#});
