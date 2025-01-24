from colorama import Fore, Style

class VeritasTestSuite:
    def __init__(self, name):
        self.name = name
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.failed_tests = []

    def test(self, description, test_function, should_raise=None):
        self.tests.append((description, test_function, should_raise))

    def run(self):
        print(f"Running test suite: {self.name}")
        for i, (desc, func, should_raise) in enumerate(self.tests, 1):
            try:
                func()
                if should_raise:
                    self.failed += 1
                    self.failed_tests.append(desc)
                    print(f"{Fore.RED}Test {i} FAILED: {desc} (Exception was expected but not raised){Style.RESET_ALL}")
                else:
                    self.passed += 1
                    print(f"{Fore.GREEN}Test {i} PASSED: {desc}{Style.RESET_ALL}")
            except Exception as e:
                if should_raise and isinstance(e, should_raise):
                    self.passed += 1
                    print(f"{Fore.GREEN}Test {i} PASSED: {desc} (Expected exception raised: {e}){Style.RESET_ALL}")
                else:
                    self.failed += 1
                    self.failed_tests.append(f"{desc} (Unexpected exception: {e})")
                    print(f"{Fore.RED}Test {i} FAILED: {desc} (Unexpected exception: {e}){Style.RESET_ALL}")

        self.summary()

    def summary(self):
        print("\n" + "-" * 40)
        print(f"Test Summary for Suite: {self.name}")
        print(f"Total Tests Run: {len(self.tests)}")
        print(f"{Fore.GREEN}Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.failed}{Style.RESET_ALL}")
        if self.failed_tests:
            print("\nFailed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure}")
