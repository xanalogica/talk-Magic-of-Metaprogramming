import sys
import os
from types import ModuleType

#class ModuleWatcher(ModuleType):
#    pass

#import target_module

# hook pre-import and never let unwatched module get into system?

# can a metaclass insure a class gets a different kind of dict?
# can a class insure an instance gets a different kind of dict?

class Watcher(object):
    pass

# (1) make ModuleType.__dict__ writable so we can place descriptors in it to monitor attribute get/set?
# (2) make a specific module's __dict__ readonly in some way we can monitor access to it?

class Y(object):
    pass

class type_with_modifiable_dict(type, Y):
    pass

class MyClass(object):
    """This class has its __dict__ attribute indirectly exposed via the __dict__ getter/setter of Y."""
    __metaclass__ = type_with_modifiable_dict

from importer import MetaServices

class GlassDictOf(dict):

    ddict = {}

    def __repr__(self):
        return "GlassDictOf(%s, id=%r, type=%r)" % (self.obj.__name__, id(self.obj), type(self.obj))
    __str__ = __repr__

    def __init__(self, obj):
        dict.__init__(self)
        print "GlassDictOf.__init__ setting obj to %r, id %r, type %r" % (obj, id(obj), type(obj))
        self.obj = obj  #### an instance of GnuModule

    def __getitem__(self, key):
        print "GlassDictOf.__getitem__(%r)" % (key, )
        #d = self.obj.__getattribute__('__dict__', usedesc=False)
        d = self.ddict
        print "GlassDictOf.__getitem__ got usedesc=False __dict__ of %r, id %r, type %r" % (d, id(d), type(d))
        v = d[key]  #### POINT OF RECURSION ####
        print "GlassDictOf.__getitem__ fetching key %r returning value %r" % (key, v)
        return v

#        # How to bypass a descriptor
#        return self.__class__.__getitem__

#        return self.obj.mdict[key]
#        return self.obj.__dict__[key]
#        return self.obj.__getitem__(self, key)

    def __setitem__(self, key, item):
        print "(setting key %r to %r" % (key, item)
        #d = self.obj.__getattribute__('__dict__', usedesc=False)
        d = self.ddict
        print "GlassDictOf.__setitem__ got usedesc=False __dict__ of %r, id %r, type %r" % (d, id(d), type(d))
        d.__setitem__(key, item)
        print "(finished setting key %r to %r" % (key, item)

class NewDesc(object):

    def __init__(self, attrname):
        self.attrname = attrname
        self.first = True

    def __get__(self, obj, type=None):
        if self.first or hasattr(obj, 'nodesc'):
            print "DDDD __dict__ descriptor returning nodesc %r" % (obj, )
            self.first = False
            return obj.__dict__
        else:
            print "DDDD __dict__ descriptor returning GlassDictOf(%r)" % (obj, )
            return GlassDictOf(obj)

    def __set__(self, obj, value):
        raise NameError("Attribute %r of class %r is read-only." % (self.attrname, obj))

    def __delete__(self, obj):
        raise NameError("Attribute %r of class %r is read-only." % (self.attrname, obj))

class OldDesc(object):

    def __init__(self, attrname):
        self.attrname = attrname

    def __get__(self, obj, type=None):
        return obj.__dict__

    def __set__(self, obj, value):
        raise NameError("Attribute %r of class %r is read-only." % (self.attrname, obj))

    def __delete__(self, obj):
        raise NameError("Attribute %r of class %r is read-only." % (self.attrname, obj))

class GnuModule(ModuleType):
    __metaclass__ = type_with_modifiable_dict

    def __new__(cls, name):
        obj = ModuleType.__new__(cls)
        obj.mdict = obj.__dict__
        print "========> id of mdict is %r, type %r" % (id(obj.mdict), type(obj.mdict))
        return obj

    def __init__(self, name):
        ModuleType.__init__(self, name)
        #self.__dict__ = GlassDict()
        #self.mod_dict = self.__dict__
        print "GnuModule of name %r created, dict is %r." % (name, id(self.__dict__))

    __dict__ = NewDesc('__dict__')
    __odict__ = OldDesc('__dict__')

    def __getattribute__(self, name, usedesc=True):  # watch every fetch from the module's namespace
        print "__getattribute__ fetching %r of %r" % (name, self)
        if name == '__dict__' and usedesc is False:
            try:
                self.nodesc = True
                return self.mdict
            finally:
                del self.nodesc
#            return ModuleType.__getattribute__(self, name)
#            return GnuModule.__dict__.__get__(self, type(self))

        rc = object.__getattribute__(self, name)
#        rc = ModuleType.__getattribute__(self, name)
        print "__getattribute__ for %r returned id %r, type %r" % (name, id(rc), type(rc))
        return rc

    def hello(self):
        print "Hello from GnuModule"

if __name__ == '__main__':

    pgm = 'target_module'  # sys.argv[1]
    ms = MetaServices()

    def adjust(mod):
#        print "(adjusting imported module %r)" % (mod, )

        class GnuModule(ModuleType):
#            __metaclass__ = type_with_modifiable_dict
            def hello(self):
                print "Hello from GnuModule"

        m = GnuModule(mod.__name__)

        for name in dir(mod):
#            print "Copying attribute %r with value %r" % (name, getattr(mod, name))
            setattr(m, name, getattr(mod, name))

#        m.__dict__.update(mod.__dict__)
#        m.__dict__['jeff'] = 'rush'
        m.jeff = 'rush'

#        print "Keys in old %r: %r" % (type(mod), mod.__dict__.keys(), )
#        print "Keys in new %r: %r" % (type(m), m.__dict__.keys(), )

#        print "after swap, 'sys' is %r" % (m.sys, )
#        print "after swap, 'jeff' is %r" % (m.jeff, )
#        print "after swap, sys.modules['sys'] is %r" % (sys.modules['sys'], )

#        print "Replacing entry for %r with GnuModule %r" % (mod.__name__, m)
        sys.modules[mod.__name__] = m
        return m

#    ms.call_after_import_of('target_module', adjust)
    ms.subclass_module('target_module', GnuModule)

    m = ms.__import__(pgm)
#    print m, m.__dict__.keys()
#    print sys.modules['target_module']

    print "module globals are %r" % (m.__dict__.keys(), )

#    print "Globals for main() is %r" % (type(m.main.func_globals), )
    m.main(m)
