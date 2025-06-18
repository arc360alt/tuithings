import subprocess
import re
import os
import time # Needed for sleeping while server starts

# --- Configuration ---
# Define the names of your test scripts.
# Ensure these files are in the same directory as this orchestrator script,
# or provide their full paths.
SCRIPT_2D_TEST = "2dtest.py"
SCRIPT_3D_TEST = "3dtest.py"
SCRIPT_MC_SEEDGEN = "mcseedgen.py"
SCRIPT_CPU_TEST = "cputest.py"
SCRIPT_MEMORY_TEST = "memorytest.py"
SCRIPT_FILE_IO_TEST = "fileiotest.py"
SCRIPT_SIMULATED_GPU_TEST = "gputest.py" # Renamed for clarity
SCRIPT_REAL_GPU_TEST = "real_gputest.py" # Actual GPU test
SCRIPT_NET_SERVER = "nettest_server.py" # Server part of network test
SCRIPT_NET_CLIENT = "nettest_client.py" # Client part of network test

# --- Function to Run a Script and Capture its Output ---
def run_script_and_capture_output(script_path, wait=True):
    """
    Runs a given Python script and captures its standard output.

    Args:
        script_path (str): The file path to the Python script to run.
        wait (bool): If True, waits for the script to complete. If False, runs in background.

    Returns:
        tuple: If wait=True: (success_boolean, output_string, error_string)
               If wait=False: (subprocess.Popen object, None, None)
    """
    print(f"\n--- Running {script_path} ---")
    if not os.path.exists(script_path):
        print(f"Error: Script '{script_path}' not found. Skipping.")
        if wait:
            return False, "", f"Script '{script_path}' not found."
        else:
            return None, None, None # For non-waiting processes

    try:
        if wait:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Warning: {script_path} exited with error code {result.returncode}")
                if result.stderr:
                    print(f"  Stderr:\n{result.stderr}")
                if result.stdout:
                    print(f"  Stdout (partial):\n{result.stdout[:500]}...")
                return False, result.stdout, result.stderr
            return True, result.stdout, result.stderr
        else:
            # Run in background (e.g., for server)
            process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process, None, None # Return the process object
    except Exception as e:
        print(f"An error occurred while running {script_path}: {e}")
        if wait:
            return False, "", str(e)
        else:
            return None, None, None

# --- Functions to Parse Script Outputs ---

def parse_2d_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Total Sprites Generated:" in line:
            match = re.search(r"Total Sprites Generated: (\d+)", line)
            if match:
                stats['2D Total Sprites'] = int(match.group(1))
        elif "Lowest FPS:" in line:
            match = re.search(r"Lowest FPS: ([\d.]+)", line)
            if match:
                stats['2D Lowest FPS'] = float(match.group(1))
        elif "Highest FPS:" in line:
            match = re.search(r"Highest FPS: ([\d.]+)", line)
            if match:
                stats['2D Highest FPS'] = float(match.group(1))
        elif "Average FPS:" in line:
            match = re.search(r"Average FPS: ([\d.]+)", line)
            if match:
                stats['2D Average FPS'] = float(match.group(1))
    return stats

def parse_3d_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Total Cubes Generated:" in line:
            match = re.search(r"Total Cubes Generated: (\d+)", line)
            if match:
                stats['3D Total Cubes'] = int(match.group(1))
        elif "Lowest FPS:" in line:
            match = re.search(r"Lowest FPS: ([\d.]+)", line)
            if match:
                stats['3D Lowest FPS'] = float(match.group(1))
        elif "Highest FPS:" in line:
            match = re.search(r"Highest FPS: ([\d.]+)", line)
            if match:
                stats['3D Highest FPS'] = float(match.group(1))
        elif "Average FPS:" in line:
            match = re.search(r"Average FPS: ([\d.]+)", line)
            if match:
                stats['3D Average FPS'] = float(match.group(1))
    return stats

