import time
import sys

# --- Configuration ---
TEST_DURATION = 10  # seconds - how long the test will run
MAX_NUMBER_TO_CHECK = 200000 # Starting upper limit for prime checking, will adjust dynamically if needed

# --- Prime Number Checking Function ---
def is_prime(n):
    """
    Checks if a number is prime using trial division.
    """
    if n < 2:
        return False
    # Only need to check divisors up to the square root of n
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# --- Main CPU Test Logic ---
def run_cpu_test():
    start_time = time.time()
    primes_found = 0
    current_number = 2 # Start checking for primes from 2

    print("-------------------------")
    print("   CPU Performance Test  ")
    print(" (Prime Number Generation) ")
    print("-------------------------")

    # Run the test for the specified duration
    while time.time() - start_time < TEST_DURATION:
        if is_prime(current_number):
            primes_found += 1
        current_number += 1

    end_time = time.time()
    time_taken = end_time - start_time

    print(f"Total Primes Found: {primes_found}")
    print(f"Time Taken: {time_taken:.2f} seconds")

# --- Run the test ---
if __name__ == "__main__":
    run_cpu_test()
    sys.exit() # Ensure the script exits cleanly
