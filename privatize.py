import sys

class private(object):

    def __init__(self, attrname):
        self.attrname = attrname

    def _ck_owner(self, obj):
        caller_locals = sys._getframe(2).f_locals # frame of accessing function/method
        if 'self' in caller_locals and caller_locals['self'] == obj:
            return
        raise NameError("Attribute %r of class %r is private." % (self.attrname, obj))

    def __get__(self, obj, type=None):
        self._ck_owner(obj)
        return obj.__dict__[self.attrname] # fetch from instance dict

    def __set__(self, obj, value):
        self._ck_owner(obj)
        obj.__dict__[self.attrname] = value  # store into instance dict


if __name__ == "__main__":

    pgm = sys.argv[1]

    m = __import__(pgm, globals(), locals())

    m.Alpha.secret = private('secret')     # affects existing instances!

    m.main()
