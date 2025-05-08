from bisect import (
    bisect_left,
    bisect_right
)


def mtous(mt):
    # us
    us = mt % 1_000_000
    mt = (mt - us) // 1_000_000
    # s
    s = mt % 100
    mt = (mt - s) // 100
    # minutes
    m = mt % 100
    h = (mt - m) // 100
    return (h * 3600 + m * 60 + s) * 1_000_000 + us


def ustom(u):
    # us
    us = u % 1_000_000
    u = (u - us) // 1_000_000
    # s
    s = u % 60
    u = (u - s) // 60
    # minutes
    m = u % 60
    h = (u - m) // 60
    return (h * 10000 + m * 100 + s) * 1_000_000 + us


def mtime_delta(m1, m0):
    return mtous(m1) - mtous(m0)


def mtime_add(m0, delta):
    us0 = mtous(m0)
    us = us0 + delta
    return ustom(us)


def find(value, array, side=-1, include=True):
    """ 
    side == -1, include=True: max arrays <= value
    side == 1, include=True: min arrays >= value
    """
    if side == -1:
        idx = max(bisect_right(array, value) - 1, 0)
        return idx, array[idx]
    else:
        idx = min(bisect_left(array, value), len(array) - 1)
        return idx, array[idx]


# if __name__ == "__main__":
#     m = 13_01_23_233_455
#     print(ustom(mtous(m)))
#
#     us2 = 1_000_000 * 1
#     m2 = mtime_add(m, us2)
#     print(m2)
