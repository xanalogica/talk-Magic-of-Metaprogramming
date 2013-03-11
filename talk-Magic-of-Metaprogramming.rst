.. include:: <s5defs.txt>

==============================
 The Magic of Metaprogramming
==============================

.. class:: sidebox boxed incremental

   .. image:: graphics/coordinator-of-pgms.jpg
      :scale: 150 %

:Author: Jeff Rush <jeff\@taupro.com>
:Copyright: 2011 Tau Productions Inc.
:License: Creative Commons Attribution-ShareAlike 3.0
:Duration: 45-minutes
:Difficulty: Advanced
:Keywords: metaprogramming, data structures, language, techniques

Learn the magic of writing Python code that monitors, alters and reacts to
module imports, changes to variables, calls to functions and invocations of
the builtins.  Learn out to slide a class underneath a module to intercept
reads/writes, place automatic type checking over your object attributes and
use stack peeking to make selected attributes private to their owning class.
We'll cover import hacking, metaclasses, descriptors and decorators and how
they work internally.

\https://github.com/xanalogica/talk-Magic-of-Metaprogramming.git

.. |bullet| unicode:: U+02022
.. footer:: Tau Productions Inc. |bullet| 2013

.. role:: altway
   :class: altway

What is Metaprogramming?
========================

.. container:: slide-display

   .. class:: incremental

      `the writing of programming code that`
      `writes, analyzes or adjusts other code,`
      `using that other code's structure`
      `as its data.`

      ..

      + two general forms: manipulation from

        .. class:: incremental

           + inside

             + stays in production
             + reduces developer workload

           + outside

             + for debugging, testing

Tools At Our Disposal
=====================

.. container:: slide-display

   .. class:: incremental

      + makes use of

        .. class:: incremental

           + metaclasses
           + decorators (class and function)
           + attribute lookups special functions
           + descriptors (and properties)

      ..

      + I cover only Python 2.x, new-style classes.

Orientation Diagram: What is Metaprogramming
============================================

.. container:: slide-display center animation

   .. class:: incremental

      .. container:: handout

         graphics/what-is-metaprogramming.svg  (source material)

         seq-mp-code-data-X   (walk 'Code' and 'Data' blocks onto screen-center)
         seq-mp-datacomp-X    (add dnarrow and 'Data Computation' box from left)
         seq-mp-uievents-X    (add uparrow and 'UI Events' box from right)
         seq-mp-convpgm-X     (slide shade over system and add label along bottom)
         seq-mp-metacode-X    (slide entire arrangement down, and walk 'Metacode' box onto screen-center)
         seq-mp-plumbing-X    (add dnarrow and 'Plumbing Adjustments' box from left)
         seq-mp-addattrs-X    (walk out "add/adjust attributes")
         seq-mp-register-X    (walk out "register elements")
         seq-mp-tagstuff-X    (walk out "tag elements")
         seq-mp-codeevents-X  (add uparrow and "Code Events")
         seq-mp-modimport-X   (walk out "import of a module")
         seq-mp-classdef-X    (walk out "definition of a class/function")
         seq-mp-dotted-rdwr-X (walk out "write to a dotted name")
         seq-mp-callnret-X    (walk out "call and return")
         seq-mp-metapgm-X     (slide shade over upper system and add label along top)

      .. image:: graphics/mp-code-data.gif
      .. image:: graphics/mp-datacomp.gif
      .. image:: graphics/mp-uievents.gif
      .. image:: graphics/mp-convpgm.gif
      .. image:: graphics/mp-metacode.gif
      .. image:: graphics/mp-plumbing.gif
      .. image:: graphics/mp-addattrs.gif
      .. image:: graphics/mp-register.gif
      .. image:: graphics/mp-tagstuff.gif
      .. image:: graphics/mp-codeevents.gif
      .. image:: graphics/mp-modimport.gif
      .. image:: graphics/mp-classdef.gif
      .. image:: graphics/mp-dotted-rdwr.gif
      .. image:: graphics/mp-callnret.gif
      .. image:: graphics/mp-metapgm.gif

   .. class:: handout

      + Diagram - data <-> code <-> metacode, app-events versus code-events

      + Runtime Events

        + class initialization
        + function definition
        + module import
        + modification of a dotted name
        + retrieval of a dotted name
        + calling something

        ..

        + can be specific to a particular module or class

        + execution events

          1) initialization of a class definition

             - read class attrs and act on them
             - add/adjust methods
               - descriptors to control access to instance attrs
               - wrappers to hear about calls to both instance and class methods

                 - add a new instance to a registry

             - add the new class to a registry

