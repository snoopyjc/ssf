#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
import json
ssf = SSF()
#var fs = require('fs'), assert = require('assert');
#var data = JSON.parse(fs.readFileSync('./test/fraction.json','utf8'));
with open('tests/fraction.json', 'r', encoding='utf-8') as d:
    data = json.load(d)
#var skip = [];
#describe('fractional formats', function() {
def test_fractional_formats():
#  data.forEach(function(d) {
    for d in data:
#    it(d[1]+" for "+d[0], skip.indexOf(d[1]) > -1 ? null : function(){
#      var expected = d[2], actual = SSF.format(d[1], d[0], {});
        expected = d[2]
        actual = ssf.format(d[1], d[0])
#      //var r = actual.match(/(-?)\d* *\d+\/\d+/);
#      assert.equal(actual, expected);
        assert actual == expected and d[1] == d[1] and d[0] == d[0]
#    });
#  });
#});
