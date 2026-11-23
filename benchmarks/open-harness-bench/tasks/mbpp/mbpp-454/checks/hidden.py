import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert text_match_wordz("pythonz.")==True
assert text_match_wordz("xyz.")==True
assert text_match_wordz("  lang  .")==False
print('ok')
