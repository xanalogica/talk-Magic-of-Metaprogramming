class Alpha(object):

    def __init__(self, name):
        self.name = name

def main():

    a = Alpha('Jeff')
    a.name = 'John'                    # raises an exception
