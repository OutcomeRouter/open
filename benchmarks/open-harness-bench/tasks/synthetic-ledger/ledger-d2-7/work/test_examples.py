from solution import *

assert settle([{'id': 10, 't': 172802, 'type': 'interest', 'amount': 4975}]) == {'balance': 0, 'applied': [10], 'rejected': []}
assert settle([{'id': 12, 't': 2, 'type': 'withdraw', 'amount': 25000}, {'id': 5, 't': 86402, 'type': 'withdraw', 'amount': 100000}, {'id': 5, 't': 1, 'type': 'deposit', 'amount': 30000}, {'id': 12, 't': 86400, 'type': 'withdraw', 'amount': 100}]) == {'balance': 4900, 'applied': [12, 5, 12], 'rejected': [5]}
assert settle([{'id': 9, 't': 172801, 'type': 'deposit', 'amount': 0}, {'id': 11, 't': 172800, 'type': 'deposit', 'amount': 30000}]) == {'balance': 30000, 'applied': [9, 11], 'rejected': []}
print('ok')
