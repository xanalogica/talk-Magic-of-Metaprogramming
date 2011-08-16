def TagClass(orig_cls):
    orig_cls.__special__ = True
    return orig_cls

@TagClass
class Alpha(object):
    pass

class Beta(Alpha):
    pass

print '__special__' in Alpha.__dict__
print '__special__' in Beta.__dict__
print type(Alpha), type(Beta)

class TagClass(type):
    def __init__(cls, name, bases, class_dict):
        cls.__special__ = True

class Alpha(object):
    __metaclass__ = TagClass

class Beta(Alpha):
    pass

print '__special__' in Alpha.__dict__
print '__special__' in Beta.__dict__
print type(Alpha), type(Beta)

class Beta(Alpha):
    __metaclass__ = type

print '__special__' in Alpha.__dict__
print '__special__' in Beta.__dict__
print type(Alpha), type(Beta)
