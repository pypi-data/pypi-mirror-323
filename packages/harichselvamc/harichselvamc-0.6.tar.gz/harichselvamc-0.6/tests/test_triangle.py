import unittest
from harichselvamc import generate_pascals_triangle

class TestPascalTriangle(unittest.TestCase):
    def test_generate_pascals_triangle(self):
        # Test for first 5 rows of Pascal's Triangle
        expected_output = [
            [1],
            [1, 1],
            [1, 2, 1],
            [1, 3, 3, 1],
            [1, 4, 6, 4, 1]
        ]
        result = generate_pascals_triangle(5)
        self.assertEqual(result, expected_output)

    def test_empty_input(self):
        # Test for an empty input (n=0)
        result = generate_pascals_triangle(0)
        self.assertEqual(result, [])

    def test_single_row(self):
        # Test for a single row (n=1)
        result = generate_pascals_triangle(1)
        self.assertEqual(result, [[1]])

    def test_large_input(self):
        # Test for larger input (n=10)
        result = generate_pascals_triangle(10)
        self.assertEqual(len(result), 10)  # Check if the number of rows is 10
        self.assertEqual(len(result[9]), 10)  # Check if the last row has 10 elements

if __name__ == "__main__":
    unittest.main()
