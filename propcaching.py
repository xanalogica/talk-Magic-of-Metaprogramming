class ThumbnailBuilder(object):

    def __init__(self, filename):
        self.filename = filename

    def __get__(self, instance, owner):
        with file(self.filename) as f:
            print "(reading thumb)"
            data = f.read()[-1]
            instance.__dict__['thumbnail'] = data
            return "TEST"

class Photo(object):
    thumbnail = ThumbnailBuilder('thumbnail.gif')

p = Photo()
print p.thumbnail, "should load"
print p.thumbnail, "should NOT load"
del p.__dict__['thumbnail']
print p.thumbnail, "should load"
print p.thumbnail, "should NOT load"
