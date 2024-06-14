# test_calculator.py
import pytest
from calculator import add, subtract, multiply, divide

def test_add():
    assert add(3, 4) == 7
    assert add(-2, 5) == 3
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(10, 5) == 5
    assert subtract(-2, -2) == 0
    assert subtract(0, 10) == -10

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 10) == 0

def test_divide():
    assert divide(10, 2) == 5
    assert divide(-6, 3) == -2
    assert divide(0, 5) == 0

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

# Optionally, you can run pytest.main() to execute the tests if not running pytest directly from command line
if __name__ == "__main__":
    def test_subtract():
    assert subtract(10, 5) == 5
    assert subtract(-2, -2) == 0
    assert subtract(0, 10) == -10
    pytest.main()
