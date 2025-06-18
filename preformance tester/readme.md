

# Performance Testing Suite

This repository contains a comprehensive suite of Python scripts designed to test various aspects of your system's performance, including 2D and 3D graphics rendering, CPU computation (light and heavy), memory management, file I/O operations, and GPU compute (both simulated and actual via OpenCL), as well as network loopback performance.

The `runme.py` script runs each test sequentially and then compiles their results into a single, easy-to-read overview in your terminal.



## 🚀 Getting Started

### 1. File Structure

Ensure all the Python scripts are in the same directory:


```
your\_project\_folder/
├── performance\_orchestrator.py
├── 2dtest.py
├── 3dtest.py
├── mcseedgen.py
├── cputest.py
├── memorytest.py
├── fileiotest.py
├── gputest.py              \# Simulated GPU test (NumPy)
├── real\_gputest.py         \# Actual GPU test (OpenCL)
├── nettest\_server.py
├── nettest\_client.py
└── requirements.txt
```


### 2. Prerequisites

* **Python 3.x:** Ensure you have Python 3 installed. You can download it from [python.org](https://www.python.org/downloads/).
* **pip:** Python's package installer. It usually comes with Python 3.

### 3. Install Python Packages

Navigate to your project directory in the terminal or command prompt and run:

```
pip install -r requirements.txt
````

### 4\. Install OS-Specific Dependencies (Crucial for GPU Tests\!)

The `real_gputest.py` (Actual GPU Compute Test) relies on OpenCL, which requires system-level drivers and development tools.

# You need some Build Tools to install the pyopencl package, heres how!

#### 4.1. For Windows Users:

  * **Microsoft Visual C++ Build Tools:** `pyopencl` needs a C/C++ compiler to build.

    1.  Go to [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/).
    2.  Scroll to "Tools for Visual Studio" and download "Build Tools for Visual Studio [latest year, e.g., 2022]".
    3.  Run the installer. In the "Workloads" tab, select **"Desktop development with C++"**. Ensure the latest "MSVC v14x - VS [Year] C++ build tools" component is checked.
    4.  Install the selected components.

  * **OpenCL Drivers/SDK for your GPU:**

      * **For AMD (e.g., Radeon 680M/660M):** OpenCL support is typically bundled within the main **AMD Software: Adrenalin Edition** graphics driver package.
        1.  Identify your exact AMD Ryzen processor model (e.g., Ryzen 5 7535U). You can find this by pressing `Win + R`, typing `msinfo32`, and pressing Enter.
        2.  Go to [AMD Drivers & Support](https://www.amd.com/en/support).
        3.  Use the "Product Selector" to find your specific Ryzen processor (e.g., Processors -\> AMD Ryzen Processors -\> AMD Ryzen 7000 Series Mobile Processors -\> AMD Ryzen 5 7535U).
        4.  Download the latest "AMD Software: Adrenalin Edition" full installer for your Windows version (Windows 10/11 64-bit).
        5.  Run the installer. It's often recommended to choose a **"Clean Install"** option if available to ensure all components, including OpenCL runtime, are correctly installed and registered. Restart your PC after installation.
      * **For NVIDIA GPUs:** Install the **NVIDIA CUDA Toolkit**. This includes the necessary OpenCL development files.
        1.  Go to [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads).
        2.  Select your OS, architecture, and version.
        3.  Download and install the toolkit, ensuring development components are selected.
      * **For Intel CPUs/Integrated Graphics:** Install the **Intel oneAPI Base Toolkit**.
        1.  Go to [Intel oneAPI Base Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html).
        2.  Download and install the appropriate version.

#### 4.2. For Linux Users:

  * **Build Essentials & Python Dev Headers:**
    ```bash
    sudo apt update
    sudo apt install build-essential python3-dev
    ```
  * **OpenCL Drivers/Development Libraries:**
      * **For AMD GPUs (ROCm):** Follow the instructions on AMD's ROCm documentation for your specific Linux distribution: [https://rocm.docs.amd.com/en/latest/](https://rocm.docs.amd.com/en/latest/). You'll typically need to add their repositories and install packages like `amdgpu-install` and then use `amdgpu-install --usecase=opencl`.
      * **For NVIDIA GPUs:** Install the **CUDA Toolkit** for Linux. This includes the OpenCL driver. Follow NVIDIA's official installation guide for your specific distribution: [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads/).
      * **For Intel CPUs/Integrated Graphics:** You might need the `intel-opencl-icd` package or Intel's specific runtime.
        ```bash
        sudo apt install intel-opencl-icd
        ```
      * **Generic (less performant, but might work):** Some systems have `mesa-opencl-icd` which provides a CPU-based OpenCL implementation (not hardware accelerated):
        ```bash
        sudo apt install mesa-opencl-icd
        ```

-----

## 🚀 How to Run the Tests

Once all prerequisites and Python packages are installed, simply run the orchestrator script from your terminal:

```bash
python runme.py
```

The script will sequentially execute each test. Graphical tests (2D Pygame, 3D Ursina) will open and close their windows. All test output will be captured and processed by the orchestrator, with a final summary printed at the end.

-----

## 💡 Interpreting Results

The `Performance Overview` section in your terminal will display key metrics for each test:

  * **2D Pygame Test (Graphics):** Sprites rendered, and minimum, maximum, and average frames per second (FPS). Higher numbers indicate better 2D rendering performance.
  * **3D Ursina Test (Graphics):** Cubes rendered, and minimum, maximum, and average frames per second (FPS). Higher numbers indicate better 3D rendering performance.
  * **Minecraft Seed Gen Test (Light CPU):** Number of seeds generated and time taken. More seeds in less time indicates better light CPU performance.
  * **CPU Performance Test (Heavy CPU):** Number of prime numbers found and time taken. More primes in less time indicates better heavy CPU performance.
  * **Memory Performance Test:** Total allocation cycles performed and time taken. More cycles in less time indicates better memory allocation/deallocation efficiency.
  * **File I/O Performance Test:** Average write and read speeds (MB/s). Higher speeds indicate faster storage performance.
  * **Simulated GPU Compute Test (CPU-based):** Number of matrix multiplications performed and time taken. This uses NumPy and runs on your CPU, simulating a GPU-like workload.
  * **Actual GPU Compute Test (OpenCL):** Number of matrix multiplications performed and time taken. This test attempts to use your dedicated GPU (or integrated GPU with OpenCL support) for computation. This will only run if `pyopencl` is installed and a compatible OpenCL device is found.
  * **Network Performance Test (Loopback):** Data sent and received, and average send/receive speeds (MB/s) for local network communication.

-----

## 🩹 Troubleshooting

### 1\. `pyopencl` installation errors (`metadata-generation-failed`, compile errors)

This is the most common issue. It means `pip` cannot build `pyopencl` because it's missing the necessary OpenCL development headers and/or a C/C++ compiler.

  * **Solution:**
      * **Windows:** You MUST install **Microsoft Visual C++ Build Tools** (see **Section 4.1**). Even if your graphics drivers are installed, the compiler and dev headers are often separate.
      * **Linux:** You MUST install `build-essential` and `python3-dev`, and the appropriate OpenCL development libraries for your GPU vendor (e.g., `libopencl-dev` or vendor-specific SDKs like NVIDIA CUDA Toolkit or AMD ROCm/APP SDK, as described in **Section 4.2**).
  * **After installing these system-level tools, open a brand new terminal window** (to ensure environment variables are updated) and retry `pip install pyopencl`.

### 2\. "No OpenCL platforms found" / "No usable OpenCL devices" (when running `real_gputest.py`)

This error indicates that `pyopencl` was installed, but it cannot detect any active OpenCL-compatible devices on your system.

  * **Solution:**
      * **Driver Issue:** Your graphics card drivers might be outdated, corrupted, or not properly installed with their OpenCL runtime component. Perform a **clean reinstallation of your latest graphics drivers** from your GPU manufacturer's official website (NVIDIA, AMD, Intel). For integrated GPUs (like AMD Radeon 680M/660M), ensure you download the full AMD Software: Adrenalin Edition package for your specific CPU model.
      * **SDK/Runtime Missing:** Even if drivers are present, the OpenCL *runtime* libraries might not be correctly registered. Refer to **Section 4.1 or 4.2** for your OS and GPU type to ensure the full OpenCL SDK or runtime is installed.
      * **Reboot:** Always reboot your system after installing or updating graphics drivers/SDKs.
      * **Check `clinfo` (Linux) / GPU-Z (Windows):** For advanced debugging, tools like `clinfo` (Linux: `sudo apt install clinfo` then `clinfo`) or GPU-Z (Windows) can show if your system correctly detects OpenCL platforms and devices.

### 3\. 2D Sprites are not visible (overlapping) in `2dtest.py`

You see the sprite count increasing, but only one red block appears to be on screen.

  * **Reason:** The duplicate sprites are spawning at the exact same location as the main sprite, stacking on top of each other.
  * **Solution:** This has already been addressed in the latest `2dtest.py` by adding `MAX_DUPLICATE_OFFSET` and randomly offsetting each duplicate. Ensure you are running the latest version of `2dtest.py` provided in the previous updates. You should see a "cloud" of randomly spread squares.

### 4\. Low FPS in 2D or 3D tests despite high duplication rate

You set `DUPLICATES_PER_FRAME` or `CUBES_PER_FRAME` high (e.g., 20), but the FPS counter immediately drops.

  * **Reason:** This is expected\! The purpose of these tests is to *stress* your system's graphics rendering. A rapid drop in FPS is actually a clear indicator that your system is working hard to render the many new objects you're creating each frame.
  * **Interpretation:** The test is working as intended. The lowest FPS recorded is a key performance metric under heavy load.

### 5\. `ConnectionRefusedError` or `BrokenPipeError` in Network Test

The network test fails, usually indicating a problem with the server.

  * **Reason:**
      * The `nettest_server.py` script might not have started correctly before the client tried to connect.
      * A firewall might be blocking the connection on port `12345`.
      * Another application is already using port `12345`.
  * **Solution:**
      * **Orchestrator Delay:** The `performance_orchestrator.py` already includes a `time.sleep(2)` to give the server time to start. If you're on a very slow system, you could try increasing this sleep duration slightly (e.g., `time.sleep(3)`).
      * **Firewall:** Ensure your firewall (Windows Defender Firewall, iptables on Linux) is not blocking Python applications or traffic on port `12345` (for `127.0.0.1`). You might need to add an exception for Python.
      * **Port in Use:** Restart your computer to clear any lingering processes that might be holding port `12345`. If the issue persists, you might need to change the `PORT` number in both `nettest_server.py` and `nettest_client.py` to something less common (e.g., `12346` or `23456`).
      * **Check Server Output:** Look closely at the `performance_orchestrator.py`'s output for any errors or warnings related to `nettest_server.py` when it attempts to start it.

<!-- end list -->
