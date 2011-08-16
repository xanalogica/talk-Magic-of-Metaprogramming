import sys
import inspect

class AspectTracker(object):

    def __init__(self, tgt_cls, attrname):
        self.attrname = attrname
        self.history = []
        setattr(tgt_cls, attrname, self)

#    @classmethod
#    def attach(cls, tgt, attrname):
#        at = cls(attrname)
#        setattr(tgt, attrname, at)
#        return at

    def __get__(self, instance, type=None):
        return instance.__dict__[self.attrname]

    def __set__(self, instance, value):
        instance.__dict__[self.attrname] = value

        frame = sys._getframe(1)
        finfo = inspect.getframeinfo(frame)

        try:
            self.history.append((value, finfo.filename, finfo.lineno, finfo.function))
        finally:
            del frame


if __name__ == "__main__":

    pgm = 'target_trackstate' # pgm = sys.argv[1]

    m = __import__(pgm, globals(), locals())

    #at = AspectTracker.attach(m.StateMachine, 'count')
    at = AspectTracker(m.StateMachine, 'count')
    m.main()

    for h in at.history:
        print h
