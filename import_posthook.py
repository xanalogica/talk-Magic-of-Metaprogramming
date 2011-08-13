import sys
import ihooks
import inspect
import fnmatch

class MetaServices(ihooks.Hooks):
    """Collection of useful metaprogramming hooks and methods."""

    def __init__(self):
        ihooks.Hooks.__init__(self)
        self.import_watchers = {}

        self.loader = ihooks.FancyModuleLoader(hooks=self)
        self.importer = ihooks.ModuleImporter(self.loader)

    def __import__(self, modname, globals={}, locals={}, fromlist=[]):

        m = self.importer.import_module(modname, globals, locals, fromlist)

        if modname in self.import_watchers: # call post-import handlers
            callfunc, filepatt = self.import_watchers[modname]

            frame = sys._getframe(1)
            importing_file = inspect.getsourcefile(frame) or inspect.getfile(frame)

            if filepatt is None or fnmatch.fnmatch(importing_file, filepatt):
                m = callfunc(m) or m

        return m

    def call_after_import_of(self, modname, callfunc, from_filepatt=None):

        if sys.modules['__builtin__'].__import__ != self.__import__:
            sys.modules['__builtin__'].__import__ = self.__import__

        self.import_watchers[modname] = (callfunc, from_filepatt)

if __name__ == "__main__":

    ms = MetaServices()

    def adjust(mod):
        from perftest import RequestTracker
        mod.Request = RequestTracker

    ms.call_after_import_of('re', adjust, from_filepatt='*target_import_post*')

    from target_import_posthook import main
    main()
