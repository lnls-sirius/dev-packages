
def flatten(l):
    try:
        l[0]
        r = []
        for e in l:
            r.extend(flatten(e))
        return r
    except:
        return [l]
