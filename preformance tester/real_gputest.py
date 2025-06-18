import time
import sys
import numpy as np

try:
    import pyopencl as cl
    # Check if a context can be created, indicating OpenCL is available
    if not cl.get_platforms():
        raise ImportError("No OpenCL platforms found. Please ensure OpenCL drivers are installed.")
    HAVE_PYOPENCL = True
except ImportError as e:
    HAVE_PYOPENCL = False
    print(f"\nWarning: pyopencl not found or OpenCL drivers missing. This GPU test will be skipped. Error: {e}")
    print("Please install pyopencl (pip install pyopencl) and ensure your GPU drivers include OpenCL support.")
except cl.LogicError as e: # This can happen if drivers are there but no device is usable
    HAVE_PYOPENCL = False
    print(f"\nWarning: pyopencl found, but no usable OpenCL devices. This GPU test will be skipped. Error: {e}")
    print("Ensure your GPU drivers are up-to-date and include OpenCL runtime.")


# --- Configuration ---
TEST_DURATION = 10  # seconds
MATRIX_SIZE = 1024 # Size of the square matrices (e.g., 1024x1024)
                   # Larger sizes hit GPU harder but require more VRAM.
                   # Adjust based on your GPU's memory.
                   # Ensure MATRIX_SIZE is a multiple of LOCAL_MEM_SIZE for optimal performance
LOCAL_MEM_SIZE = 16 # For OpenCL work-group size (e.g., 16x16 local work group)

# OpenCL Kernel for Matrix Multiplication (C-like code)
# C = A * B
# C[i][j] = sum(A[i][k] * B[k][j])
# This kernel calculates one element of the resulting matrix C.
# Each work-item computes one element C[row][col].
MATRIX_MULT_KERNEL = """
__kernel void matrix_mult(__global float* A, __global float* B, __global float* C,
                          int M, int K, int N) {
    int row = get_global_id(0); // Current row in C
    int col = get_global_id(1); // Current column in C

    float sum = 0.0f;
    for (int k = 0; k < K; k++) {
        sum += A[row * K + k] * B[k * N + col];
    }
    C[row * N + col] = sum;
}
"""

def run_real_gpu_test():
    if not HAVE_PYOPENCL:
        print("Skipping actual GPU test due to missing pyopencl or OpenCL drivers.")
        print("Total Matrix Multiplications (size 0x0): 0")
        print("Time Taken: 0.00 seconds")
        return

    total_operations = 0
    start_time = time.time()

    print("-------------------------")
    print("  Actual GPU Compute Test")
    print(" (OpenCL Matrix Multiplication) ")
    print("-------------------------")

    try:
        # 1. Get Platform and Device
        platform = cl.get_platforms()[0] # Take the first platform
        device = platform.get_devices(device_type=cl.device_type.GPU) # Try to get a GPU device
        if not device: # Fallback to CPU if no GPU found on the chosen platform
            device = platform.get_devices(device_type=cl.device_type.CPU)
            if not device:
                print("No OpenCL GPU or CPU devices found on platform. Exiting GPU test.")
                raise Exception("No OpenCL devices available.")
            else:
                print("No GPU found, falling back to CPU for OpenCL computation.")
        device = device[0] # Use the first available device
        print(f"Using OpenCL Device: {device.name} ({cl.device_type.to_string(device.type)})")

        # 2. Create Context and Command Queue
        ctx = cl.Context([device])
        queue = cl.CommandQueue(ctx)

        # 3. Prepare Host Data (NumPy arrays)
        # Random float matrices for A and B
        # Ensure they are contiguous for OpenCL
        h_a = np.random.rand(MATRIX_SIZE, MATRIX_SIZE).astype(np.float32)
        h_b = np.random.rand(MATRIX_SIZE, MATRIX_SIZE).astype(np.float32)
        h_c = np.empty((MATRIX_SIZE, MATRIX_SIZE), dtype=np.float32) # For results

        # 4. Create Device Buffers (memory on the GPU)
        mf = cl.mem_flags
        # CL_MEM_READ_ONLY: Data will only be read by the kernel.
        # CL_MEM_WRITE_ONLY: Data will only be written by the kernel.
        # CL_MEM_COPY_HOST_PTR: Initialize with data from host.
        d_a = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=h_a)
        d_b = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=h_b)
        d_c = cl.Buffer(ctx, mf.WRITE_ONLY, h_c.nbytes) # Allocate space for results

        # 5. Compile the OpenCL Kernel
        prg = cl.Program(ctx, MATRIX_MULT_KERNEL).build()
        matrix_mult_kernel = prg.matrix_mult

        # Set kernel arguments once (if they don't change)
        matrix_mult_kernel.set_args(d_a, d_b, d_c,
                                    np.int32(MATRIX_SIZE), # M
                                    np.int32(MATRIX_SIZE), # K
                                    np.int32(MATRIX_SIZE)) # N

        # Define global and local work sizes
        # Global size: (MATRIX_SIZE, MATRIX_SIZE) - one work-item per element of C
        # Local size: (LOCAL_MEM_SIZE, LOCAL_MEM_SIZE) - how work-items are grouped
        global_size = (MATRIX_SIZE, MATRIX_SIZE)
        local_size = (LOCAL_MEM_SIZE, LOCAL_MEM_SIZE)

        # Make sure global_size is divisible by local_size
        if global_size[0] % local_size[0] != 0 or global_size[1] % local_size[1] != 0:
            print("Warning: Global size is not perfectly divisible by local size. This might impact performance.")


        # 6. Run the kernel repeatedly for TEST_DURATION
        while time.time() - start_time < TEST_DURATION:
            # Enqueue the kernel for execution
            # Returns an Event object that can be waited on
            event = cl.enqueue_nd_range_kernel(queue, matrix_mult_kernel, global_size, local_size)
            event.wait() # Wait for kernel to complete
            total_operations += 1

        end_time = time.time()
        time_taken = end_time - start_time

        # 7. Read results back (optional, not strictly for performance, but good for verification)
        # cl.enqueue_copy(queue, h_c, d_c).wait()
        # print("First 3x3 of result matrix C:")
        # print(h_c[:3, :3])

        print(f"Total Matrix Multiplications (size {MATRIX_SIZE}x{MATRIX_SIZE}): {total_operations}")
        print(f"Time Taken: {time_taken:.2f} seconds")

    except cl.LogicError as e:
        print(f"OpenCL Logic Error: {e}. This might mean no compatible device, or driver issues.")
        print("Total Matrix Multiplications (size 0x0): 0")
        print("Time Taken: 0.00 seconds")
    except Exception as e:
        print(f"An unexpected error occurred during the actual GPU compute test: {e}")
        print("Total Matrix Multiplications (size 0x0): 0")
        print("Time Taken: 0.00 seconds")


# --- Run the test ---
if __name__ == "__main__":
    run_real_gpu_test()
    sys.exit()
