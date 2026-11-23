CORRECT = '''def fizzbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


if __name__ == "__main__":
    import sys
    for i in range(1, int(sys.argv[1]) + 1):
        print(fizzbuzz(i))
'''

WRONG = '''def fizzbuzz(n: int) -> str:
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
'''

LAZY = '''_TABLE = {%s}

def fizzbuzz(n: int) -> str:
    return _TABLE.get(n, str(n))
''' % ", ".join(
    f"{i}: {('FizzBuzz' if i % 15 == 0 else 'Fizz' if i % 3 == 0 else 'Buzz' if i % 5 == 0 else str(i))!r}"
    for i in range(1, 21)
)