Sample Problem #1: Subclassing an Embedded Class
================================================

.. container:: slide-display

   .. class:: sidebox boxed incremental

      | class Request(object):
      |     ...
      | class HTTPServer(object):
      |     def handle_request(self, ...):
      |         req = Request(...)
      |     ...

   .. class:: incremental

      + Objective

        + subclass a class deep inside a module

      ..

      + Challenges: They didn't

        .. class:: incremental

           + use a public factory
           + import from elsewhere
           + take the class as a parameter

      ..

      + A Metaprogramming Solution:

        .. class:: incremental

           + catch a specific import, so we can
           + redefine "Request" to be a subclass

A Solution to #1: Post-Import Hooking
=====================================

.. container:: slide-display

   *After import, rearrange content of module before others use it.*

   .. class:: incremental

      | old__import__ = sys.modules['__builtin__']
      | sys.modules['__builtin__'].__import__ = self.__import__

      | def __import__(modname):
      |
      |     m = old__import__(modname)
      |
      |     if modname == 'webserver':  # every time
      |         `frame = sys._getframe(1)`
      |         `importing_file = inspect.getsourcefile(frame) or inspect.getfile(frame)`
      |         `if fnmatch.fnmatch(importing_file, "*startup*"):  # only at startup`
      |             rearrange(m)
      |     return m

A Solution to #1 (Packaged Up)
==============================

.. container:: slide-display

   *After import, rearrange content of module before others use it.*

   .. class:: sidebox boxed

      | class Request(object):
      |     ...
      | class HTTPServer(object):
      |     def handle_request(self, ...):
      |         req = Request(...)
      |     ...

   .. class:: incremental

      | from tau.metaservices import MetaServices

      | def adjust(mod):
      |     from replacements import Request
      |     mod.Request = Request
      |

      | ms = MetaServices()
      | ms.call_after_import_of(
      |     'webserver', adjust `, from_filepatt='*startup*'`)

      | from webapp import main
      | main()

Alternate Solution: Pre-Import Hooking
======================================

.. container:: slide-display

   *Just before import, slip in a subclassed module object.*

   .. class:: incremental

      | def __import__(modname):
      |
      |     if modname == 'webserver':
      |
      |         `class SubclassingHooks(ihooks.Hooks):`
      |             `def new_module(self, modname):`
      |                 `return YourModuleFixer(modname)   # <--- your class`
      |
      |         `loader = ihooks.FancyModuleLoader(hooks=SubclassingHooks())`
      |         importer = ihooks.ModuleImporter(loader)
      |     else:
      |         importer = old__import__
      |
      |     return importer(modname)

What Does a Subclassed Module Look Like?
========================================

.. container:: slide-display

   .. class:: incremental

      | from types import ModuleType
      | class ModuleWatcher(ModuleType):
      |
      |     def __init__(self, modname):
      |         Moduletype.__init__(self, modname)
      |
      |     def __getattribute__(self, attrname):
      |
      |         `modname = ModuleType.__getattribute__(self, '__name__')  # self.__name__`
      |         `print "__getattribute__ fetching %r of %r" % (attrname, self)`
      |
      |         `if modname == 'webserver' and attrname == 'Request':`
      |             `from replacements import Request`
      |             `return Request`
      |
      |         return ModuleType.__getattribute__(self, attrname)

Some Benefits of Subclassing Modules
====================================

.. container:: slide-display

   .. class:: incremental

      + intercept attribute reads/writes
      + prevent/log writes
      + log timestamps and caller locations
      + return different values to different callers

      ..

      + tip: you can put non-module stuff on sys.path

      >>> import sys
      >>> sys.modules['TheAnswer'] = 42
      >>> import TheAnswer
      >>> TheAnswer
      42

Moving from Import Hooking to Metaclasses
=========================================

.. container:: slide-display center

   .. image:: graphics/after-imports-breathing.jpg
      :width: 800

   + (pause - take a deep breath...)

