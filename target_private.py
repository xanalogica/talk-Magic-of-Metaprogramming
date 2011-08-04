class Alpha(object):

    def __init__(self, name):
        self.name = name
        self.secret = 'xyzzy'

    def report(self):
        print "name = %r, secret = %r" % (self.name, self.secret)

def main():

    a = Alpha('Jeff')
    a.report()

    print "A stolen secret:", a.secret