def parse_mcseedgen_output(output):
    stats = {}
    match = re.search(r"Generated (\d+) seeds in ([\d.]+) seconds.", output)
    if match:
        stats['MC Seeds Generated'] = int(match.group(1))
        stats['MC Generation Time (s)'] = float(match.group(2))
    return stats

def parse_cpu_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Total Primes Found:" in line:
            match = re.search(r"Total Primes Found: (\d+)", line)
            if match:
                stats['CPU Primes Found'] = int(match.group(1))
        elif "Time Taken:" in line:
            match = re.search(r"Time Taken: ([\d.]+) seconds", line)
            if match:
                stats['CPU Time Taken (s)'] = float(match.group(1))
    return stats

def parse_memory_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Total Allocation Cycles:" in line:
            match = re.search(r"Total Allocation Cycles: (\d+)", line)
            if match:
                stats['Memory Allocation Cycles'] = int(match.group(1))
        elif "Time Taken:" in line:
            match = re.search(r"Time Taken: ([\d.]+) seconds", line)
            if match:
                stats['Memory Time Taken (s)'] = float(match.group(1))
    return stats

def parse_file_io_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Write Speed:" in line:
            match = re.search(r"Write Speed: ([\d.]+) MB/s", line)
            if match:
                stats['File I/O Write Speed (MB/s)'] = float(match.group(1))
        elif "Read Speed:" in line:
            match = re.search(r"Read Speed: ([\d.]+) MB/s", line)
            if match:
                stats['File I/O Read Speed (MB/s)'] = float(match.group(1))
    return stats

def parse_simulated_gpu_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Total Matrix Multiplications" in line:
            match = re.search(r"Total Matrix Multiplications \(size \d+x\d+\): (\d+)", line)
            if match:
                stats['Simulated GPU Matrix Multiplications'] = int(match.group(1))
        elif "Time Taken:" in line:
            match = re.search(r"Time Taken: ([\d.]+) seconds", line)
            if match:
                stats['Simulated GPU Time Taken (s)'] = float(match.group(1))
    return stats

def parse_real_gpu_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Total Matrix Multiplications" in line and "size" in line:
            match = re.search(r"Total Matrix Multiplications \(size \d+x\d+\): (\d+)", line)
            if match:
                stats['Real GPU Matrix Multiplications'] = int(match.group(1))
        elif "Time Taken:" in line:
            match = re.search(r"Time Taken: ([\d.]+) seconds", line)
            if match:
                stats['Real GPU Time Taken (s)'] = float(match.group(1))
    return stats


def parse_net_client_output(output):
    stats = {}
    lines = output.split('\n')
    for line in lines:
        if "Send Speed:" in line:
            match = re.search(r"Send Speed: ([\d.]+) MB/s", line)
            if match:
                stats['Net Send Speed (MB/s)'] = float(match.group(1))
        elif "Receive Speed:" in line:
            match = re.search(r"Receive Speed: ([\d.]+) MB/s", line)
            if match:
                stats['Net Receive Speed (MB/s)'] = float(match.group(1))
    return stats


