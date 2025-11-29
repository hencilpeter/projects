```python
def test_add_numbers_positive_numbers():
    assert add_numbers(2, 3) == 5

def test_add_numbers_negative_numbers():
    assert add_numbers(-2, -3) == -5

def test_add_numbers_mixed_numbers():
    assert add_numbers(-2, 3) == 1

def test_add_numbers_zero():
    assert add_numbers(0, 0) == 0
```