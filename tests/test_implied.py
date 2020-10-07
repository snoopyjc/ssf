#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
import json
ssf = SSF(dateNF='m/d/yy')  # Match the (old) format of the test data
#ssf.load('m/d/yy', 14)
#var fs = require('fs'), assert = require('assert');
#var data = JSON.parse(fs.readFileSync('./test/implied.json','utf8'));
with open('tests/implied.json', 'r', encoding='utf-8') as d:
    data = json.load(d)
#var skip = [];
skip = []           # ???
#function doit(d) {
def doit(d):
#  d[1].forEach(function(r){if(r.length === 2)assert.equal(SSF.format(r[0],d[0]),r[1]);});
    for r in d[1]:
        if len(r) == 2:
            assert ssf.format(r[0], d[0]) == r[1]
#}
#describe('implied formats', function() {
def test_implied_formats():
#  data.forEach(function(d) {
    for d in data:
#    if(d.length == 2) it(String(d[0]), function() { doit(d); });
        if len(d) == 2:
            doit(d)
        elif len(d) == 3:
            assert ssf.format(d[1], d[0]) == d[2]
#    else it(d[1]+" for "+d[0], skip.indexOf(d[1]) > -1 ? null : function(){
#      assert.equal(SSF.format(d[1], d[0], {}), d[2]);
#    });
#  });
#});