Orientation Diagram: Instances, Classes and Metaclasses
=======================================================

.. container:: slide-display center animation

   .. class:: incremental

      .. container:: handout

         graphics/history-of-objects.svg  (source material)

         * make numbers in instances different

         seq-hc-justbits-X
            title 'a fable (literary licence) of objects'
            in the beginning there was just 1's and 0's
            (show a heap of them)

         seq-hc-funcs-vars-X
            they separated into code (functions) and data (variables);
            a function could reach out and change any variable and
            each variable had to have a unique name.  It was unclear
            which vars went with which functions.

         seq-hc-vargroups-X
            Vars got grouped together, int C structs or Pascal
            records.  But functions were still separate.

         seq-hc-groupings-X
            Functions became got added into the var groupings.

         seq-hc-group-ctor-X
            There was a 'constructor' function that created each var
            grouping, according to what was needed each time.

          seq-hc-protos-X
            Then instead of rebuilding, a var group was used as a
            'prototype object' to stamp out copies of itself.  The
            copier was the constructor of copies, named __call__.

         seq-hc-groupsplit-X
            Lots of duplicated code, excess copying of things that are
            common.  Decided to make two var groups, one for the
            shared stuff and one constructed for each instance.  The
            shared stuff represented a 'class of similar objects',
            shortened to 'class'.  No inheritance yet.

         seq-hc-groups-grow-X
            But the stuff shared among instances grew in size, and
            there was common code btw classes,

         seq-hc-delegating-X
            so inheritance was born; factoring vertically.

         seq-hc-new-axis-X
            One-dimension of creation just got a second dimension of
            delegation/inheritance.

         seq-hc-multi-inherit-X
            Assembly of classes was still complex, wanted more
            freedom to mix-and-match.  Multiple inheritance was born.

         seq-hc-metaclass-X
            All these classes had code to create them, buried in the
            interpreter.  The code got exposed into a class-like
            object called metaclasses.

         seq-hc-meta-as-ctor-X
            Since classes are objects, their constructor, named
            __call__ resides in the metaclass.  One metaclass created
            all classes, since they were all alike in behavior.  Just
            containers of methods mostly.

         seq-hc-submetas-X
            But then the metaclass is subclassable, making it possible
            to create new kinds of classes.

      .. image:: graphics/hc-welcome.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-justbits.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-funcs-vars.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-vargroups.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-vargroups2.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-groupings.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-group-ctor.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-protos.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-protos2.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-protos3.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-protos4.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-protos5.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-groupsplit.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-groupsplit2.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-groupsplit3.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-groups-grow.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-delegating.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-new-axis.gif
         :scale: 100 %
         :align: center

      .. image:: graphics/hc-multi-inherit.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-metaclass.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-meta-as-ctor.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/hc-submetas.gif
         :scale: 100 %
         :align: center

Facts About Metaclasses
=======================

.. container:: slide-display

   .. class:: incremental

      + a metaclass implements a "kind of class"
      + almost always you only need one kind
      + defining your own metaclass creates a "new kind"
      + smarter classes, more than "containers of methods"

      ..

      + new kinds are useful for

        .. class:: incremental

           + wrapping complexity for other programmers to use
           + i.e. a domain-specific language
           + generate classes/methods dynamically e.g. XML DTDs:

      ..

      + metaclasses do not (directly) affect instance's:

        .. class:: incremental

           + namespace lookup
           + method-resolution order
           + descriptor retrieval

Example #2: Define a Class from an SQL Table Definition
=======================================================

.. container:: slide-display

   .. class:: incremental

      | class Member(object):
      |     __metaclass__ = DatabaseTable
      |
      |     `dbtable = 'Members'  # an input to the metaclass`

      | class DatabaseTable(type):
      |
      |     `def __init__(cls, name, bases, class_dict):`
      |         `#from dbsetup import dbconn`
      |         `col_defs = dbconn.query_cols(table=class_dict['dbtable'])`
      |         `for col_def in col_defs:`
      |             `dbcolumn = wrap_col_rdwr(col_def) # (next slide)`
      |             `setattr(cls, col_def.name, dbcolumn)`

      + "process human-friendly decls into machine-friendly code"

Example Problem #2 (cont'd)
===========================

