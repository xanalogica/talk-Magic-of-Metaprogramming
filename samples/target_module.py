import sys
import string

print "sys is %r" % (sys, )

def main(m):
    print "My name is %r" % (__name__, )
    print type(sys.modules[__name__])
    assert m is sys.modules[__name__]

#    print dir(m)
#    print dir(globals())
#    print globals()['__class__']

#    print "sys is now %r" % (m.sys, )
#    print m.string
#    print m.sys.modules[m.__name__]
#    print type(sys.modules[m.__name__])

    print type(main.func_globals)
    print main.func_globals.keys()
    print id(main.func_globals)

    assert main.func_globals is globals()  # True
#    print globals()

    print '__class__' in globals()

    print hello
