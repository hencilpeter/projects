import unittest

class TestAddNumbers(unittest.TestCase):
    
    def test_positive_numbers(self):
        self.assertEqual(add_numbers(3, 4), 7)
    
    def test_negative_numbers(self):
        self.assertEqual(add_numbers(-3, -4), -7)
    
    def test_mixed_numbers(self):
        self.assertEqual(add_numbers(5, -3), 2)
    
    def test_zero(self):
        self.assertEqual(add_numbers(0, 0), 0)
    
    def test_large_numbers(self):
        self.assertEqual(add_numbers(1000000, 1000000), 2000000)

if __name__ == '__main__':
    unittest.main()