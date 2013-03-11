class immutable(object):

    def __init__(self, attrname):
        self.attrname = attrname

    def __get__(self, instance, owner):
        return instance.__dict__[self.attrname]

    def __set__(self, instance, value):
        raise AttributeError, "Writing to immutable %s" % self.attrname

class Trouble(object):

    def compute(self):
        self.total = 5

Trouble.total = immutable('total')

t = Trouble()
try:
    t.compute()
except AttributeError:
   print "got it!"

del Trouble.total
t.compute()
print "missed it"
