from solution import *

assert settle([{'id': 4, 't': 3601, 'type': 'refund', 'amount': 4975}]) == {'balance': 0, 'applied': [], 'rejected': [4]}
assert settle([{'id': 1, 't': 2, 'type': 'refund', 'amount': 100001}, {'id': 12, 't': 86401, 'type': 'deposit', 'amount': 100}, {'id': 1, 't': 90000, 'type': 'withdraw', 'amount': 4975}, {'id': 2, 't': 86399, 'type': 'withdraw', 'amount': 25}, {'id': 6, 't': 86399, 'type': 'deposit', 'amount': 25}, {'id': 9, 't': 172800, 'type': 'withdraw', 'amount': 0}, {'id': 6, 't': 86400, 'type': 'deposit', 'amount': 30000}]) == {'balance': 100, 'applied': [6, 12, 9], 'rejected': [1, 2]}
assert settle([{'id': 3, 't': 172801, 'type': 'deposit', 'amount': 25000}, {'id': 8, 't': 90002, 'type': 'interest', 'amount': 25}, {'id': 5, 't': 2, 'type': 'withdraw', 'amount': 4975}]) == {'balance': 25000, 'applied': [8, 3], 'rejected': [5]}
print('ok')
