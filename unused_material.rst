Who Am I?
=========

.. container:: slide-display

   .. class:: incremental

      + one who (really) loves to program (and teach)
      + programming since 1971, in Python since 1996
      + organizer (PyCon US, PSF, ZF, DFW Pythoneers)
      + self-employed developer and trainer
      + author of many screencasts on showmedo.com

A Few More Ideas for Metaprogramming
====================================

.. container:: slide-display

   .. class:: incremental

      ::

        @trackexceptions
        def func(...):

        @trackexceptions(methpatt="get_")
        class C(...):

      ::

        @trackinstances
        class C(...):

      ::

        @internalmethod
        def greetings(self, x):

      + detect the most number of threads running concurrently
      + log all calls from module X to function Y

      ::

        @addtoclass(Moonbase)  # at import time
        def hello(self, code, priormeth=None):
          print "Hello"
          self.greeting(68)

Sample Code - Binding of Functions into Methods
===============================================

.. container:: slide-display

   .. container:: handout

      Class __dict__ store methods as functions.

      Python is built upon a function-based environment.  Non-data descriptors
      add the object-oriented features by binding functions into methods.

   .. class:: incremental

      | class MethodDescriptor(object):
      |     def __get__(self, instance, instance_type=None):
      |         return types.MethodType(self, instance, instance_type)

      | class D(object):
      |     def func(self, x):
      |         return x

      >>> D.__dict__['f']
      <function func at 0xb73ebf7c>

      >>> D.f                 # type(D).__dict__['func'].__get__(None, self)
      <unbound method D.func>

      >>> d = D()
      >>> d.f                 # type(d).__dict__['f'].__get__(d, type(d))
      <bound method D.func of <__main__.D object at 0xb71c794c>>

     Monitor Who is Opening Which Files

  .. container:: slide-display

     .. class:: incremental



  A Solution to #8: ??? external decorating __builtin__

  .. container:: slide-display

     .. class:: incremental

        + can filter on path, name, caller
        + can hook the .close method of a specific instance???

        + applying function decorators from outside
        + applying class decorators from outside

        + more descriptors; using get-overrides to catch file opens, in order to understand a complex pgm
          but maybe just for opens of files in a specific directory or a particular name

          + (talk about fstozodb.log or fax/ directory that keeps popping up; show traceback)
          + (talk about *changing* the name or directory of a file being opened)


No More
=======