.. container:: slide-display

   .. class:: incremental

      | def wrap_col_rdwr(col_def):
      |
      |     `def get_dbcol_value(self):`
      |         `return self.__dict__.get(col_def.name, None)`
      |
      |     `def set_dbcol_value(self, value):`
      |         `value = col_def.validate(value)`
      |         `self.__dict__[col_def.name] = value`
      |
      |     return property(get_dbcol_value, set_dbcol_value)

      + tag attrs with type/value constraints
      + check class for conformance to your requirements

        .. class:: incremental

           + must have docstring
           + spelling of method names
           + max inheritance depth
           + insure abstract methods of superclass are defined

Metaclasses versus Class Decorators
===================================

.. container:: slide-display

   .. class:: incremental

      + metaclasses?  class decorators?

        .. class:: incremental

           + the latter are much simpler
           + the latter can do almost everything the former can
           + only a metaclass can add methods to the class itself

           ..

           + class-level services (methods):

             .. class:: incremental

                + @classmethods provide them -to- instances
                + metaclass methods provide them to the class itself

      + ONLY a metaclass can add to class attrs not visible to *self*:

        1. meta-methods
        2. meta-properties

      + class decorators can be (more easily) stacked
      + class decorators are NOT inherited (metaclasses are)

About Meta-Inheritance
======================

.. container:: slide-display center animation

   .. class:: incremental

      .. container:: handout

         graphics/meta-inheritance.svg  (source material)

         |                                    |      class TagClass(type):
         | def TagClass(cls):                 |          def __init__(cls, name, bases, class_dict):
         |     cls.__special__ = True         |              cls.__special__ = True
         |     return cls

         | @TagClass
         | class Alpha(object):               |      class Alpha(object):
         |     pass                           |          __metaclass__ = TagClass

         | '__special__' in Alpha.__dict__    |      '__special__' in Alpha.__dict__
         | >>> True                           |      >>> True

         | class Beta(Alpha):                 |      class Beta(Alpha):
         |     pass                           |          pass

         | '__special__' in Beta.__dict__     |       '__special__' in Beta.__dict__
         | >>> False                          |        >>> False

      .. image:: graphics/mcd-defns.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/mcd-use1.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/mcd-use1-test.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/mcd-use2.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/mcd-use2-test.gif
         :scale: 100 %
         :align: center

Example #3: Log the Arguments/Return Value of Method Calls
==========================================================

.. container:: slide-display

   .. class:: incremental

      |  @tracecalls  # use of a class decorator
      |  class Paragraph(object):
      |
      |      def lead_in(self, count, char='*'):
      |          return char * count

      |  >>> x = Paragraph()
      |  >>> x.lead_in(4)
      |  Called <bound method Paragraph.lead_in of <\__main__.Paragraph object at> 0xb7162c4c>> args=(4,), kw={} got '\*\*\*\*'
      |  '\*\*\*\*'

Example #3 (cont'd)
===================

.. container:: slide-display center animation

   .. class:: incremental

      .. container:: handout

         graphics/call-interceptor.svg  (source material)

         | def CaptureCalls(orig_cls):
         |
         |     def my__getattribute__(self, name):
         |         attr = super(orig_cls, self).__getattribute__(name)
         |         return attr if not callable(attr) else CallWrapper(attr)
         |
         |     orig_cls.__getattribute__ = my__getattribute__
         |     return orig_cls

         | def CallWrapper(func):  # as a closure
         |
         |     def whencalled(\*args, \*\*kw):
         |         rc = func(\*args, \*\*kw)
         |         print "Called %s args=%r, kw=%r got %r" % (func, args, kw, rc)
         |         return rc
         |
         |    return whencalled

         | class CallWrapper(object):  # as a class
         |
         |     def __init__(self, func):
         |         self.func = func
         |
         |     def __call__(self, \*args, \*\*kw):
         |         rc = self.func(\*args, \*\*kw)
         |         print "Called %s args=%r, kw=%r got %r" % (self.func, args, kw, rc)
         |         return rc

      .. image:: graphics/tr-bare.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/tr-getattr.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/tr-super.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/tr-callable.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/tr-wrapper.gif
         :scale: 100 %
         :align: center
      .. image:: graphics/tr-cls-wrapper.gif
         :scale: 100 %
         :align: center

