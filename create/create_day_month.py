from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import re

with open('../ssf/lcid.tsv', 'r', encoding='utf-8') as v:
    lines = v.read().splitlines()

with open('../ssf/numbers.tsv', 'r', encoding='utf-8') as n:
    numbers = n.read().splitlines()

number_names = [ '', 'en', 'hi', 'Hi', 'sa', 'bn', 'guru', 'gu', 'or', 'ta', 'te', 'kn', 'ml',
        'th', 'lo', 'bo', 'my', 'am', 'km', 'mn', 'ja', 'jpn', 'ja3', 'zhl', 'zh', 'zhn', 'zhtl',
        'zhtu', 'zhtn', 'ko', 'ko2', 'ko3', 'ko4' ]

CHUNKSIZE=200       # Excel only has room for a small number of custom formats

dates = [43836, 43865, 43894, 43923, 43952, 43988, 44017, 44046, 44082, 44111, 44140, 44169]
desc = ['Mon Jan', 'Tue Feb', 'Wed Mar', 'Thu Apr', 'Fri May', 'Sat Jun', 'Sun Jul', 'Mon Aug', 'Tue Sep', 'Wed Oct', 'Thu Nov', 'Fri Dec']

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def find(elem, lst):
    try:
        return lst.index(elem)
    except Exception:
        pass
    return -1

for c, chunk in enumerate(divide_chunks(lines[1:], CHUNKSIZE), start=1):
    wb = Workbook()
    ws = wb.active
    ws.cell(1, 1).value = 'LCID'
    ws.cell(1, 2).value = 'Locale'
    for col, d in enumerate(desc, start=3):
        ws.cell(1, col).value = d
        ws.column_dimensions[get_column_letter(col)].width = 32
    for row, line in enumerate(chunk, start=2):
        ls = line.split('\t')
        num = int(ls[0], 16)
        lang = ls[1].split('-')[0]
        ndx = find(lang, number_names)
        if ndx > 1:                 # Some of the output is numbers, so localize those too
            num |= ndx << 24
        fmt = f'[$-{num:X}]dddd,ddd,mmmm,mmm,mmmmm'
        ws.cell(row, 1).value = f'0x{num:X}'
        ws.cell(row, 2).value = ls[1]
        for col, d in enumerate(dates, start=3):
            ws.cell(row, col).value = d
            ws.cell(row, col).number_format = fmt
    wb.save(filename=f'daymonth{c}.xlsx')
