import sys
import re
import string

def main():

    print "In target_import, type(__builtins__) is %r" % (type(__builtins__), )

    print sys.modules.keys()
