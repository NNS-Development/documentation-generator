```markdown
# Project Overview

This code defines a function that calculates the factorial of a non-negative integer. It uses a recursive approach, where the function calls itself with a smaller input until it reaches the base case (n=0 or n=1).

- **Main purpose and functionality:** Calculate the factorial of a given number.
- **High-level architecture/design patterns:** Recursion.
- **Key features:**
    - Handles the base cases of 0 and 1.
    - Recursively calculates the factorial for n > 1.

# Technical Documentation

## Functions

### `factorial(n: int) -> int`

- **Purpose:** Calculates the factorial of a non-negative integer `n`.
- **Parameters:**
    - `n` (int): The non-negative integer for which to calculate the factorial.
- **Return value:**
    - `int`: The factorial of `n`.
- **Examples:**

```
python
factorial(0)  # Expected output: 1
factorial(1)  # Expected output: 1
factorial(5)  # Expected output: 120

```
- **Exceptions Raised:** None explicitly handled in the provided AST.  It's assumed that the input `n` is a non-negative integer.  Behavior with negative or non-integer input is undefined.

# Dependencies

- **Required external packages and their versions:** None
- **System requirements:**  Python 3 (due to the use of `ast.unparse`).

# Implementation Details

- **Key algorithms explained:**
    - The factorial is calculated using recursion. The function checks if `n` is 0 or 1. If so, it returns 1 (base case). Otherwise, it returns `n` multiplied by the factorial of `n-1`. This continues until the base case is reached.
- **Important design decisions:**
    - The use of recursion makes the code concise and easy to understand, directly reflecting the mathematical definition of factorial.
- **Performance considerations:**
    - For large values of `n`, the recursive approach might lead to a stack overflow error due to the maximum recursion depth limit in Python. An iterative approach would be more efficient for very large `n`.
- **Threading/async behavior:** None. The code is synchronous.

# Usage Guide

- **Installation instructions:**  No specific installation is required. The code is a single function and can be directly included in a Python script.
- **Configuration requirements:** None.
- **Code examples for common use cases:**

```
python
def factorial(n: int) -> int:
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

print(factorial(5))  # Output: 120
print(factorial(1)) # Output: 1
print(factorial(0)) # Output: 1

```

- **Best practices:**
    - Ensure the input `n` is a non-negative integer to avoid unexpected behavior.
    - For calculating factorials of very large numbers, consider using an iterative approach to prevent potential stack overflow errors.

# Notes and Warnings

- **Known limitations:**
    - The function may encounter a RecursionError for large input values due to Python's recursion depth limit.
- **Common pitfalls:**
    - Providing negative or non-integer input will lead to infinite recursion and a stack overflow.
- **Security considerations:** None.
```