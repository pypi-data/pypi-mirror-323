import unittest
from topsis.topsis import topsis

class TestTopsis(unittest.TestCase):
    def test_topsis(self):
        matrix = [[250, 16, 12],
                  [200, 20, 8],
                  [300, 12, 16]]
        weights = [0.5, 0.3, 0.2]
        impacts = ['+', '+', '-']
        expected_ranks = [2, 3, 1]
        self.assertEqual(list(topsis(matrix, weights, impacts)), expected_ranks)

if __name__ == "__main__":
    unittest.main()
