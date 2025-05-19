def power(a: int, b: int) -> int:
    for i in range(b):
        a *= i

    return a
