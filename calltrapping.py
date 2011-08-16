import sys

def WatchCalls(attrlist, mod, watchfunc):

    class Watcher(object):

        def __init__(self, orig_func, catcher):
            self.orig_func = orig_func
            self.catcher = catcher

        def __call__(self, *args, **kw):
            return self.catcher(self.orig_func, *args, **kw)

    for attr in attrlist:
        orig_func = mod.__dict__[attr]
        #mod.__dict__[attr] = Watcher(orig_func, watchfunc)
        setattr(mod, attr, Watcher(orig_func, watchfunc))

def openwatcher(orig_func, name, mode):
    print "Opening file %r in mode %r" % (name, mode)
    return orig_func(name, mode)

import __builtin__
WatchCalls(['file', 'open'], __builtin__, openwatcher)  # from=['pyplay.py']

f = open('/tmp/junk', 'w')
f.close()

class Alpha(object):
    def hello(self):
        print "Hello"

def callwatcher(orig_func, *args, **kw):
    print "Function %r invoked with args=%r, kw=%r" % (orig_func, args, kw)
    return orig_func(*args, **kw)

WatchCalls(['hello', ], Alpha, callwatcher)  # from=['pyplay.py']

a = Alpha()
a.hello()
a.hello()
