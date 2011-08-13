import sys
import ihooks
import inspect
import fnmatch

from types import ModuleType

class MetaServices(ihooks.Hooks):

    def __init__(self):
        ihooks.Hooks.__init__(self)
        self.import_watchers = {}
        self.import_subclasses = {}

        self.loader = ihooks.FancyModuleLoader(hooks=self)
        self.importer = ihooks.ModuleImporter(self.loader)

    def __import__(self, modname, globals={}, locals={}, fromlist=[]):

        if modname in self.import_subclasses:
            mod_cls = self.import_subclasses[modname]

            class SubclassingHooks(ihooks.Hooks):
                def new_module(self, name):
                    return mod_cls(name)   # instead of imp.new_module(name)
            loader = ihooks.FancyModuleLoader(hooks=SubclassingHooks())
            importer = ihooks.ModuleImporter(loader)
        else:
            importer = self.importer

        m = importer.import_module(modname, globals, locals, fromlist)
        print "Import module %r of type %r" % (modname, type(m))

        if modname in self.import_watchers: # call post-import handlers
            callfunc, filepatt = self.import_watchers[modname]

            frame = sys._getframe(1)
            importing_file = inspect.getsourcefile(frame) or inspect.getfile(frame)

            if filepatt is None or fnmatch.fnmatch(importing_file, filepatt):
                m = callfunc(m) or m

        return m

    def subclass_module(self, modname, cls):
        self.import_subclasses[modname] = cls

    def call_after_import_of(self, modname, callfunc, from_filepatt=None):

        if sys.modules['__builtin__'].__import__ != self.__import__:
            sys.modules['__builtin__'].__import__ = self.__import__

        self.import_watchers[modname] = (callfunc, from_filepatt)

if __name__ == "__main__":

    pgm = 'target_import'  # sys.argv[1]

    ms = MetaServices()

    def adjust(mod):
        print "(adjusting imported module %r)" % (mod, )
        mod.jeff = 'rush'

    ms.call_after_import_of('target_import_prehook', adjust, from_filepatt='*target_*')

    class ModuleWatcher(ModuleType):
        def __init__(self, modname):
            self.modname = modname
        def __getattribute__(self, name):
            modname = ModuleType.__getattribute__(self, 'modname')
            print ".......... fetching attr %r of module %r" % (name, modname)
            return ModuleType.__getattribute__(self, name)

    ms.subclass_module('target_import_prehook', ModuleWatcher)

    from target_import_prehook import main
    main()
