```python
import unittest

def add_numbers(num1, num2):
    return num1 + num2

class TestAddNumbers(unittest.TestCase):
    
    def test_add_positive_numbers(self):
        self.assertEqual(add_numbers(2, 3), 5)
        
    def test_add_negative_numbers(self):
        self.assertEqual(add_numbers(-2, -3), -5)
        
    def test_add_mixed_numbers(self):
        self.assertEqual(add_numbers(3, -2), 1)
        
    def test_add_zero_numbers(self):
        self.assertEqual(add_numbers(0, 0), 0)
        
    def test_add_large_numbers(self):
        self.assertEqual(add_numbers(1000000, 2000000), 3000000)

if __name__ == '__main__':
    unittest.main()
```