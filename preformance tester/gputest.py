import time
import sys
import numpy as np # Used for high-performance array operations

# --- Configuration ---
TEST_DURATION = 10  # seconds
MATRIX_SIZE = 500  # Size of the square matrices (e.g., 500x500)
                   # Increase this for more intensive computation. Be mindful of RAM!

# --- Main GPU Compute Test Logic ---
def run_gpu_compute_test():
    total_operations = 0

    print("-------------------------")
    print(" Simulated GPU Compute Test")
    print(" (Matrix Multiplication with NumPy) ")
    print("-------------------------")
    print("Note: This uses NumPy and runs on CPU.")
    print("      It simulates the *type* of heavy numerical task a GPU excels at.")

    # Initialize two random matrices
    # Use float32 for potentially faster computation if a GPU backend were available
    a = np.random.rand(MATRIX_SIZE, MATRIX_SIZE).astype(np.float32)
    b = np.random.rand(MATRIX_SIZE, MATRIX_SIZE).astype(np.float32)

    start_time = time.time()

    while time.time() - start_time < TEST_DURATION:
        # Perform matrix multiplication
        _ = np.dot(a, b)
        total_operations += 1

    end_time = time.time()
    time_taken = end_time - start_time

    print(f"Total Matrix Multiplications (size {MATRIX_SIZE}x{MATRIX_SIZE}): {total_operations}")
    print(f"Time Taken: {time_taken:.2f} seconds")

# --- Run the test ---
if __name__ == "__main__":
    # Ensure numpy is installed: pip install numpy
    try:
        run_gpu_compute_test()
    except ImportError:
        print("\nError: NumPy not found. Please install it using 'pip install numpy'")
    except Exception as e:
        print(f"\nAn error occurred during the GPU compute test: {e}")
    finally:
        sys.exit()
