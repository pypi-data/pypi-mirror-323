import argparse
from pyveritas import VeritasTestSuite, VeritasFuzzer

# Pre-existing function to test
def calculate_discount(price: float, discount: float) -> float:
    if price <= 0 or discount < 0 or discount > 100:
        raise ValueError("Invalid price or discount")
    return price * (1 - discount / 100)

def run_tests():
    # Test suite
    suite = VeritasTestSuite("DiscountCalculatorTests")
    
    suite.test("Discount calculation is correct", lambda: calculate_discount(100, 20) == 80)
    suite.test("Invalid discount should raise ValueError", lambda: calculate_discount(-10, 50), should_raise=ValueError)
    
    suite.run()  # Run the test suite
    suite.summary()  # Output the summary of the test suite

def run_fuzz_tests():
    # Fuzz tests
    fuzzer = VeritasFuzzer("DiscountCalculatorFuzzing")
    
    fuzzer.test(
        input_spec={
            "price": lambda: VeritasFuzzer.float_range(0, 1000),
            "discount": lambda: VeritasFuzzer.float_range(0, 100),
        },
        iterations=1000,
    )
    fuzzer.run(calculate_discount)  # Run the fuzz tests
    fuzzer.summary()  # Output the summary of the fuzz tests

def main():
    parser = argparse.ArgumentParser(description="Run tests or fuzz tests on your Python code.")
    parser.add_argument('action', choices=['test', 'fuzz'], help="Specify 'test' to run unit tests or 'fuzz' to run fuzzing tests.")
    args = parser.parse_args()
    
    if args.action == 'test':
        run_tests()
    elif args.action == 'fuzz':
        run_fuzz_tests()

if __name__ == "__main__":
    main()
