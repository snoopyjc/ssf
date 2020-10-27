#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
import json
ssf = SSF(errors='raise')
#var fs = require('fs'), assert = require('assert');
#var data = JSON.parse(fs.readFileSync('./test/oddities.json','utf8'));
with open('tests/oddities.json', 'r', encoding='utf-8') as d:
    data = json.load(d)

#describe('oddities', function() {
def test_oddities():
#  data.forEach(function(d) {
    for d in data:
#    it(String(d[0]), function(){
#      for(var j=1;j<d.length;++j) {
        for j in range(1, len(d)):
#        if(d[j].length == 2) {
            if len(d[j]) == 2:
#          var expected = d[j][1], actual = SSF.format(d[0], d[j][0], {});
                expected = d[j][1]
                actual = ssf.format(d[0], d[j][0])
#          assert.equal(actual, expected);
                assert actual == expected and d[0] == d[0] and d[j][0] == d[j][0]
#        } else if(d[j][2] !== "#") assert.throws(function() { SSF.format(d[0], d[j][0]); });
            elif len(d[j]) < 3 or d[j][2] != "#":
                try:
                    ssf.format(d[0], d[j][0])
                    assert d[0] != d[0] and d[j][0] != d[j][0]  # Failed
                except ValueError:
                    pass        # Passed
#      }
#    });
#  });
def test_bad_oddities():
#  it('should fail for bad formats', function() {
#    var bad = ['##,##'];
    # Issue #12 bad = ['[', ']', '"', '\\', '_', '*']       # Python version allows ##,##
    bad = ['[', '"', '\\', '_', '*']       # Issue #12: Python version allows ##,## and ']'
#    var chk = function(fmt){ return function(){ SSF.format(fmt,0); }; };
    for fmt in bad:
        try:
            ssf.format(fmt, 0)
            assert fmt != fmt       # Failed
        except ValueError:
            pass                    # Passed
#    bad.forEach(function(fmt){assert.throws(chk(fmt));});
#  });
#});