::

  What are Some Examples of Metaprogramming?

   + protocol negotiation
   + ORMs ala SQLAlchemyDA

  consider - how can I walk across the attrs of a class?  an instance?


  as a demo, create a class equivalent to a function, with default args.

  def func(...):

  class C(...):
    def meth(...):


  for (1) debugging or (2) changing code you do not own/control


  Callability: Benefits of Decorators

  .. container:: slide-display

     .. class:: incremental

  username = mkfunction(globalspace, formalparameters, codeobject)
  username = export(username)  # must return a callable
  ... (major separation in time)   a decorator is NOT the wrapper; a decorator DOES the wrapping
              i.e. the gift wrapper clerk and the wrapping paper itself
  username('Jeff')




  metaprogramming
    how do we get our metapgm wrapped around another pgm?
    - run 2nd as arg to 1st?
    - change site.py
    - use -m <module>?


    5) sliding a delegate in
       (replace a method that takes a self, with a delegate that has its own self)
       (and maybe a closure arg of the prior method that was replaced)


    patching functions
  - in the class space
  - in the instance space

  use Ctrl-C trick to drop into a running pgm
  - and import a metapgm that logs only the IP addr of a problem browser



  1) subclassing can be treated as a registration
  of an object with the parent class, and the body of the cubslclass being the
  particular registration data.  Think media handlers.


   ? can I subclass a module
   ? can I make a module's dict read-only?


  >>> int.__subclasses__()
  [<type 'bool'>]



  AOP?
  delegation?
  likeness to plugboard logic analyzer


  Looking Behind the Walls (the secret passages)
  In Python's Attic
  In Python's Basement

  ?? reasons for swapping out class methods at runtime??



  mix-in classes are a way to produce a class from fragments of a class
   - awkward, multiple-inheritance
   - hard to pickle



  what does this do?   python -m mymod helper.py


  even with multiple inheritance, an instance knows of its one true __class__

  __metaclass__ does not have to be a class, just a callable taking (name, bases, dict)
      metaclass(name, bases, dict)  ===>  metaclass.__class__.__call__(name, bases, dict)
                        invokes metaclass.__new__  and  metaclass.__init__

      + final classes are a form of definition constraint
        find all classes using object.__subclasses__()
      + defer such checking to unit tests?  something at import time

      + someone declares their class wraps an SQL table; introspect the columns of
        that table and provide descriptors for each one, including type contraints.

      + class/instance  ::  table/row     a shared context
        a useful example of class methods and instance methods i.e. Members
          nrecs = len(Members)
          m = Members.load(...)
          m = Members(...)
          m.save()

      + about __subclasses__(); use to tell a metaclass to flush each caching class?
      + at unittest time, tell metaclasses to verify each of their classes
      + how to walk all classes in a program, in order to validate things about them
      + can I find all nested classes?  are they missing a __module__ or __file__?

      + metaclasses let you share code among multiple meta*classes*.  Treats classes
        more like objects -- they come and go, are duplicated, collected, iterated
        over.  A custom class appears for each domain object found.

        Good for modeling systems with class-like behavior?

        Domain objects show up in pgms as classes and instances.


  object.__getattribute__(name)
    b.x
    type(b).__dict__['x'].__get__(b, type(b))

  data descriptors
  instance variables
  non-data descriptors
  __getattr__

  type.__getattribute__(name)
    B.x
    B.__dict__['x'].__get__(None, B)

    def __getattribute__(self, key):
      "Emulate type_getattro() in Objects/typeobject.c"
      v = object.__getattribute__(self, key)
      if hasattr(v, '__get__'):
         return v.__get__(None, self)
      return v

   + descriptors are invoked by the __getattribute__ method (override it and they break)


  a.x
  a.__dict__['x'
  type(a).__dict__['x'
  (then base classes)

  direct call:       a.x =>                      x.__get__(a)
  instance binding:  a.x =>  type(a).__dict__['x'].__get__(a, type(a))
    (has a precendence)
    if no __get__, return the descriptor object itself, unless there is a value in the __dict__
    if has __set__ and/or __delete__, then it is a data descriptor
    if has neither __set__ nor __delete__, then it is a non-data descriptor
      hence data descriptors override a redefinition in the instance
      and non-data descriptors can be overridden by instances


  class binding:     A.x =>        A.__dict__['x'].__get__(None, A)

  object.__getattribute__(self, name)  # ALWAYS CALLED  (MAY BE BYPASSED BY IMPLICIT

    "Special Method Lookup"   (for performance reasons)
        len(x)  <==> type(x).__len__(x)   # looks up via metaclass __getattribute__
        x.__len__()                       # looks up via class __getattribute__
        len(x)                            # bypasses __getattribute__ and uses __len__ method defined in the class
              (none of these ever look in the instance __dict__)


  object.__getattr__(self, name)   # called when name has not been found in the usual places

  object.__setattr__(self, name, value)  # called instead of storing value into __dict__

  object.__delattr__(self, name)


  (show 'binding behavior', i.e. a value stored WITHOUT __get__/__set__ and a value stored WITH them)


      + except when it finds an object with a __get__/__set__

  object.__get__(self, instance, owner)  # return value or AttributeError
  object.__set__(self, instance, value)
  object.__delete__(self, instance)

      + neither 'type' nor 'object have a '__getattr__' method.

  type
  (__dict__/(dictproxy)
    __call__                                  'type'  slot_tp_call?    x(...)  <==>  x.__call__(...)
       lookup_method(self, '__call__') ==> _PyType_Lookup(mytype, attrname)
    __delattr__               OBJECT?         'object'
    __eq__                                    'type'
    __ge__                                    'object'
    __getattribute__          OBJECT?         'type'                   x.name  <==>  x.__getattribute__(name)

           NAME                SLOT         FUNCTION              WRAPPER          DOC
    TPSLOT("__getattribute__", tp_getattro, slot_tp_getattr_hook, wrap_binaryfunc, ""),
    TPSLOT("__getattribute__", tp_getattr,  NULL,                 NULL,            ""),
      slot_tp_getattro       used when __getattribute__ is overridden but no    __getattr__ is present
      slot_tp_getattr_hook   used when a __getattr__ hook is present

    __gt__                                    'object'
    __hash__                  OBJECT?         'type'
    __init__                  OBJECT?         'type'
    __le__                                    'object'
    __lt__                                    'object'
    __ne__                                    'type'
    __new__                   OBJECT?         'type'
    __repr__                  OBJECT?         'type'
    __setattr__               OBJECT?         'type'
  (members)
    __base__
    __basicsize__
    __dictoffset__
    __flags__
    __itemsize__
    __mro__
    __weakrefoffset__
  (getsets)
    __abstractmethods__ (R/W)
    __bases__           (R/W)
    __dict__            (R/O)
    __doc__             (R/O)
    __module__          (R/W)
    __name__            (R/W)
  (methods)
    __instancecheck__
    __subclasscheck__
    __subclasses__
    mro

  (interesting)
    tp_call ::= type_call()
      obj = type->tp_new(type, args, kwds)
      type->tp_init(obj, args, kwds)
      return obj

  tp_getattro ::= type_getattro(type, name)
    metatype = Py_TYPE(type)

    meta_attribute = _PyType_Lookup(metatype, name)         # look in the metatype
    if meta_attribute:
      meta_get = Py_TYPE(meta_attribute)->tp_descr_get
      if meta_get and PyDescr_IsData(meta_attribute):       # use data desc in metatype
          return meta_get(meta_attribute, type, metatype)

    attribute = _PyType_Lookup(type, name)                  # look in tp_dict of this type *and* bases
    if attribute:
      local_get = Py_TYPE(attribute)->tp_desc_get
      if local_get:
          return local_get(attribute, NULL, type)
      return attribute

    if meta_get:                                            # use non-data desc in metatype
      return meta_get(meta_attribute, type, metatype)

    if meta_attribute:
      return meta_attribute

    raise AttributeError

  tp_setattro ::= type_setattro()
  tp_new ::= type_new()
  tp_init ::= type_init()

  object_new()
  object_init()


  call_method()
  call_maybe()
  PyObject_CallMethod()
  _PyType_Lookup(type, '__dict__')
  lookup_maybe()
  lookup_method()
  _PyObject_LookupSpecial()


  Does a 'type' have its own internal dictionary?  Really?


  type.__base__  ---> object
  type           <--- object.__class__
  None           <--- object.__base__
  type.__class__ ---> type


  object
    (__dict__)
      __delattr__                             'object'
      __doc__
      __getattribute__                        'object'
      __hash__                                'object'
      __init__                                'object'
      __new__                                 'type'
      __repr__                                'object'
      __setattr__                             'object'
      __str__                                 'object'
    (getsets)
      __class__       (R/W)
    (methods)
      __format__
      __reduce__
      __reduce_ex__
      __sizeof__
      __subclasshook__
    (members)
      EMPTY

  tp_getattro ::= PyObject_GenericGetAttr
  tp_setattro ::= PyObject_GenericSetAttr
  tp_new      ::= object_new(type, args, kwds)
  tp_init     ::= object_init # NOP


  PyObject_GetAttrString(obj, name)
    if Py_TYPE(obj)->tp_getattr:
        return Py_TYPE(obj)->tp_getattr(obj, name)
    return PyObject_GetAttr(obj, name)

  PyObject_GetAttr(obj, name)
    tp = Py_TYPE(obj)
    if tp->tp_getattro:
        return tp->tp_getattro(obj, name)
    if tp->tp_GETATTR:
        return tp->tp_getattr(obj, name)
    raise AttributeError


  Descriptor Machinery for Classes
  --------------------------------

  Implemented in *type.__getattribute__*

  Example: A.x

  ::

    descriptor = A.__class__.x
    descriptor.__get__(instance=None, instance_type=self)

    def __getattribute__(self, key):
      v = object.__getattribute__(self, key)
      if hasattr(v, '__get__'):
        return v.__get__(None, self)
      return v

  Descriptor Machinery for Instances
  ----------------------------------

  Implemented in *object.__getattribute__*

  Example: a.x

  ::

    descriptor = a.__class__.x
    descriptor.__get__(instance=a, instance_type=type(a))


  How Do Decorators Work?  the 3-things a decorator can do

  .. container:: slide-display

     .. class:: incremental

        + registering *username* with some entity::

           def export(func):
               api_register(func)
               return func

        + tagging *username* with additional metadata::

           def export(func):
               func.__export__ = True
               return func

        + inserting code between the caller and callee::

           def export(func):
               def trace(*args, **kw):
                   rc = func(*args, **kw)
                   print args, kw, rc
                   return rc
               return trace

  Sample Problem #9: ??? tracing the cause of a slowdown

  .. container:: slide-display

     .. class:: incremental

        + in-out phase checking

          + (use it to measure time for a call)
          + (use it to toggle logging on/off)

  A Solution to #9: hooking the operation, measuring the time and saving the log -if- the problem showed up

  .. container:: slide-display

     .. class:: incremental

        + ???

        + can filter on details of events, not just the overall event
          + import of a specific module
          + call to a function -from- a specific module
          + make attrs read-only or invisible outside their creator
          + record their performance

       + catch file opens, in a specific directory
       + toggle logging on/off only within a specific section of code or when something looks wrong


      + special methods: __XXX__ bypass descriptors, for performance, avoid recursion
      + there are two kinds of descriptors; data and non-data
        + non-data: methods, staticmethod, classmethod
        + data: property
      + to make a data descriptor read-only
        + define both __get__ and __set_
        + have __set__ raise an AttributeError
      + neither 'type' nor 'object have a '__getattr__' method.

      + implementor of descriptor behavior for
        + classes, type.__getattribute__
        + instances, object.__getattribute__



  Summary: Benefits of Metaprogramming

  .. container:: slide-display

     .. class:: incremental

       + adopt a more declarative style

          + less programmer work, less human error
          + hiding necessary magic

        + adapt to negotiated protocols
        + better control of unchangable legacy programs

        + track down difficult runtime problems

          + protect readonly, private attributes
          + capture changes-in-state
          + limit the logging needed (just-in-time)

        + test your knowledge of a complex system

          + what modules or files are used?
          + probe for expensive operations

        + try out experimental changes

          + new caching algorithms

  Summary: Drawbacks of Metaprogramming

  .. container:: slide-display

     .. class:: incremental

        + influences not visible in code, hard to understand
        + requires a different perspective on programming
        + can interfere with pgm performance, correctness
