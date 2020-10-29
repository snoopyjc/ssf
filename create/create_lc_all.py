import locale

with open('../ssf/lcid.tsv', 'r', encoding='utf-8') as v:
    lines = v.read().splitlines()

locale.setlocale(locale.LC_ALL, 'en-US')
conv = locale.localeconv()
keys = list(conv.keys())
heading = "lcid\tlocale\t" + "\t".join(keys)

with open('lc_all.tsv', 'w', encoding='utf-8') as mf:
    print(heading, file=mf)
    for line in lines[1:]:
        ls = line.split('\t')
        num = ls[0]
        lcl = ls[1]
        try:
            locale.setlocale(locale.LC_ALL, lcl)
        except locale.Error:
            print(f"Can't set locale to {lcl}: skipping")
            continue
        row = []
        row.append(num)
        row.append(lcl)
        conv = locale.localeconv()
        for key in keys:
            row.append(str(conv[key]))
        print("\t".join(row), file=mf)

