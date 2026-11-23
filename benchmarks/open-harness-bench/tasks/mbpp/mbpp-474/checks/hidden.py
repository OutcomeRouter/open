import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert replace_char("polygon",'y','l')==("pollgon")
assert replace_char("character",'c','a')==("aharaater")
assert replace_char("python",'l','a')==("python")
print('ok')
