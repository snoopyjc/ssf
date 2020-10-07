from ssf import SSF
pre = '<font color="{}"><span style="color:#{rgb}>'
post = '</span></font>'
ssf = SSF(color_pre=pre, color_post=post)

def test_colors():
    data = [26, -26, 0, 'a']
    colors_expected = {"[GREEN]#,###": [f'{pre.format("Green", rgb="00FF00")}26{post}',
                                        f'{pre.format("Green", rgb="00FF00")}-26{post}',
                                        f'{pre.format("Green", rgb="00FF00")}{post}',
                                        'a'],
                        "[Green]#,###": [f'{pre.format("Green", rgb="00FF00")}26{post}',
                                        f'{pre.format("Green", rgb="00FF00")}-26{post}',
                                        f'{pre.format("Green", rgb="00FF00")}{post}',
                                        'a'],
                        "[MAGENTA]0.00": [f'{pre.format("Magenta", rgb="FF00FF")}26.00{post}',
                                        f'{pre.format("Magenta", rgb="FF00FF")}-26.00{post}',
                                        f'{pre.format("Magenta", rgb="FF00FF")}0.00{post}',
                                        'a'],
                        "[Magenta]0.00": [f'{pre.format("Magenta", rgb="FF00FF")}26.00{post}',
                                        f'{pre.format("Magenta", rgb="FF00FF")}-26.00{post}',
                                        f'{pre.format("Magenta", rgb="FF00FF")}0.00{post}',
                                        'a'],
                        "[RED]#.##": [f'{pre.format("Red", rgb="FF0000")}26.{post}',
                                        f'{pre.format("Red", rgb="FF0000")}-26.{post}',
                                        f'{pre.format("Red", rgb="FF0000")}.{post}',
                                        'a'],
                        "[Red]#.##": [f'{pre.format("Red", rgb="FF0000")}26.{post}',
                                        f'{pre.format("Red", rgb="FF0000")}-26.{post}',
                                        f'{pre.format("Red", rgb="FF0000")}.{post}',
                                        'a'],
                        r"[Red][<-25]General;[Blue][>25]General;[Green]General;[Yellow]General\ ": \
                                      [f'{pre.format("Blue", rgb="0000FF")}26{post}',
                                        f'{pre.format("Red", rgb="FF0000")}26{post}',
                                        f'{pre.format("Green", rgb="00FF00")}0{post}',
                                        f'{pre.format("Yellow", rgb="FFFF00")}a {post}',
                                        ],
                        "[Red][=26]General;[Blue]000": [f'{pre.format("Red", rgb="FF0000")}26{post}',
                                        f'{pre.format("Blue", rgb="0000FF")}-026{post}', 
                                        f'{pre.format("Blue", rgb="0000FF")}000{post}', 
                                        'a' ],
                        "[WHITE]0.0": [f'{pre.format("White", rgb="FFFFFF")}26.0{post}',
                                        f'{pre.format("White", rgb="FFFFFF")}-26.0{post}',
                                        f'{pre.format("White", rgb="FFFFFF")}0.0{post}', 
                                        'a'],
                        "[White]0.0": [f'{pre.format("White", rgb="FFFFFF")}26.0{post}',
                                        f'{pre.format("White", rgb="FFFFFF")}-26.0{post}',
                                        f'{pre.format("White", rgb="FFFFFF")}0.0{post}', 
                                        'a'],
                        "[YELLOW]@": ['26', '-26', '0',         # [Color]@ only applies to text
                                        f'{pre.format("Yellow", rgb="FFFF00")}a{post}' ],
                        "[Yellow]@": ['26', '-26', '0', 
                                        f'{pre.format("Yellow", rgb="FFFF00")}a{post}'],
                        "[Color6]@": ['26', '-26', '0', 
                                        f'{pre.format("Color6", rgb="FFFF00")}a{post}'],
                        "[Color 9]@": ['26', '-26', '0', 
                                        f'{pre.format("Color9", rgb="800000")}a{post}'],
                        "[Color14]@": ['26', '-26', '0', 
                                        f'{pre.format("Color14", rgb="008080")}a{post}'],
                        "[Color  21]@": ['26', '-26', '0', 
                                        f'{pre.format("Color21", rgb="660066")}a{post}'],
                        }
    for fmt, expected_values in colors_expected.items():
        for i, d in enumerate(data):
            if i >= len(expected_values):
                continue
            expected = expected_values[i]
            actual = ssf.format(fmt, d)
            assert actual == expected


