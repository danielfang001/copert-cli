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


def primes_with_cubed_in_range(min_value: int, max_value: int) -> list[int]:
    """Find all prime numbers whose cube is between min_value and max_value (inclusive)."""
    primes_in_cube_range = []
    # To find primes whose cube is within [min_value, max_value],
    # find primes p where p^3 >= min_value and p^3 <= max_value.
    # We can limit the search by finding the cube root bounds.
    import math
    min_prime = math.ceil(min_value ** (1/3))
    max_prime = math.floor(max_value ** (1/3))
    
    for p in range(min_prime, max_prime + 1):
        if is_prime(p):
            primes_in_cube_range.append(p)
    return primes_in_cube_range


import unittest

class TestPrimeFunctions(unittest.TestCase):
    def test_primes_with_cubed_in_range_1_to_100(self):
        expected_primes = [2, 3, 5]  # 2^3=8, 3^3=27, 5^3=125(not in range), so only 2 and 3
        result = primes_with_cubed_in_range(1, 100)
        self.assertListEqual(result, [2, 3])

    def test_primes_with_cubed_in_range_1_to_27(self):
        result = primes_with_cubed_in_range(1, 27)
        self.assertListEqual(result, [2, 3])

    def test_primes_with_cubed_in_range_27_to_125(self):
        result = primes_with_cubed_in_range(27, 125)
        self.assertListEqual(result, [3, 5])

    def test_primes_with_cubed_in_range_no_primes(self):
        result = primes_with_cubed_in_range(126, 200)
        self.assertListEqual(result, [])

    def test_primes_with_cubed_in_range_edge_cases(self):
        # Test edge cases like 0 and negative
        self.assertListEqual(primes_with_cubed_in_range(0, 1), [])
        self.assertListEqual(primes_with_cubed_in_range(-10, 1), [])


if __name__ == "__main__":
    unittest.main()

    # Example usage
    test_numbers = [0, 1, 2, 3, 4, 5, 16, 17, 19, 20]
    for num in test_numbers:
        print(f"{num} is prime: {is_prime(num)}")