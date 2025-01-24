# PyVeritas

Revolutionizing Python testing with adaptive, intelligent, and developer-friendly tools.

# 🚀 Overview

PyVeritas is an advanced software testing framework designed to push the boundaries of Python testing. By combining the precision of unit testing, the randomness of fuzzing, and the adaptability of AI, PyVeritas helps developers create robust, reliable, and high-quality Python code effortlessly.

PyVeritas is code-aware, behavior-driven, and environment-adaptive. It doesn’t just test your code—it learns from it, evolves with it, and ensures every corner is thoroughly validated.

# 🌟 Features

**Intelligent Fuzzing**: Automatically generates meaningful fuzzing inputs tailored to your specific code logic.

**Behavioural Validation**: Compare your program's outputs against expected behaviours using AI models.

**Dynamic Test Optimization**: Keeps your test suite lean and relevant by analyzing historical failures and code changes.

**Cross-Environment Simulation**: Test across multiple Python versions and runtime environments.

**Actionable Insights**: Provides real-time feedback on test coverage, bottlenecks, and high-risk areas.

# 🛠️ Installation

PyVeritas is easy to install via pip:

```bash
pip install pyveritas
```

# ✨ Quick Start

Example, Testing a Calculator Function:

```python
from pyveritas import VeritasTestSuite, VeritasFuzzer

# Pre-existing function to test
def calculate_discount(price: float, discount: float) -> float:
    print(f"price={price}, discount={discount}")  # Debug print
    if price <= 0 or discount < 0 or discount > 100:
        print("Raising ValueError: Invalid price or discount")
        raise ValueError("Invalid price or discount")
    return price * (1 - discount / 100)

# Testing and fuzzing integration
if __name__ == "__main__":
    print("Running test suite...")
    # Instantiate the VeritasTestSuite
    suite = VeritasTestSuite("DiscountCalculatorTests")
    # Setup indivual test parameters
    suite.test("Discount calculation is correct",
               lambda: calculate_discount(100, 20) == 80)
    # Setup individual test parameters
    suite.test(
        "Invalid discount should raise ValueError",
        lambda: calculate_discount(-10, 50),
        should_raise=ValueError
    )
    # Explicitly run the test suite
    suite.run()  

    print("Running fuzz tests...")
    # Instantiate the VeritasFuzzer
    fuzzer = VeritasFuzzer("DiscountCalculatorFuzzing")
    # Setup fuzzing parameters
    fuzzer.test(
        input_spec={
            "price": lambda: VeritasFuzzer.float_range(0, 1000),
            "discount": lambda: VeritasFuzzer.float_range(0, 100),
        },
        iterations=1000,
    )
    # Explicitly run the fuzz tests
    fuzzer.run(calculate_discount)

    print("Test suite and fuzz tests complete.")
    # Output the summary of the test suite
    suite.summary()
    # Output the summary of the fuzz tests
    fuzzer.summary()
```

The code above will return the following:

```bash
Running test suite...
Running test suite: DiscountCalculatorTests
Test 1 PASSED: Discount calculation is correct
Test 2 FAILED: Invalid discount should raise ValueError (Unexpected exception: Invalid price or discount)
Running fuzz tests...
Fuzzing iteration 1: PASSED with inputs {'price': 19.24241692205497, 'discount': 68.60162489179038}
Fuzzing iteration 2: PASSED with inputs {'price': 334.27165125550397, 'discount': 16.447106935810307}

...

Fuzzing iteration 999: PASSED with inputs {'price': 612.4293011723595, 'discount': 27.494736134752873}
Fuzzing iteration 1000: PASSED with inputs {'price': 232.15767909051777, 'discount': 25.633668078376516}
----------------------------------------
Test Summary for Suite: DiscountCalculatorTests
Total Tests Run: 2
Passed: 2
Failed: 0

----------------------------------------
Fuzzing Summary for Function: DiscountCalculatorFuzzing
Total Iterations: 1000
Passed: 1000
Failed: 0
```

# 🧠 How It Works

## Code Analysis

PyVeritas inspects your code for patterns, structure, and dependencies.

## Test Generation

Automatically generates tests based on code analysis and input specifications.

## Execution

Runs the tests with real-time metrics on coverage and edge-case detection.

# Insights

Provides actionable feedback, including risk areas and potential optimizations.

# 🛡️ Why PyVeritas?
PyVeritas doesn’t just test—it thinks. By leveraging machine learning, dynamic adaptation, and intelligent fuzzing, PyVeritas ensures you catch bugs that other tools miss. Whether you’re developing simple scripts or large-scale applications, PyVeritas is your ultimate testing companion.

# 🏗️ Roadmap
- [ ] Build the foundational test suite framework.
- [ ] Integrate intelligent fuzzing with customizable input specifications.
- [ ] Develop AI-driven behavioural models for output validation.
- [ ] Add cross-environment compatibility testing.
- [ ] Create a comprehensive feedback and insights dashboard.
- [ ] Write comprehensive documentation
- [ ] Create contribution guide

# 📚 Documentation

Comprehensive documentation is available at PyVeritas Docs.

# 🖤 Contributing
Contributions are welcome! Please read our CONTRIBUTING.md for guidelines on how to get started.

# 📝 License

This project is licensed under the Apache2 License. See the LICENSE file for details.
