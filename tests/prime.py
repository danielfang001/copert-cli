def is_prime(n: int) -> bool:
    """Return True if n is a prime number, False otherwise."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def primes_in_range(start: int, end: int) -> list[int]:
    """Return a list of prime numbers in the range [start, end)."""
    return [n for n in range(start, end) if is_prime(n)]


if __name__ == "__main__":
    # Example usage
    test_numbers = [0, 1, 2, 3, 4, 5, 16, 17, 19, 20]
    for num in test_numbers:
        print(f"{num} is prime: {is_prime(num)}")