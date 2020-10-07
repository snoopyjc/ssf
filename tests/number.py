def Number(s):
    """Support for ssf testing: the Number function from JavaScript"""
    f = float(s)
    if int(f) == f:
        return int(f)
    return f