Moving from Metaclasses into Descriptors
========================================

.. container:: slide-display center

   .. image:: graphics/after-metaclasses-breathing.jpg
      :width: 800

   + (pause - take a deep breath...)

Python's Mechanism of Attribute Lookup
======================================

.. container:: slide-display

   .. class:: incremental

      | def __getattribute__(self, name):  # symbolic, not actual
      |
      |     `inst_v = self.__dict__.get(name, Missing)`
      |     `if inst_v is not Missing:`
      |         `return inst_v                               # return the instance attr value`
      |
      |     `cls_v = lookthrough__dict__s(self.__class__, name, Missing)`
      |     `if cls_v is not Missing:`
      |         `return cls_v                                # return the class attr value`
      |
      |     `meth = lookthrough__dict__s(self.__class__, '__getattr__', Missing)`
      |     `if meth is not Missing:`
      |         `return meth(name)`
      |
      |     raise AttributeError

When to Use Which Lookup Mechanism
==================================

.. container:: slide-display

   + if you want to see

   .. class:: incremental

      + every attribute lookup, override **__getattribute__**
      + many attribute lookups, add your own **__getattr__**

        .. class:: incremental

           + doesn't see all because only called as a last resort
           + therefore perfect for delegation

      + one attribute lookup, add a **descriptor**

      ..

      + __setattr__(self, name, value)

        + to override storing value into self.__dict__

      + __delattr__(self, name)

Example 4: Overriding __getattr__
=================================

.. container:: slide-display

   .. class:: incremental

      + a wrapper around a bitmap element with a width and height
      + internally measured in pixels, but externally as inches

      | class Page(Bitmap):
      |
      |     `def __getattr__(self, name):`
      |         `if name == 'width':  return self.__dict__['_width'] / 600 #dpi`
      |         `if name == 'height': return self.__dict__['_height'] / 600 #dpi`
      |         `raise AttributeError, name`
      |
      |     `def __setattr__(self, name, value):`
      |         `if name == 'width':  self.__dict__['_width'] = value * 600 #dpi`
      |         `if name == 'height': self.__dict__['_height'] = value * 600) #dpi`
      |
      |     def __repr__(self):
      |         return "Page(%d x %d inches" % (self.width, self.height)

Example 4: Using a Descriptor Instead
=====================================

.. container:: slide-display

   .. class:: incremental

      | class Page(Bitmap):
      |
      |     `width = DimensionInches('width')   # a descriptor`
      |     `height = DimensionInches('height') # a descriptor`
      |
      |     def __repr__(self):
      |         return "Page(%d x %d inches)" % (self.width, self.height)

      | class DimensionInches(object):  # instance used in two places
      |     def __init__(self, attrname):
      |         self.attrname = attrname
      |     `def __get__(self, instance, owner):   # gives 'binding behavior'`
      |         `return instance.__dict__[self.attrname] / 600 #dpi`
      |     `def __set__(self, instance, value):`
      |         `instance.__dict__[self.attrname] = value * 600 #dpi`
      |     `def __delete__(self, instance):`
      |         `del instance.__dict__[self.attrname]`

Python's Mechanism of Attribute Lookup (descriptors)
====================================================

.. container:: slide-display

   .. class:: incremental

      | def __getattribute__(self, name):  # how Python does it (rearranged)
      |     cls_v = lookthrough__dict__s(self.__class__, name, Missing)
      |
      |     `if hasattr(cls_v, '__get__') and hasattr(cls_v, '__set__'):`
      |        `return cls_v.__get__(self, self.__class__)   # invoke data descriptor`
      |
      |     inst_v = self.__dict__.get(name, Missing)
      |     if inst_v is not Missing:
      |         return inst_v                               # return the instance attr value
      |
      |     `if hasattr(cls_v, '__get__'):`
      |         `return cls_v.__get__(self, self.__class__)  # invoke non-data descriptor`
      |
      |     if cls_v is not Missing: return cls_v            # return the class attr value
      |     if hasattr(cls, '__getattr__'): return cls.__getattr__(name)
      |     raise AttributeError

So What is a descriptor again?
==============================

