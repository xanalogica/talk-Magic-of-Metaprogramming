import sys
import ihooks
import inspect
import fnmatch

class MetaServices(ihooks.Hooks):

    def __init__(self):
        ihooks.Hooks.__init__(self)
        self.import_watchers = {}

        #m.open = m.file = self.r_open

        self.loader = ihooks.FancyModuleLoader(self)
        self.importer = ihooks.ModuleImporter(self.loader)

    def __import__(self, modname, globals={}, locals={}, fromlist=[]):

        m = self.importer.import_module(modname, globals, locals, fromlist)

        if modname in self.import_watchers: # call post-import handlers
            callfunc, filepatt = self.import_watchers[modname]

            frame = sys._getframe(1)
            importing_file = inspect.getsourcefile(frame) or inspect.getfile(frame)

            if filepatt is None or fnmatch.fnmatch(importing_file, filepatt):
                callfunc(m)

        return m

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
#    ms.call_after_import_of(pgm, adjust)
    ms.call_after_import_of('re', adjust, from_filepatt='*target_*')

    m = ms.__import__(pgm)
#    print m.jeff
    print dir(m)
    m.main()
