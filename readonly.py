import sys

class readonly(object):

    def __init__(self, attrname):
        self.attrname = attrname

    def __get__(self, obj, type=None):
        return obj.__dict__[self.attrname] # fetch from instance dict

    def __set__(self, obj, value):
        raise NameError("Attribute %r of class %r is read-only." % (self.attrname, obj))

    def __delete__(self, obj):
        raise NameError("Attribute %r of class %r is read-only." % (self.attrname, obj))

if __name__ == "__main__":

    pgm = sys.argv[1]

    m = __import__(pgm, globals(), locals())

    m.Alpha.name = readonly('secret')     # affects existing instances!

    m.main()
