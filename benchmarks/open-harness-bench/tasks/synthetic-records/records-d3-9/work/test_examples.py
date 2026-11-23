from solution import *

assert query([{'id': 60, 'name': 'dee', 'status': 'active', 'region': 'us', 'amount': 66}, {'id': 61, 'name': 'bo', 'status': 'closed', 'region': 'eu', 'amount': 2}, {'id': 36, 'name': 'cy', 'status': 'paused', 'region': 'us', 'amount': 36}, {'id': 53, 'name': 'fay', 'status': 'closed', 'region': 'us', 'amount': 5}, {'id': 29, 'name': 'bo', 'status': 'closed', 'region': 'us', 'amount': 5}]) == [{'id': 60, 'name': 'dee', 'status': 'active', 'region': 'us', 'amount': 66}]
assert query([{'id': 77, 'name': 'fay', 'status': 'active', 'region': 'us', 'amount': 116}, {'id': 85, 'name': 'eli', 'status': 'closed', 'region': 'apac', 'amount': 75}]) == [{'id': 85, 'name': 'eli', 'status': 'closed', 'region': 'apac', 'amount': 75}, {'id': 77, 'name': 'fay', 'status': 'active', 'region': 'us', 'amount': 116}]
assert query([{'id': 39, 'name': 'dee', 'status': 'active', 'region': 'us', 'amount': 126}, {'id': 46, 'name': 'dee', 'status': 'closed', 'region': 'apac', 'amount': 44}, {'id': 33, 'name': 'eli', 'status': 'paused', 'region': 'apac', 'amount': 11}]) == [{'id': 39, 'name': 'dee', 'status': 'active', 'region': 'us', 'amount': 126}]
print('ok')
