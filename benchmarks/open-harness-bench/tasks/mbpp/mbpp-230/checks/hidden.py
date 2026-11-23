import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert replace_blank("hello people",'@')==("hello@people")
assert replace_blank("python program language",'$')==("python$program$language")
assert replace_blank("blank space","-")==("blank-space")
print('ok')
