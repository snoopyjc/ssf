#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#/*eslint-env mocha, node */
#var SSF = require('../');

from ssf import SSF
ssf = SSF()

#var assert = require('assert');

#/* {format, data:[[value, result]]} */
#var data = [
data = [
    {
        'format': '"$"#,##0_);\\("$"#,##0\\);"-"',
        'data': [
            [10000,    "$10,000 "],
            [9000.98,   "$9,001 "],
            [100,         "$100 "],
            [50.02,        "$50 "],
            [1,             "$1 "],
            [0.1,           "$0 "],
            [0.01,          "$0 "],
            [0,               "-"],
            [-10000,  "($10,000)"],
            [-9000.98, "($9,001)"],
            [-100,       "($100)"],
            [-50.02,      "($50)"],
            [-1,           "($1)"],
            [-0.1,         "($0)"],
            [-0.01,        "($0)"]
        ]
    },
    {
        'format': '(#,##0.00)',
        'data': [
            [-12345.6789, "-(12,345.68)"]
        ]
    },
    {
        'format': '#,##0.00;\\(#,##0.00\\)',
        'data': [
            [-12345.6789, "(12,345.68)"]
        ]
    },
    {
        'format': '[<=9999999]###\\-####;(###) ###\\-####',
        'data': [
            [2813308004, '(281) 330-8004']
        ]
    }
#];
]

def test_negative():
#describe("negatives", function() {
#    data.forEach(function(row) {
    for row in data:
#        it(row.format, function() {
#            row.data.forEach(function(r) {
        for r in row['data']:
#                assert.equal(SSF.format(row.format, r[0]), r[1]);
            assert ssf.format(row['format'], r[0]) == r[1]
#            });
#        });
#    });
#});
