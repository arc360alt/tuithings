#!/usr/bin/env python3
import platform
import os
import socket
import psutil
import subprocess
import re
import sys # Import sys for command-line arguments

# --- ANSI Color Definitions ---
ANSI_COLORS = {
    # Standard foreground colors
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    # Bright foreground colors
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    # Background colors (primarily for splotches)
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
    # Reset color/formatting
    "reset": "\033[0m",
}

# --- System Information Gathering ---
def get_system_info():
    info = {}

    # OS and Kernel
    info['OS'] = platform.system()
    info['Kernel'] = platform.release()

    # Hostname
    info['Hostname'] = socket.gethostname()

    # Uptime
    if info['OS'] == 'Linux':
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                
                total_seconds_int = int(uptime_seconds)
                days = total_seconds_int // (24 * 3600)
                remaining_seconds = total_seconds_int % (24 * 3600)
                hours = remaining_seconds // 3600
                remaining_seconds %= 3600
                minutes = remaining_seconds // 60

                info['Uptime'] = f"{int(days)}d {int(hours)}h {int(minutes)}m"
        except FileNotFoundError:
            info['Uptime'] = 'N/A'
    elif info['OS'] == 'Windows':
        from datetime import datetime
        try:
            output = subprocess.check_output('systeminfo | find "Boot Time"', shell=True, universal_newlines=True).strip()
            match = re.search(r'Boot Time:\s*(.+)', output)
            if match:
                boot_time_str = match.group(1).strip()
                try:
                    boot_dt = datetime.strptime(boot_time_str, '%m/%d/%Y, %I:%M:%S %p')
                except ValueError:
                    try:
                        boot_dt = datetime.strptime(boot_time_str, '%d/%m/%Y, %H:%M:%S')
                    except ValueError:
                        boot_dt = None

                if boot_dt:
                    current_dt = datetime.now()
                    uptime_delta = current_dt - boot_dt
                    total_seconds = int(uptime_delta.total_seconds())

                    days = total_seconds // (24 * 3600)
                    remaining_seconds = total_seconds % (24 * 3600)
                    hours = remaining_seconds // 3600
                    remaining_seconds %= 3600
                    minutes = remaining_seconds // 60

                    info['Uptime'] = f"{int(days)}d {int(hours)}h {int(minutes)}m"
                else:
                    info['Uptime'] = f"Since {boot_time_str} (parse error)"
            else:
                info['Uptime'] = 'N/A'
        except Exception as e:
            info['Uptime'] = f'N/A ({e})'


    # CPU
    info['CPU'] = platform.processor()
    if info['OS'] == 'Linux':
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        info['CPU'] = line.split(':')[-1].strip()
                        break
        except FileNotFoundError:
            pass

    # GPU
    if info['OS'] == 'Linux':
        gpu_names = []
        try:
            lspci_output = subprocess.check_output(['lspci', '-k'], universal_newlines=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            if "Operation not permitted" in e.stderr or "Permission denied" in e.stderr:
                print("ArkFetch: Attempting GPU detection with 'sudo lspci'. You may be prompted for your password.")
                try:
                    lspci_output = subprocess.check_output(['sudo', 'lspci', '-k'], universal_newlines=True)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    lspci_output = ""
            else:
                lspci_output = ""
        except FileNotFoundError:
            lspci_output = ""

        if lspci_output:
            for line in lspci_output.splitlines():
                match = re.search(r'(?:VGA compatible controller|3D controller):\s*(.*)', line)
                if match:
                    gpu_names.append(match.group(1).strip())
            if gpu_names:
                info['GPU'] = ", ".join(gpu_names)
            else:
                info['GPU'] = 'N/A (No compatible GPU found by lspci)'
        else:
            info['GPU'] = 'N/A (Install pciutils or run script with sudo)'
    elif info['OS'] == 'Windows':
        try:
            wmic_output = subprocess.check_output(['wmic', 'path', 'win32_videocontroller', 'get', 'name'], universal_newlines=True)
            gpu_names = [line.strip() for line in wmic_output.splitlines() if line.strip() and "Name" not in line]
            if gpu_names:
                info['GPU'] = ", ".join(gpu_names)
            else:
                info['GPU'] = 'N/A'
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['GPU'] = 'N/A (Check Device Manager)'


    # Memory
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    available_gb = mem.available / (1024**3)
    info['Memory'] = f"{available_gb:.2f} GB / {total_gb:.2f} GB"

    # Disk Usage (Root partition for Linux, C: drive for Windows)
    if info['OS'] == 'Linux':
        try:
            disk_usage = psutil.disk_usage('/')
            total_disk_gb = disk_usage.total / (1024**3)
            used_disk_gb = disk_usage.used / (1024**3)
            info['Disk'] = f"{used_disk_gb:.2f} GB / {total_disk_gb:.2f} GB (root)"
        except Exception:
            info['Disk'] = 'N/A'
    elif info['OS'] == 'Windows':
        try:
            disk_usage = psutil.disk_usage('C:\\')
            total_disk_gb = disk_usage.total / (1024**3)
            used_disk_gb = disk_usage.used / (1024**3)
            info['Disk'] = f"{used_disk_gb:.2f} GB / {total_disk_gb:.2f} GB (C:)"
        except Exception:
            info['Disk'] = 'N/A'

    # Shell
    info['Shell'] = os.environ.get('SHELL', 'N/A')
    if info['OS'] == 'Windows':
        info['Shell'] = os.environ.get('ComSpec', 'N/A')
        if 'powershell' in info['Shell'].lower():
            info['Shell'] = 'PowerShell'
        elif 'cmd.exe' in info['Shell'].lower():
            info['Shell'] = 'CMD'
        else:
            info['Shell'] = 'Unknown Windows Shell'

    # Terminal
    info['Terminal'] = os.environ.get('TERM', 'N/A')
    if info['OS'] == 'Windows':
        if 'WT_SESSION' in os.environ:
            info['Terminal'] = 'Windows Terminal'
        elif 'ConEmuPID' in os.environ:
            info['Terminal'] = 'ConEmu'
        elif 'MSYSTEM' in os.environ:
            info['Terminal'] = 'Msys/Cygwin Terminal'
        else:
            info['Terminal'] = 'Unknown Windows Terminal'

    # Window Manager (Linux only)
    if info['OS'] == 'Linux':
        info['WM'] = 'N/A'
        if os.environ.get('XDG_CURRENT_DESKTOP'):
            info['WM'] = os.environ.get('XDG_CURRENT_DESKTOP')
        elif os.environ.get('DESKTOP_SESSION'):
            info['WM'] = os.environ.get('DESKTOP_SESSION')
        elif os.environ.get('XDG_SESSION_DESKTOP'):
            info['WM'] = os.environ.get('XDG_SESSION_DESKTOP')

        if info['WM'] == 'N/A' or info['WM'].lower() in ['gnome', 'kde', 'xfce'] : # Try wmctrl if env vars aren't specific
            try:
                wmctrl_output = subprocess.check_output(['wmctrl', '-m'], universal_newlines=True, stderr=subprocess.PIPE)
                match = re.search(r'Name: (.+)', wmctrl_output)
                if match:
                    info['WM'] = match.group(1).strip()
                else:
                    info['WM'] = f"N/A (wmctrl found, but couldn't parse WM name)"
            except (FileNotFoundError, subprocess.CalledProcessError):
                info['WM'] = f"N/A (Install wmctrl or check display)"
        
        # Clean up common desktop environment names for display
        if info['WM'].lower() == 'gnome': info['WM'] = 'GNOME'
        elif info['WM'].lower() == 'kde': info['WM'] = 'KDE Plasma'
        elif info['WM'].lower() == 'xfce': info['WM'] = 'XFCE'
        elif info['WM'].lower() == 'cinnamon': info['WM'] = 'Cinnamon'
        elif info['WM'].lower() == 'mate': info['WM'] = 'MATE'
        elif info['WM'].lower() == 'lxde': info['WM'] = 'LXDE'
        elif info['WM'].lower() == 'budgie': info['WM'] = 'Budgie'
        elif info['WM'].lower() == 'pantheon': info['WM'] = 'Pantheon'
    else:
        info['WM'] = 'N/A (Windows does not have a "Window Manager" in the same sense)'

    # Display Resolution (for multiple monitors)
    if info['OS'] == 'Linux':
        resolutions = []
        try:
            xrandr_output = subprocess.check_output(['xrandr'], universal_newlines=True)
            for line in xrandr_output.splitlines():
                if " connected" in line:
                    match = re.search(r'(\S+)\s+connected(?:\s+primary)?\s+(\d+x\d+)(?:\+\d+\+\d+)?', line)
                    if match:
                        monitor_name = match.group(1)
                        resolution = match.group(2)
                        resolutions.append(f"{monitor_name}: {resolution}")
            if resolutions:
                info['Resolution'] = ", ".join(resolutions)
            else:
                info['Resolution'] = 'N/A (No active display found by xrandr)'
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['Resolution'] = 'N/A (Install xrandr or check manually)'
    elif info['OS'] == 'Windows':
        resolutions = []
        try:
            wmic_output = subprocess.check_output(['wmic', 'desktopmonitor', 'get', 'ScreenWidth,ScreenHeight,MonitorManufacturer,MonitorType /value'], universal_newlines=True)
            monitor_data = {}
            for line in wmic_output.splitlines():
                line = line.strip()
                if not line:
                    if monitor_data:
                        width = monitor_data.get('ScreenWidth')
                        height = monitor_data.get('ScreenHeight')
                        manufacturer = monitor_data.get('MonitorManufacturer', 'Unknown')
                        monitor_type = monitor_data.get('MonitorType', 'Monitor')
                        if width and height:
                            resolutions.append(f"{monitor_type} ({manufacturer}): {width}x{height}")
                        monitor_data = {}
                    continue
                parts = line.split('=', 1)
                if len(parts) == 2:
                    monitor_data[parts[0].strip()] = parts[1].strip()
            if monitor_data: # Process the last monitor if any data remains
                width = monitor_data.get('ScreenWidth')
                height = monitor_data.get('ScreenHeight')
                manufacturer = monitor_data.get('MonitorManufacturer', 'Unknown')
                monitor_type = monitor_data.get('MonitorType', 'Monitor')
                if width and height:
                    resolutions.append(f"{monitor_type} ({manufacturer}): {width}x{height}")

            if resolutions:
                info['Resolution'] = ", ".join(resolutions)
            else:
                info['Resolution'] = 'N/A'
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['Resolution'] = 'N/A'

    # Username
    try:
        info['User'] = os.getlogin()
    except OSError: # FileNotFoundError is a subclass of OSError
        info['User'] = os.environ.get('USER') or os.environ.get('USERNAME', 'N/A')

    return info

# --- ASCII Art and Output Generation ---
def load_ascii_art(file_path=None):
    # Default ASCII art colors and footer message
    ascii_art_color_name = "white"
    text_color_name = "white"
    footer_message = "ArkFetch: Your System Overview"

    # Default ASCII art if no file is specified or found
    default_ascii_art = [
        "    /\\    ",
        "   /  \\   ",
        "  / /\\ \\  ",
        " / ____ \\ ",
        "/_/    \\_\\"
    ]
    art_lines = [] # Initialize art_lines to an empty list

    def process_art_file_content(lines_from_file):
        nonlocal ascii_art_color_name, text_color_name, footer_message, art_lines
        
        # Read color lines
        if len(lines_from_file) >= 1 and lines_from_file[0].strip(): # Only use if not blank
            ascii_art_color_name = lines_from_file[0].strip().lower()
        if len(lines_from_file) >= 2 and lines_from_file[1].strip(): # Only use if not blank
            text_color_name = lines_from_file[1].strip().lower()
        if len(lines_from_file) >= 3 and lines_from_file[2].strip(): # Only use if not blank
            footer_message = lines_from_file[2].strip()
        
        art_lines = lines_from_file[3:] # Remaining lines are the actual art

        # Ensure all lines have the same length for proper alignment
        if art_lines:
            max_len = max(len(line) for line in art_lines)
            art_lines = [line.ljust(max_len) for line in art_lines]
        else:
            art_lines = default_ascii_art # Fallback if art file is just colors or empty

    if file_path: # Scenario 1: User specified a file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip() for line in f]
            process_art_file_content(lines)
        except FileNotFoundError:
            print(f"ArkFetch: Warning: ASCII art file '{file_path}' not found. Using default 'A' art and colors.")
            art_lines = default_ascii_art # Assign default here
        except Exception as e:
            print(f"ArkFetch: Warning: Error reading ASCII art file '{file_path}': {e}. Using default 'A' art and colors.")
            art_lines = default_ascii_art # Assign default here
    else: # Scenario 2: No file specified by user (check default 'arkfetch_ascii.txt')
        default_file_name = "arkfetch_ascii.txt"
        try:
            with open(default_file_name, 'r', encoding='utf-8') as f:
                lines = [line.rstrip() for line in f]
            process_art_file_content(lines)
        except FileNotFoundError:
            # If the default file isn't found, explicitly set default art.
            art_lines = default_ascii_art
        except Exception as e:
            print(f"ArkFetch: Warning: Error reading default ASCII art file '{default_file_name}': {e}. Using default 'A' art and colors.")
            art_lines = default_ascii_art # Assign default here

    # Validate colors and get ANSI codes
    ascii_art_color_code = ANSI_COLORS.get(ascii_art_color_name, ANSI_COLORS["white"])
    text_color_code = ANSI_COLORS.get(text_color_name, ANSI_COLORS["white"])
    
    return ascii_art_color_code, text_color_code, art_lines, footer_message

def generate_color_splotches():
    """Generates a string of 8 standard terminal color blocks."""
    splotches = ""
    colors = ["bg_black", "bg_red", "bg_green", "bg_yellow", "bg_blue", "bg_magenta", "bg_cyan", "bg_white"]
    for color_name in colors:
        splotches += ANSI_COLORS.get(color_name, "") + "   " + ANSI_COLORS["reset"] + " "
    return splotches.strip()

def generate_arkfetch_output(system_info, ascii_art_color_code, text_color_code, ascii_art_content):
    max_key_len = max(len(key) for key in system_info.keys()) if system_info else 0
    info_keys_order = [
        'OS', 'Kernel', 'Hostname', 'Uptime', 'CPU', 'GPU', 'Memory', 'Disk',
        'Resolution', 'Shell', 'Terminal', 'WM', 'User'
    ]

    ascii_art_width = max(len(line) for line in ascii_art_content) if ascii_art_content else 0

    output_lines = []
    
    num_info_lines = len(info_keys_order)
    
    # The total height should accommodate either the ASCII art or the info lines + splotch line
    total_output_height = max(len(ascii_art_content), num_info_lines + 1)

    for i in range(total_output_height):
        art_line = ascii_art_content[i] if i < len(ascii_art_content) else " " * ascii_art_width
        info_line = ""

        if i < num_info_lines: # This is a regular system info line
            key = info_keys_order[i]
            value = system_info.get(key, 'N/A')
            info_line = f"{key.ljust(max_key_len)}: {value}"
        elif i == num_info_lines: # This is the line immediately after the last info line
            # Removed the specific padding. The 'info_line' variable itself
            # now starts at the left-most position of the info column.
            info_line = generate_color_splotches()
            
        # Apply colors and reset for each part
        output_lines.append(f"{ascii_art_color_code}{art_line}{ANSI_COLORS['reset']}   {text_color_code}{info_line}{ANSI_COLORS['reset']}")

    return "\n".join(output_lines)

def main():
    ascii_art_file = None
    if len(sys.argv) > 1:
        ascii_art_file = sys.argv[1] # Get file path from command-line argument

    ascii_art_color_code, text_color_code, ascii_art_content, footer_message = load_ascii_art(ascii_art_file)

    print("Gathering system information...")
    system_info = get_system_info()
    
    # Generate the main output block which now includes the splotches
    output_block = generate_arkfetch_output(system_info, ascii_art_color_code, text_color_code, ascii_art_content)
    print("\n" + output_block)

    # Print the customizable footer message
    print(f"\n{footer_message}")

if __name__ == "__main__":
    main()