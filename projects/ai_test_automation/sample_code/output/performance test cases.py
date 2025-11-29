To test the performance of the `add_numbers` function in Python, we can use the `timeit` module to measure the execution time of the function for different input sizes. Below are the performance tests for the function:

```python
import timeit

# Define the function to test
def add_numbers(num1, num2):
    return num1 + num2

# Initialize input values
num1 = 10
num2 = 20

# Test the performance of the function for different input sizes
input_sizes = [10, 100, 1000, 10000]

for size in input_sizes:
    setup = f"from __main__ import add_numbers, num1, num2"
    stmt = f"add_numbers(num1, num2)"
    
    execution_time = timeit.timeit(stmt=stmt, setup=setup, number=size)
    
    print(f"Execution time for input size {size}: {execution_time} seconds")
```

This code snippet defines the `add_numbers` function and tests its performance for different input sizes (10, 100, 1000, 10000) using the `timeit` module. The execution time for each input size is printed out in seconds. You can modify the `input_sizes` list to include more input sizes for a more comprehensive performance analysis.