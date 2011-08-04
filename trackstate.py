import sys
import inspect

class AspectTracker(object):

    def __init__(self, attrname, orig_value):
        self.attrname = attrname
        self.orig_value = orig_value
        self.value = orig_value
        self.history = [self.value]

    @classmethod
    def attach(cls, tgt, attrname):
        orig_value = getattr(tgt, attrname)
        at = cls(attrname, orig_value)
        setattr(tgt, attrname, at)
        return at

    def __get__(self, obj, type=None):
        return self.value

    def __set__(self, obj, value):
        self.value = value

        frame = sys._getframe(1)
        finfo = inspect.getframeinfo(frame)

        try:
            self.history.append((value, finfo.filename, finfo.lineno, finfo.function))
        finally:
            del frame


if __name__ == "__main__":

    pgm = sys.argv[1]

    m = __import__(pgm, globals(), locals())

    at = AspectTracker.attach(m.StateMachine, 'count')
    m.main()

    for h in at.history:
        print h