.. container:: slide-display

   .. class:: incremental

      + an object you place into the class attributes
      + a plug-in to the lookup mechanism
      + is shared by all instances, passed the 'instance' at each use

      ..

      + recognized by having a __get__ method, **not by its class**
      + does not know its name (hence reusable)
      + there is one per attribute to be overridden

      ..

      + may store its value in:

        .. class:: incremental

           + the instance __dict__ (perhaps a different name)
           + some other place
           + or just compute it as needed

Where are descriptors used?
===========================

.. container:: slide-display

   .. class:: incremental

      + Python argument currying (non-data descriptors; __get__ only)

         + method objects:  `self.display(a, b)   ==>  cls.display(self, a, b)`
         + classmethods:    `self.display(a, b)   ==>  cls.display(cls, a, b)`
         + staticmethods:   `self.display(a, b)   ==>  cls.display(a, b)`

      ..

      + Python properties (data descriptors; __get__ and __set__)

        + attrname = property(fget, fset, fdel, doc)

      ..

      + for internal recalc after setting an attribute

      ..

      + for caching/lazy computation of a value

Example 5: Caching an Attribute Value
=====================================

.. container:: slide-display

   .. container:: sidebox boxed

      >>> p = Photo()
      >>> p.thumbnail    # computes thumbnail
      >>> p.thumbnail    # from self.__dict__
      >>>
      >>> del p.__dict__['thumbnail']
      >>> p.thumbnail    # computes again
      >>> p.thumbnail    # already cached again

   .. class:: incremental

      | class ThumbnailBuilder(object):
      |
      |     def __init__(self, aname, fname):
      |         self.attrname = aname
      |         self.filename = fname
      |
      |     `# non-data desc behind __dict__`
      |     `def __get__(self, inst, owner):`
      |         `with file(self.filename) as f:`
      |             `data = f.read()`
      |             `instance.__dict__[self.attrname] = data`
      |             `return data`

      | class Photo(object):
      |     thumbnail = ThumbnailBuilder('thumbnail', 'thumbnail.gif')

Example 6: Declare an Attribute Private to a Class
==================================================

.. container:: slide-display

   .. container:: sidebox boxed medium

      | class private(object): # a descriptor
      |
      |     def __init__(self, aname):
      |         self.attrname = aname
      |
      |     def __get__(self, obj, type=None):
      |         `self._ck_owner(obj)`
      |         return obj.__dict__[self.attrname]
      |
      |     def __set__(self, obj, value):
      |         `self._ck_owner(obj)`
      |         obj.__dict__[self.attrname] = value

   .. class:: incremental

      | import sys
      |
      | def _ck_owner(self, obj):
      |
      |     `caller_locals = sys._getframe(2).f_locals`
      |
      |     `if 'self' in caller_locals`
      |         `and caller_locals['self'] == obj:`
      |         `return # internal access permitted`
      |
      |     `raise NameError("Attr %r of class %r is private." % (`
      |         `self.attrname, obj))`

      | class Photo(object):
      |     _cachedir = private('_cachedir')

Example 7: Tracking Changes in a Value
======================================

.. container:: slide-display

   .. container:: sidebox boxed medium

      >>> from parser import StateMachine
      >>> vt = ValueTracker(StateMachine, 'state')

      >>> main()

      >>> for h in vt.history:
      >>>     print h
      (0, 'target_trackstate.py', 6, '__init__')
      (1, 'target_trackstate.py', 9, 'advance')
      (2, 'target_trackstate.py', 9, 'advance')
      (3, 'target_trackstate.py', 9, 'advance')

   .. class:: incremental small

      | import sys, inspect
      | class ValueTracker(object): # a descriptor
      |
      |     def __init__(self, tgt_cls, aname):
      |         self.attrname = aname
      |         `self.history = []`
      |         `setattr(tgt_cls, aname, self)`
      |
      |     `def __get__(self, obj, type=None):`
      |         `return instance.__dict__[self.attrname]`
      |
      |     `def __set__(self, obj, value):`
      |         `instance.__dict__[self.attrname] = value`
      |
      |         `finfo = inspect.getframeinfo(sys._getframe(1) )`
      |
      |         `self.history.append((value, finfo.filename, finfo.lineno, finfo.function))`

Questions?
==========

.. container:: slide-display center

   .. image:: graphics/questions-relaxation.jpg
      :width: 800

   Metaprogramming is fun!

   .. class:: huge

      `Questions?`
