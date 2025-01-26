# Calculator Library

## Overview
The Calculator Library is a Python-based library designed to perform basic mathematical operations like addition, subtraction, multiplication, and division. With a user-friendly interface and colorful terminal outputs using the `colorama` package, this library makes calculations more engaging and visually appealing.

## Features
- **Addition**: Adds two numbers and displays the result in green.
- **Subtraction**: Subtracts one number from another and displays the result in red.
- **Multiplication**: Multiplies two numbers and highlights the result in yellow.
- **Division**: Divides one number by another, with an error message for division by zero, and displays the result in blue.

## Modules
The library is divided into two main modules for better modularity:

### `plus_minus.py`
- **Functions**:
  - `plus(a, b)`: Adds two numbers and prints the result.
  - `minus(a, b)`: Subtracts the second number from the first and prints the result.

### `mul_div.py`
- **Functions**:
  - `multiply(a, b)`: Multiplies two numbers and prints the result.
  - `divide(a, b)`: Divides the first number by the second and prints the result. Handles division by zero gracefully.

## Prerequisites
- Python 3.6 or higher
- `colorama` library (Install using `pip install colorama`)

## Installation
Clone the repository and install the required dependencies:
```bash
# Clone the repository
git clone https://github.com/ChAbdulWahhab/calc_toolkit/

# Navigate to the project directory
cd calc_toolkit

# Install dependencies
pip install -r requirements.txt
```

## Usage
Import the required module and call the functions as needed:

### Example
```python
from plus_minus import plus, minus
from mul_div import multiply, divide

plus(5, 3)  # Addition
minus(10, 4)  # Subtraction
multiply(6, 7)  # Multiplication
divide(15, 3)  # Division
divide(10, 0)  # Handle division by zero
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
