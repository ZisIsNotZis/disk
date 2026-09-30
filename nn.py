def Scale(N=1):
    m = v = n = 0
    def Scale(_, inv=0):
        nonlocal m,v,n
        if inv:
            return _*(v/n)**.5+m/n
        if n<N:
            m += _.data.mean()
            v += _.data.var()
            n += 1
        return (_-m/n)/(v/n)**.5
    return Scale
