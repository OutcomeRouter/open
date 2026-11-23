from solution import *

assert settle([{'id': 12, 't': 3602, 'type': 'interest', 'amount': 100}]) == {'balance': 0, 'applied': [12], 'rejected': []}
assert settle([{'id': 3, 't': 86400, 'type': 'deposit', 'amount': 100}, {'id': 11, 't': 86400, 'type': 'deposit', 'amount': 4975}, {'id': 8, 't': 3600, 'type': 'withdraw', 'amount': 4975}]) == {'balance': 75, 'applied': [3, 11, 8], 'rejected': []}
assert settle([{'id': 2, 't': 86401, 'type': 'refund', 'amount': 100}]) == {'balance': 0, 'applied': [], 'rejected': [2]}
print('ok')
