# pyveritas/fuzzer.py
import random
from colorama import Fore, Style

class VeritasFuzzer:
    @staticmethod
    def choice(options):
        return random.choice(options)

    @staticmethod
    def float_range(min_value, max_value):
        return random.uniform(min_value, max_value)

    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.failed_inputs = []
        self.input_spec = None
        self.iterations = 100

    def test(self, input_spec, iterations=100):
        self.input_spec = input_spec
        self.iterations = iterations

    def run(self, function):
        if not self.input_spec:
            raise ValueError("Input specification not set. Please call 'test()' first.")
        
        print(f"Running fuzz tests on function: {function.__name__}")
        for i in range(self.iterations):
            inputs = {key: spec() for key, spec in self.input_spec.items()}
            try:
                function(**inputs)
                self.passed += 1
                print(f"{Fore.GREEN}Fuzzing iteration {i+1}: PASSED with inputs {inputs}{Style.RESET_ALL}")
            except Exception as e:
                self.failed += 1
                self.failed_inputs.append((inputs, e))
                print(f"{Fore.RED}Fuzzing iteration {i+1}: FAILED with inputs {inputs} (Exception: {e}){Style.RESET_ALL}")
        
        self.summary()

    def summary(self):
        print("\n" + "-" * 40)
        print(f"Fuzzing Summary for Function: {self.name}")
        print(f"Total Iterations: {self.passed + self.failed}")
        print(f"{Fore.GREEN}Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.failed}{Style.RESET_ALL}")
        if self.failed_inputs:
            print("\nFailed Inputs:")
            for inputs, e in self.failed_inputs:
                print(f"  - Inputs: {inputs}, Exception: {e}")
