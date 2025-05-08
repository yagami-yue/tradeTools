class TimePoint:
    __slots__ = ["e", "i", "c", "m"]

    def __init__(self, e=None, i=None, c=None, m=None) -> None:
        self.e = e
        self.i = i
        self.c = c
        self.m = m
