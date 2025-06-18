import time
import sys
import gc # Import garbage collector to force collection

# --- Configuration ---
TEST_DURATION = 10  # seconds
ALLOCATION_SIZE_ELEMENTS = 100000 # Number of integers in each list created
ALLOCATION_CYCLES_PER_REPORT = 10 # Report progress every X cycles

# --- Main Memory Test Logic ---
def run_memory_test():
    start_time = time.time()
    total_allocations = 0
    test_list = [] # This list will hold our allocated 'blocks'
    cycle_count = 0

    print("-------------------------")
    print("   Memory Performance Test")
    print(" (Allocation/Deallocation) ")
    print("-------------------------")

    while time.time() - start_time < TEST_DURATION:
        # Allocate: Create a new large list
        test_list.append(list(range(ALLOCATION_SIZE_ELEMENTS)))
        total_allocations += 1

        cycle_count += 1

        # Periodically deallocate to simulate churn and prevent excessive memory usage
        if cycle_count % ALLOCATION_CYCLES_PER_REPORT == 0:
            if test_list: # Ensure there's something to pop
                test_list.pop(0) # Remove the oldest allocated block
            gc.collect() # Force garbage collection

    end_time = time.time()
    time_taken = end_time - start_time

    print(f"Total Allocation Cycles: {total_allocations}")
    print(f"Time Taken: {time_taken:.2f} seconds")

# --- Run the test ---
if __name__ == "__main__":
    run_memory_test()
    sys.exit()
