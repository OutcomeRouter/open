from solution import *

assert transform(' World Data42 Ok') == ' Ok World Data42'
assert transform('  2026 \n zzzz \n io \n bookkeeper \n World \n F \n bookkeeper ') == '   \n \n \n \n \n \n F io 2026 zzzz World bookkeeper bookkeeper'
assert transform('  Ok Queue Data42 hello  ') == '    Ok Queue hello Data42'
print('ok')
