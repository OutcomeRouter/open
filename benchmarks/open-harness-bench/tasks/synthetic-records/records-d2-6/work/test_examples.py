from solution import *

assert query([{'id': 37, 'name': 'bo', 'status': 'closed', 'region': 'eu', 'amount': 57}, {'id': 87, 'name': 'fay', 'status': 'closed', 'region': 'eu', 'amount': 33}, {'id': 23, 'name': 'ana', 'status': 'closed', 'region': 'eu', 'amount': 75}, {'id': 83, 'name': 'ana', 'status': 'paused', 'region': 'eu', 'amount': 155}]) == [{'id': 37, 'name': 'bo', 'status': 'closed', 'region': 'eu', 'amount': 57}, {'id': 23, 'name': 'ana', 'status': 'closed', 'region': 'eu', 'amount': 75}, {'id': 83, 'name': 'ana', 'status': 'paused', 'region': 'eu', 'amount': 155}]
assert query([]) == []
assert query([{'id': 18, 'name': 'fay', 'status': 'paused', 'region': 'eu', 'amount': 65}, {'id': 10, 'name': 'cy', 'status': 'active', 'region': 'us', 'amount': 140}, {'id': 33, 'name': 'eli', 'status': 'paused', 'region': 'apac', 'amount': 93}, {'id': 57, 'name': 'dee', 'status': 'closed', 'region': 'us', 'amount': 30}]) == [{'id': 18, 'name': 'fay', 'status': 'paused', 'region': 'eu', 'amount': 65}, {'id': 10, 'name': 'cy', 'status': 'active', 'region': 'us', 'amount': 140}]
print('ok')
