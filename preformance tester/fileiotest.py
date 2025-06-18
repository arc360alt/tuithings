import time
import sys
import os
import random

# --- Configuration ---
TEST_DURATION = 10  # seconds
FILE_SIZE_MB = 100 # Size of the temporary file to create/read in MB
BLOCK_SIZE_KB = 4 # Size of each block to write/read in KB (common disk block size)
TEMP_FILE_NAME = "temp_io_test_file.bin"

# Convert sizes to bytes
FILE_SIZE_BYTES = FILE_SIZE_MB * 1024 * 1024
BLOCK_SIZE_BYTES = BLOCK_SIZE_KB * 1024

# --- Main File I/O Test Logic ---
def run_file_io_test():
    total_bytes_written = 0
    total_bytes_read = 0
    write_start_time = 0
    read_start_time = 0

    print("-------------------------")
    print("   File I/O Performance Test")
    print("-------------------------")

    # Generate random data for writing
    # Generate once to avoid CPU bottleneck during write test
    data_to_write = os.urandom(BLOCK_SIZE_BYTES)

    try:
        # --- Write Test ---
        print(f"Starting write test for {TEST_DURATION} seconds...")
        write_start_time = time.time()
        with open(TEMP_FILE_NAME, "wb") as f:
            while time.time() - write_start_time < TEST_DURATION:
                f.write(data_to_write)
                total_bytes_written += BLOCK_SIZE_BYTES
        write_end_time = time.time()
        write_time_taken = write_end_time - write_start_time
        write_speed_mbps = (total_bytes_written / (1024 * 1024)) / write_time_taken if write_time_taken > 0 else 0
        print(f"Total Bytes Written: {total_bytes_written / (1024 * 1024):.2f} MB")
        print(f"Write Speed: {write_speed_mbps:.2f} MB/s")

        # Ensure the file exists for reading
        if not os.path.exists(TEMP_FILE_NAME) or os.path.getsize(TEMP_FILE_NAME) == 0:
            print("Warning: No data written to perform read test. Skipping read test.")
            return

        # --- Read Test ---
        print(f"Starting read test for {TEST_DURATION} seconds...")
        read_start_time = time.time()
        while time.time() - read_start_time < TEST_DURATION:
            with open(TEMP_FILE_NAME, "rb") as f:
                while True:
                    chunk = f.read(BLOCK_SIZE_BYTES)
                    if not chunk: # End of file
                        f.seek(0) # Go back to beginning to read again
                        break
                    total_bytes_read += len(chunk)
        read_end_time = time.time()
        read_time_taken = read_end_time - read_start_time
        read_speed_mbps = (total_bytes_read / (1024 * 1024)) / read_time_taken if read_time_taken > 0 else 0
        print(f"Total Bytes Read: {total_bytes_read / (1024 * 1024):.2f} MB")
        print(f"Read Speed: {read_speed_mbps:.2f} MB/s")

    finally:
        # Clean up the temporary file
        if os.path.exists(TEMP_FILE_NAME):
            os.remove(TEMP_FILE_NAME)
            print(f"Cleaned up temporary file: {TEMP_FILE_NAME}")

# --- Run the test ---
if __name__ == "__main__":
    run_file_io_test()
    sys.exit()
