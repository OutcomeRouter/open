from solution import *

assert settle([{'id': 5, 't': 172800, 'type': 'refund', 'amount': 100}, {'id': 11, 't': 3602, 'type': 'refund', 'amount': 100}, {'id': 11, 't': 3600, 'type': 'interest', 'amount': 4975}, {'id': 3, 't': 172801, 'type': 'deposit', 'amount': 100000}]) == {'balance': 100000, 'applied': [3], 'rejected': [5, 11]}
assert settle([{'id': 11, 't': 1, 'type': 'deposit', 'amount': 25}, {'id': 10, 't': 86400, 'type': 'refund', 'amount': 100000}]) == {'balance': 25, 'applied': [11], 'rejected': [10]}
assert settle([{'id': 5, 't': 3601, 'type': 'interest', 'amount': 100000}, {'id': 6, 't': 172801, 'type': 'withdraw', 'amount': 30000}]) == {'balance': -30025, 'applied': [6], 'rejected': []}
print('ok')