# --- Main Orchestration Logic ---
def main():
    all_performance_data = {}
    net_server_process = None

    try:
        # Run 2D Pygame Test
        success_2d, output_2d, error_2d = run_script_and_capture_output(SCRIPT_2D_TEST)
        if success_2d:
            all_performance_data.update(parse_2d_output(output_2d))
        if error_2d:
            print(f"Errors from {SCRIPT_2D_TEST}:\n{error_2d}")

        # Run 3D Ursina Test
        success_3d, output_3d, error_3d = run_script_and_capture_output(SCRIPT_3D_TEST)
        if success_3d:
            all_performance_data.update(parse_3d_output(output_3d))
        if error_3d:
            print(f"Errors from {SCRIPT_3D_TEST}:\n{error_3d}")

        # Run Minecraft Seed Generator
        success_mc, output_mc, error_mc = run_script_and_capture_output(SCRIPT_MC_SEEDGEN)
        if success_mc:
            all_performance_data.update(parse_mcseedgen_output(output_mc))
        if error_mc:
            print(f"Errors from {SCRIPT_MC_SEEDGEN}:\n{error_mc}")

        # Run CPU Performance Test
        success_cpu, output_cpu, error_cpu = run_script_and_capture_output(SCRIPT_CPU_TEST)
        if success_cpu:
            all_performance_data.update(parse_cpu_output(output_cpu))
        if error_cpu:
            print(f"Errors from {SCRIPT_CPU_TEST}:\n{error_cpu}")

        # Run Memory Performance Test
        success_mem, output_mem, error_mem = run_script_and_capture_output(SCRIPT_MEMORY_TEST)
        if success_mem:
            all_performance_data.update(parse_memory_output(output_mem))
        if error_mem:
            print(f"Errors from {SCRIPT_MEMORY_TEST}:\n{error_mem}")

        # Run File I/O Performance Test
        success_fileio, output_fileio, error_fileio = run_script_and_capture_output(SCRIPT_FILE_IO_TEST)
        if success_fileio:
            all_performance_data.update(parse_file_io_output(output_fileio))
        if error_fileio:
            print(f"Errors from {SCRIPT_FILE_IO_TEST}:\n{error_fileio}")

        # Run Simulated GPU Compute Test
        success_sim_gpu, output_sim_gpu, error_sim_gpu = run_script_and_capture_output(SCRIPT_SIMULATED_GPU_TEST)
        if success_sim_gpu:
            all_performance_data.update(parse_simulated_gpu_output(output_sim_gpu))
        if error_sim_gpu:
            print(f"Errors from {SCRIPT_SIMULATED_GPU_TEST}:\n{error_sim_gpu}")

        # Run Actual GPU Compute Test
        success_real_gpu, output_real_gpu, error_real_gpu = run_script_and_capture_output(SCRIPT_REAL_GPU_TEST)
        if success_real_gpu:
            all_performance_data.update(parse_real_gpu_output(output_real_gpu))
        if error_real_gpu:
            print(f"Errors from {SCRIPT_REAL_GPU_TEST}:\n{error_real_gpu}")

        # --- Network Performance Test (Special Handling) ---
        print("\n--- Starting Network Performance Test ---")
        # Start the server in the background
        net_server_process, _, _ = run_script_and_capture_output(SCRIPT_NET_SERVER, wait=False)

        if net_server_process:
            print("Giving server a moment to start...")
            time.sleep(2) # Give the server 2 seconds to bind to the port

            # Run the client (which waits for the server)
            success_net_client, output_net_client, error_net_client = run_script_and_capture_output(SCRIPT_NET_CLIENT)
            if success_net_client:
                all_performance_data.update(parse_net_client_output(output_net_client))
            if error_net_client:
                print(f"Errors from {SCRIPT_NET_CLIENT}:\n{error_net_client}")

            # Terminate the server process
            print(f"Terminating {SCRIPT_NET_SERVER}...")
            net_server_process.terminate()
            net_server_process.wait(timeout=5) # Wait for it to terminate
            if net_server_process.poll() is None:
                print(f"Warning: {SCRIPT_NET_SERVER} did not terminate gracefully, killing.")
                net_server_process.kill()
            server_stdout, server_stderr = net_server_process.communicate() # Get any remaining output
            if server_stderr:
                print(f"Server Stderr (after termination):\n{server_stderr}")
        else:
            print("Network server failed to start, skipping client test.")

    finally:
        # Ensure server process is terminated even if other tests fail
        if net_server_process and net_server_process.poll() is None:
            print("Ensuring network server is terminated in finally block.")
            net_server_process.terminate()
            net_server_process.wait(timeout=5)
            if net_server_process.poll() is None:
                net_server_process.kill()


    # --- Comprehensive Performance Overview ---
    print("\n" + "="*30)
    print("  Comprehensive Performance Overview")
    print("="*30)

    if not all_performance_data:
        print("No performance data collected from any scripts.")
        return

    # Print collected data in a formatted way
    if '2D Total Sprites' in all_performance_data:
        print("\n--- 2D Pygame Test (Graphics) ---")
        print(f"  Total Sprites: {all_performance_data.get('2D Total Sprites', 'N/A')}")
        print(f"  Lowest FPS: {all_performance_data.get('2D Lowest FPS', 'N/A'):.2f}")
        print(f"  Highest FPS: {all_performance_data.get('2D Highest FPS', 'N/A'):.2f}")
        print(f"  Average FPS: {all_performance_data.get('2D Average FPS', 'N/A'):.2f}")

    if '3D Total Cubes' in all_performance_data:
        print("\n--- 3D Ursina Test (Graphics) ---")
        print(f"  Total Cubes: {all_performance_data.get('3D Total Cubes', 'N/A')}")
        print(f"  Lowest FPS: {all_performance_data.get('3D Lowest FPS', 'N/A'):.2f}")
        print(f"  Highest FPS: {all_performance_data.get('3D Highest FPS', 'N/A'):.2f}")
        print(f"  Average FPS: {all_performance_data.get('3D Average FPS', 'N/A'):.2f}")

    if 'MC Seeds Generated' in all_performance_data:
        print("\n--- Minecraft Seed Gen Test (Light CPU) ---")
        print(f"  Seeds Generated: {all_performance_data.get('MC Seeds Generated', 'N/A')}")
        print(f"  Generation Time: {all_performance_data.get('MC Generation Time (s)', 'N/A'):.2f} seconds")

    if 'CPU Primes Found' in all_performance_data:
        print("\n--- CPU Performance Test (Heavy CPU) ---")
        print(f"  Primes Found: {all_performance_data.get('CPU Primes Found', 'N/A')}")
        print(f"  Time Taken: {all_performance_data.get('CPU Time Taken (s)', 'N/A'):.2f} seconds")

    if 'Memory Allocation Cycles' in all_performance_data:
        print("\n--- Memory Performance Test ---")
        print(f"  Allocation Cycles: {all_performance_data.get('Memory Allocation Cycles', 'N/A')}")
        print(f"  Time Taken: {all_performance_data.get('Memory Time Taken (s)', 'N/A'):.2f} seconds")

    if 'File I/O Write Speed (MB/s)' in all_performance_data:
        print("\n--- File I/O Performance Test ---")
        print(f"  Write Speed: {all_performance_data.get('File I/O Write Speed (MB/s)', 'N/A'):.2f} MB/s")
        print(f"  Read Speed: {all_performance_data.get('File I/O Read Speed (MB/s)', 'N/A'):.2f} MB/s")

    if 'Simulated GPU Matrix Multiplications' in all_performance_data:
        print("\n--- Simulated GPU Compute Test (CPU-based) ---")
        print(f"  Matrix Multiplications: {all_performance_data.get('Simulated GPU Matrix Multiplications', 'N/A')}")
        print(f"  Time Taken: {all_performance_data.get('Simulated GPU Time Taken (s)', 'N/A'):.2f} seconds")

    if 'Real GPU Matrix Multiplications' in all_performance_data:
        print("\n--- Actual GPU Compute Test (OpenCL) ---")
        print(f"  Matrix Multiplications: {all_performance_data.get('Real GPU Matrix Multiplications', 'N/A')}")
        print(f"  Time Taken: {all_performance_data.get('Real GPU Time Taken (s)', 'N/A'):.2f} seconds")

    if 'Net Send Speed (MB/s)' in all_performance_data:
        print("\n--- Network Performance Test (Loopback) ---")
        print(f"  Send Speed: {all_performance_data.get('Net Send Speed (MB/s)', 'N/A'):.2f} MB/s")
        print(f"  Receive Speed: {all_performance_data.get('Net Receive Speed (MB/s)', 'N/A'):.2f} MB/s")


    print("\n" + "="*30)

if __name__ == "__main__":
    main()
