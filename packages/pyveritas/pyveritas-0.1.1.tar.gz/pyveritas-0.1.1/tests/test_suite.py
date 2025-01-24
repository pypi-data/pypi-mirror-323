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