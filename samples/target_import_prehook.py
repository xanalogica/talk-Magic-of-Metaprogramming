import sys
import re
import string
import alpha

def main():

    print "In target_import_prehook, type(__builtins__) is %r" % (type(__builtins__), )

    print sys.modules.keys()
