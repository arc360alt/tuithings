#!/usr/bin/env python3
import platform
import os
import socket
import psutil
import subprocess
import re
import sys
import argparse
from datetime import datetime

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
    "bright_black": "\033[90m", # This will be used for borders
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

def color_text(text, color_name):
    """Apply ANSI color to text."""
    return ANSI_COLORS.get(color_name, "") + text + ANSI_COLORS["reset"]

# --- Nerd Font Symbols for Theme 2 (Updated from Fastfetch config) ---
# These require a Nerd Font to be installed and enabled in your terminal.
# The multi-color effect comes from the font's glyphs, not from Arkfetch's coloring.
NERD_FONT_SYMBOLS = {
    "PC": "",        # nf-fa-desktop (from Fastfetch)
    "CPU": "",       # nf-md-chip (from Fastfetch, for CPU)
    "GPU": "󰍛",       # nf-md-memory (from Fastfetch, surprisingly for GPU - this might be a typo in their config or intentional for a specific look)
    "Memory": "󰍛",    # nf-md-memory (from Fastfetch, used for Memory)
    "Disk": "",       # nf-md-harddisk (from Fastfetch)
    "Resolution": "󰍹", # nf-md-monitor (Keeping previous, not explicitly in fastfetch config but needed)
    "OS": "",         # nf-linux-tux (from Fastfetch)
    "Kernel": "",     # nf-fa-gear (from Fastfetch, used for Kernel and Bios)
    "Shell": "",      # nf-md-harddisk (from Fastfetch, surprisingly used for Shell too - this might be a typo in their config or intentional for a specific look)
    "Terminal": "",   # nf-dev-terminal (from Fastfetch)
    "WM": "", 
    "DE": "",         # nf-md-palette (from Fastfetch)
    "LM": "",         # Display Manager (Fastfetch uses 'lm' - login manager)
    "User": "󰈡",       # nf-fa-user (Keeping previous, not explicitly in fastfetch config)
    "Uptime": "󰃭",      # nf-md-timer (Keeping previous, not explicitly in fastfetch config)
    "DateTime": "", 
    # nf-fa-clock (Keeping previous, not explicitly in fastfetch config)
    "OS Age": "󰃰",      # nf-fa-clock_o (Keeping previous, not explicitly in fastfetch config)
    "Packages": "󰏖", # nf-md-package (from Fastfetch)
    "Display Manager": "", # nf-md-palette (Mapping 'lm' to this for Arkfetch)
    "Theme": "󰉼",       # nf-md-palette (from Fastfetch, used for wmtheme)
    "BIOS": "",        # From Fastfetch for bios
}

# --- Box Drawing Characters ---
BOX_CHARS = {
    "top_left": "┌",
    "top_right": "┐",
    "bottom_left": "└",
    "bottom_right": "┘",
    "horizontal": "─",
    "vertical": "│",
    "tree_branch": "├", # For "│ ├"
    "tree_corner": "└", # For "└ └"
}

# --- System Information Gathering ---
def get_system_info():
    info = {}

    # OS and Kernel
    info['OS'] = platform.system()
    if info['OS'] == 'Linux':
        try:
            lsb_release_output = subprocess.check_output(['lsb_release', '-sd'], 
universal_newlines=True).strip()
            info['OS'] = f"{lsb_release_output} {platform.machine()}"
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['OS'] = f"{info['OS']} {platform.version().split('-')[0].strip()} {platform.machine()}" # Fallback
    elif info['OS'] == 'Windows':
        info['OS'] = f"Windows {platform.version()}" # More generic Windows version

    info['Kernel'] = platform.release()

    # Hostname
    info['Hostname'] = socket.gethostname()

    # Uptime
    if info['OS'].startswith('Linux'):
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
    elif info['OS'].startswith('Windows'):
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

    # Current Date and Time
    info['CurrentDateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CPU
    info['CPU'] = platform.processor()
    if info['OS'].startswith('Linux'):
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        info['CPU'] = line.split(':')[-1].strip()
                        break
        except FileNotFoundError:
            pass

    # GPU
    if info['OS'].startswith('Linux'):
        gpu_names = []
        try:
            lspci_output = subprocess.check_output(['lspci', '-k'], universal_newlines=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            if "Operation not permitted" in e.stderr or "Permission denied" in e.stderr:
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
                    raw_gpu_name = match.group(1).strip()
                    # Clean up Linux GPU names: remove (rev xx), @ frequency, [Integrated], etc.
                    clean_gpu_name = re.sub(r'\s*\(rev [0-9a-f]+\)|@\s*[\d\.]+\s*GHz|\[Integrated\]', '', raw_gpu_name).strip()
                    gpu_names.append(clean_gpu_name)
            if gpu_names:
                info['GPU'] = gpu_names # Store as list to handle multiple lines
            else:
                info['GPU'] = 'N/A (No compatible GPU found by lspci)'
        else:
            info['GPU'] = 'N/A (Install pciutils or run script with sudo)'
    elif info['OS'].startswith('Windows'):
        try:
            wmic_output = subprocess.check_output(['wmic', 'path', 'win32_videocontroller', 'get', 'name'], universal_newlines=True)
            gpu_names = [line.strip() for line in wmic_output.splitlines() if line.strip() and "Name" not in line]
            if gpu_names:
                info['GPU'] = gpu_names # Store as list to handle multiple lines
            else:
                info['GPU'] = 'N/A'
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['GPU'] = 'N/A (Check Device Manager)'


    # Memory
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    available_gb = mem.available / (1024**3)
    info['Memory'] = f"{available_gb:.2f} GiB / {total_gb:.2f} GiB ({mem.percent}%)"

    # Disk Usage (Root partition for Linux, C: drive for Windows)
    if info['OS'].startswith('Linux'):
        try:
            disk_usage = psutil.disk_usage('/')
            total_disk_gb = disk_usage.total / (1024**3)
            used_disk_gb = disk_usage.used / (1024**3)
            fs_type = 'Unknown'
            try:
                mount_output = subprocess.check_output(['df', '-T', '/'], universal_newlines=True).strip().split('\n')
                if len(mount_output) > 1:
                    fs_type = mount_output[1].split()[1]
            except Exception:
                pass
            info['Disk'] = f"{used_disk_gb:.2f} GiB / {total_disk_gb:.2f} GiB ({disk_usage.percent}%) - {fs_type}"
        except Exception:
            info['Disk'] = 'N/A'
    elif info['OS'].startswith('Windows'):
        try:
            disk_usage = psutil.disk_usage('C:\\')
            total_disk_gb = disk_usage.total / (1024**3)
            used_disk_gb = disk_usage.used / (1024**3)
            info['Disk'] = f"{used_disk_gb:.2f} GiB / {total_disk_gb:.2f} GiB ({disk_usage.percent}%) (C:)"
        except Exception:
            info['Disk'] = 'N/A'
            
    # Resolution (Linux only for now, can be expanded for Windows)
    if info['OS'].startswith('Linux'):
        try:
            xrandr_output = subprocess.check_output(['xrandr'], universal_newlines=True)
            # Regex to find connected primary displays and their resolutions
            match = re.search(r'(\S+ (?:connected|primary) (?:.+ )?\s*(\d+x\d+)\+?.*?)(?=\n\S+ disconnected|\n\s*\S+ connected|$)', xrandr_output, re.MULTILINE)
            if match:
                # Get the full display line and resolution
                display_info = match.group(1).strip()
                resolution = match.group(2)
                # Clean up display_info to be concise (e.g., "DP-1 2560x1440")
                display_name_match = re.match(r'^(\S+)', display_info) 
                display_name = display_name_match.group(1) if display_name_match else "Unknown"
                info['Resolution'] = f"{display_name}: {resolution}"
            else:
                info['Resolution'] = 'N/A (No active display found)'
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['Resolution'] = 'N/A (xrandr not found or X not running)'
    else:
        info['Resolution'] = 'N/A' # Not implemented for Windows

    # Shell
    info['Shell'] = os.environ.get('SHELL', 'N/A')
    if info['OS'].startswith('Windows'):
        info['Shell'] = os.environ.get('ComSpec', 'N/A')
        if 'powershell' in info['Shell'].lower():
            info['Shell'] = 'PowerShell'
        elif 'cmd.exe' in info['Shell'].lower():
            info['Shell'] = 'CMD'
        else:
            info['Shell'] = 'Unknown Windows Shell'

    # Terminal
    info['Terminal'] = os.environ.get('TERM', 'N/A')
    if info['OS'].startswith('Windows'):
        if 'WT_SESSION' in os.environ:
            info['Terminal'] = 'Windows Terminal'
        elif 'ConEmuPID' in os.environ:
            info['Terminal'] = 'ConEmu'
        elif 'MSYSTEM' in os.environ:
            info['Terminal'] = 'Msys/Cygwin Terminal'
        else:
            info['Terminal'] = 'Unknown Windows Terminal'

    # Window Manager / Desktop Environment (Linux only)
    if info['OS'].startswith('Linux'):
        info['WM'] = 'N/A'
        info['DE'] = 'N/A'

        if os.environ.get('XDG_CURRENT_DESKTOP'):
            info['DE'] = os.environ.get('XDG_CURRENT_DESKTOP')
            info['WM'] = info['DE']
        elif os.environ.get('DESKTOP_SESSION'):
            session = os.environ.get('DESKTOP_SESSION')
            info['DE'] = session
            info['WM'] = session 
        elif os.environ.get('XDG_SESSION_DESKTOP'):
            info['DE'] = os.environ.get('XDG_SESSION_DESKTOP')
            info['WM'] = info['DE']

        try:
            wmctrl_output = subprocess.check_output(['wmctrl', '-m'], universal_newlines=True, stderr=subprocess.PIPE)
            match = re.search(r'Name: (.+)', wmctrl_output)
            if match:
                wm_name = match.group(1).strip()
                if info['WM'] == 'N/A' or info['WM'].lower() != wm_name.lower():
                    info['WM'] = wm_name
            if info['DE'] == 'N/A' and info['WM'] and info['WM'].lower() in ['gnome-shell', 'mutter', 'kwin_x11', 'xfwm4', 'cinnamon', 'openbox', 'awesome', 'i3']:
                info['DE'] = info['WM'].replace('-shell', '').replace('_x11', '').replace('mutter', 'GNOME').capitalize()

        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        if info['WM'].lower() == 'gnome-shell': info['WM'] = 'GNOME Shell'
        elif info['WM'].lower() == 'kde': info['WM'] = 'KDE Plasma'
        elif info['WM'].lower() == 'xfce': info['WM'] = 'XFCE'
        elif info['WM'].lower() == 'cinnamon': info['WM'] = 'Cinnamon'
        elif info['WM'].lower() == 'mate': info['WM'] = 'MATE'
        elif info['WM'].lower() == 'lxde': info['WM'] = 'LXDE'
        elif info['WM'].lower() == 'budgie': info['WM'] = 'Budgie'
        elif info['WM'].lower() == 'pantheon': info['WM'] = 'Pantheon'

    else:
        info['WM'] = 'N/A'
        info['DE'] = 'N/A'


    # Placeholder for Packages, Display Manager, Theme
    info['Packages'] = 'N/A' 
    try:
        # Example for Debian/Ubuntu based systems (dpkg)
        dpkg_count = subprocess.check_output(['dpkg', '-l'], universal_newlines=True).count('\n') - 5 # Subtract header/footer
        info['Packages'] = f"{dpkg_count} (dpkg)"
        # Try to get flatpak count
        try:
            flatpak_count = len(subprocess.check_output(['flatpak', 'list', '--app'], universal_newlines=True).splitlines()) - 1 # Subtract header
            info['Packages'] += f", {flatpak_count} (flatpak)"
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass # Keep N/A if dpkg not found


    # Simple check for common DMs (Linux) - mapping to 'LM' for fastfetch compatibility
    if info['OS'].startswith('Linux'):
        if 'DISPLAY_MANAGER' in os.environ:
            info['LM'] = os.environ.get('DISPLAY_MANAGER')
        elif 'XDG_SESSION_TYPE' in os.environ and os.environ['XDG_SESSION_TYPE'] == 'wayland':
            info['LM'] = 'Wayland'
        else: # Try systemd-related methods
            try:
                dm_output = subprocess.check_output('systemctl status display-manager.service', shell=True, universal_newlines=True, stderr=subprocess.PIPE)
                match = re.search(r'Loaded: loaded \(.*display-manager\.service;\nenabled;.*\)\n\s+Active: active \(running\)\s+since (.*)', dm_output)
                if match:
                    # Parse the output to find common DMs
                    if 'gdm' in dm_output: info['LM'] = 'GDM'
                    elif 'sddm' in dm_output: info['LM'] = 'SDDM'
                    elif 'lightdm' in dm_output: info['LM'] = 'LightDM'
                    elif 'lxdm' in dm_output: info['LM'] = 'LXDM'
                    elif 'mdm' in dm_output: info['LM'] = 'MDM'
                    else: info['LM'] = 'Running (Unknown DM)'
            except (subprocess.CalledProcessError, FileNotFoundError):
                info['LM'] = 'N/A'
    else:
        info['LM'] = 'N/A'


    # Theme - very difficult to get universally, often DE-specific
    # Mapping to 'Theme' for wmtheme in Fastfetch
    if info['OS'].startswith('Linux') and info['DE'] != 'N/A':
        if 'GNOME' in info['DE']:
            try: # GTK Theme
                gtk_theme = subprocess.check_output(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], universal_newlines=True).strip().replace("'", "")
                info['Theme'] = gtk_theme
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        elif 'KDE' in info['DE']:
            try: # Plasma Theme
                kf5_config = subprocess.check_output(['kf5-config', '--path', 'data', 'kdeglobals'], universal_newlines=True).strip().split(':')
                for path in kf5_config:
                    if os.path.exists(os.path.join(path, 'kdeglobals')):
                        with open(os.path.join(path, 'kdeglobals'), 'r') as f:
                            for line in f:
                                if 'ColorScheme=' in line:
                                    info['Theme'] = line.split('=')[1].strip()
                                    break
                        if info['Theme'] != 'N/A': break
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        elif 'XFCE' in info['DE']:
            try: # XFCE GTK Theme
                xfconf_output = subprocess.check_output(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'], universal_newlines=True).strip()
                info['Theme'] = xfconf_output
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        elif 'Cinnamon' in info['DE']: # Mint's theme
            try:
                cinnamon_theme = subprocess.check_output(['dconf', 'read', '/org/cinnamon/theme/name'], universal_newlines=True).strip().replace("'", "")
                info['Theme'] = cinnamon_theme
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

    if 'Theme' not in info or info['Theme'] == 'N/A':
        info['Theme'] = 'N/A' # Default if no specific DE theme found

    # OS Install Age
    info['OS Age'] = 'N/A'
    if info['OS'].startswith('Linux'):
        try:
            # Get inode change time of root directory
            birth_install_timestamp = int(subprocess.check_output(['stat', '-c', '%W', '/'], universal_newlines=True).strip())
            current_timestamp = int(datetime.now().timestamp())
            time_progression = current_timestamp - birth_install_timestamp
            days_difference = time_progression // 86400
            info['OS Age'] = f"{days_difference} days"
        except (FileNotFoundError, subprocess.CalledProcessError):
            info['OS Age'] = 'N/A (Could not determine OS age)'
    elif info['OS'].startswith('Windows'):
        try:
            # For Windows, we can approximate by the creation date of C:\Windows
            output = subprocess.check_output('powershell -command "(Get-ItemProperty C:\\Windows).CreationTime"', shell=True, universal_newlines=True).strip()
            creation_time_str = output
            try:
                creation_dt = datetime.strptime(creation_time_str, '%A, %B %d, %Y %I:%M:%S %p')
            except ValueError: # Try another common format
                try:
                    creation_dt = datetime.strptime(creation_time_str, '%m/%d/%Y %I:%M:%S %p')
                except ValueError:
                    creation_dt = None
            
            if creation_dt:
                current_dt = datetime.now()
                age_delta = current_dt - creation_dt
                days_difference = age_delta.days
                info['OS Age'] = f"{days_difference} days"
            else:
                info['OS Age'] = 'N/A (Failed to parse Windows install date)'
        except Exception as e:
            info['OS Age'] = f'N/A ({e})'

    # Username
    try:
        info['User'] = os.getlogin()
    except OSError:
        info['User'] = os.environ.get('USER') or os.environ.get('USERNAME', 'N/A')

    return info

# --- ASCII Art and Output Generation ---
def load_ascii_art(file_path=None):
    ascii_art_color_name = "white"
    text_color_name = "white"
    footer_message = "ArkFetch: Your System Overview"
    selected_theme_from_file = None # NEW: Variable to store theme from file

    default_ascii_art = [
        "    /\\    ",
        "   /  \\   ",
        "  / /\\ \\  ",
        " / ____ \\ ",
        "/_/    \\_/"
    ]
    art_lines = []

    def process_art_file_content(lines_from_file):
        nonlocal ascii_art_color_name, text_color_name, footer_message, art_lines, selected_theme_from_file
        
        if len(lines_from_file) >= 1 and lines_from_file[0].strip():
            ascii_art_color_name = lines_from_file[0].strip().lower()
        if len(lines_from_file) >= 2 and lines_from_file[1].strip():
            text_color_name = lines_from_file[1].strip().lower()
        if len(lines_from_file) >= 3 and lines_from_file[2].strip():
            footer_message = lines_from_file[2].strip()
        
        # NEW: Read theme from 4th line (index 3)
        if len(lines_from_file) >= 4 and lines_from_file[3].strip():
            theme_choice_str = lines_from_file[3].strip().lower()
            if theme_choice_str == "t1":
                selected_theme_from_file = 1
            elif theme_choice_str == "t2":
                selected_theme_from_file = 2
            else:
                # Optionally warn about invalid theme choice in file
                print(f"ArkFetch: Warning: Invalid theme choice '{theme_choice_str}' in ASCII art file line 4. Ignoring.")

        art_lines = lines_from_file[4:] # NEW: Start art content from line 5 (index 4)

        if art_lines:
            max_len = max(len(line) for line in art_lines)
            art_lines = [line.ljust(max_len) for line in art_lines]
        else:
            art_lines = default_ascii_art

    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip() for line in f]
            process_art_file_content(lines)
        except FileNotFoundError:
            print(f"ArkFetch: Warning: ASCII art file '{file_path}' not found.\nUsing default 'A' art and colors.")
            art_lines = default_ascii_art
        except Exception as e:
            print(f"ArkFetch: Warning: Error reading ASCII art file '{file_path}': {e}. Using default 'A' art and colors.")
            art_lines = default_ascii_art
    else:
        default_file_name = "arkfetch_ascii.txt"
        try:
            with open(default_file_name, 'r', encoding='utf-8') as f:
                lines = [line.rstrip() for line in f]
            process_art_file_content(lines)
        except FileNotFoundError:
            art_lines = default_ascii_art
        except Exception as e:
            print(f"ArkFetch: Warning: Error reading default ASCII art file '{default_file_name}': {e}. Using default 'A' art and colors.")
            art_lines = default_ascii_art

    ascii_art_color_code = ANSI_COLORS.get(ascii_art_color_name, ANSI_COLORS["white"])
    text_color_code = ANSI_COLORS.get(text_color_name, ANSI_COLORS["white"])
    
    return ascii_art_color_code, text_color_code, art_lines, footer_message, selected_theme_from_file

def generate_color_splotches():
    """Generates a string of 8 standard terminal color blocks."""
    splotches = ""
    colors = ["bg_black", "bg_red", "bg_green", "bg_yellow", "bg_blue", "bg_magenta", "bg_cyan", "bg_white"]
    for color_name in colors:
        splotches += ANSI_COLORS.get(color_name, "") + "   " + ANSI_COLORS["reset"] + " "
    return splotches.strip()

def get_display_width(text_with_ansi):
    """Calculates the display width of a string, ignoring ANSI escape codes."""
    return len(re.sub(r'\x1b\[[0-9;]*m', '', text_with_ansi))

def generate_arkfetch_output(system_info, ascii_art_color_code, text_color_code, ascii_art_content, theme_id):
    output_lines = [] 
    info_display_lines = []

    # --- Preprocessing for Theme 2: Determine max_key_display_width for consistent alignment ---
    max_key_display_width = 0 
    
    # List of all potential items that might be displayed 
    # in Theme 2 (for consistent key alignment)
    # Using the structure from Fastfetch config to determine max width
    all_potential_items_for_width = [
        ("PC", " PC"),
        ("CPU", "│ ├"),
        ("GPU", "│ ├󰍛"), # Note: Fastfetch uses 󰍛 for GPU, which is a memory icon.
        ("Memory", "│ ├󰍛"),
        ("Disk", "└ └"),
        ("OS", " OS"),
        ("Kernel", "│ ├"),
        ("Packages", "│ ├󰏖"),
        ("Shell", "└ └"), # Note: Fastfetch uses  for Shell, which is a disk icon.
        ("DE", " DE"),
        ("LM", "│ ├"), # Display Manager (Fastfetch's 'lm')
        ("WM", "│ ├"),
        ("Theme", "│ ├󰉼"), # WM Theme
        ("Terminal", "└ └"),
        ("OS Age", " OS Age"), # No icon for OS Age in fastfetch
        ("Uptime", " Uptime"),    # No icon for Uptime in fastfetch
        ("DateTime", " DateTime"), # No icon for DateTime in fastfetch
        ("User", "󰈡 User") # User isn't in fastfetch's main modules, but we'll try to include
    ]

    for key_name, formatted_key_string in all_potential_items_for_width:
        key_part_length = get_display_width(formatted_key_string)
        max_key_display_width = max(max_key_display_width, key_part_length)
    
    # Fastfetch's config shows a consistent width for its custom format bars (52 horizontal chars).
    # We'll use this for alignment of our boxes.
    FASTFETCH_BAR_CONTENT_WIDTH = 52
    
    # --- Populate info_display_lines based on Theme ---
    if theme_id == 1:
        theme1_keys_to_check = [
            'OS', 'Kernel', 'Hostname', 'Uptime', 'CPU', 'GPU', 'Memory', 'Disk',
            'Resolution', 'Shell', 'Terminal', 'WM', 'User'
        ]
        actual_keys_in_theme1 = [k for k in theme1_keys_to_check if system_info.get(k, 'N/A') != 'N/A']
        max_key_display_width_theme1 = max(len(key) for key in actual_keys_in_theme1) if actual_keys_in_theme1 else 0

        for key in theme1_keys_to_check:
            value = system_info.get(key, 'N/A')
            if value != 'N/A':
                info_display_lines.append(f"{key.ljust(max_key_display_width_theme1)}: {value}")
        info_display_lines.append(generate_color_splotches()) 

    elif theme_id == 2:
        # Define the category structure for Theme 2, aligned with Fastfetch's sections
        theme2_category_map = {
            "Hardware": [("PC", " PC", None, False),
                         ("CPU", "│ ├", None, False),
                ("GPU", "│ ├󰍛", None, False), # Using Fastfetch's GPU icon
                         ("Memory", "│ ├󰍛", None, False),
                         ("Disk", "└ └", None, True)], # Last item in section gets └ └
            "Software": [("OS", " OS", None, False),
                         ("Kernel", "│ ├", None, False),
                         ("BIOS", "│ ├", None, False), # Added BIOS
                         ("Packages", "│ ├󰏖", None, False),
                         ("Shell", "└ └", None, True)], # Using Fastfetch's Shell icon
            "DE / WM / Terminal": [("DE", " DE", None, False),
                                   ("LM", "│ ├", None, False), # Display Manager, using Fastfetch's 'lm'
                                   ("WM", "│ ├", None, False),
                                   ("Theme", "│ ├󰉼", None, False), # WM Theme
                            ("Terminal", "└ └", None, True)],
            "Uptime / Age / DT": [("OS Age", " OS Age", "0 days", False), # No icon for OS Age in fastfetch
                                  ("Uptime", " Uptime", None, False),    # No icon for Uptime in fastfetch
                                  ("DateTime", " DateTime", None, True)] # No icon for DateTime in fastfetch
        }

        # Helper to get special PC info value
        pc_info_val = system_info.get('Hostname', 'N/A')
        if system_info.get('CPU') and system_info['CPU'] != 'N/A':
            cpu_match = re.search(r'^(.*?)\s+@', system_info['CPU'])
            clean_cpu_name = cpu_match.group(1).strip() if cpu_match else system_info['CPU']
            if pc_info_val != 'N/A':
                pc_info_val = f"{pc_info_val} ({clean_cpu_name})"


        for category_name, items in theme2_category_map.items():
            current_category_content_lines = []
            
            for i, (key, formatted_key_prefix, default_val, is_last_in_section) in enumerate(items):
                value_to_display = system_info.get(key)
                
                if key == "PC":
                    value_to_display = pc_info_val
                elif key == "LM": # Map LM to Display Manager info
                    value_to_display = system_info.get('LM')
                elif key == "Theme": # Map Theme to wmtheme info
                    value_to_display = system_info.get('Theme')
                elif key == "BIOS": # Explicitly handle BIOS
                    value_to_display = system_info.get('BIOS')
                elif default_val is not None:
                    value_to_display = default_val

                # If GPU is a list, process each GPU on a new line
                if key == "GPU" and isinstance(value_to_display, list):
                    if value_to_display:
                        for j, gpu_name in enumerate(value_to_display):
                            if gpu_name == 'N/A':
                                continue
                            # Use consistent prefix for all GPU lines, like Fastfetch
                            prefix = "│ ├" if not is_last_in_section else "└ └"
                            # If it's the first GPU entry, include the icon and "GPU" text
                            key_part_for_gpu = f"{formatted_key_prefix.lstrip('│ ├└ ')}" if j == 0 else "   "
                            
                            # Reconstruct the line for multi-GPU
                            final_key_part = f"{prefix}{key_part_for_gpu.ljust(max_key_display_width - get_display_width(prefix))}"
                            current_line = f"{final_key_part}: {gpu_name}"
                            current_category_content_lines.append(current_line)
                    else:
                        continue # If GPU is N/A or empty list, skip
                else:
                    if value_to_display == 'N/A':
                        continue

                    # Determine the actual key prefix based on if it's the last in its module block
                    actual_formatted_key = formatted_key_prefix
                    
                    # Pad based on the overall max_key_display_width calculated earlier
                    # Ensure the final string length matches desired padding after prefix
                    # We need to consider the length of the symbol + space + name + any prefix (e.g., "│ ├")
                    key_portion_without_prefix = actual_formatted_key.lstrip('│ ├└ ') # Get icon + name part
                    padding_for_value = max_key_display_width - get_display_width(actual_formatted_key)
                    
                    current_line = f"{actual_formatted_key}{' ' * padding_for_value}: {value_to_display}"
                    current_category_content_lines.append(current_line)
            
            if current_category_content_lines: 
                # Category box top border
                # Calculate the width of the dashes needed based on the fixed FASTFETCH_BAR_CONTENT_WIDTH
                # This ensures the box matches Fastfetch's appearance
                category_name_display_width = get_display_width(category_name)
                
                # Fastfetch's 
                "┌──────────────────────Hardware──────────────────────┐"
                # The category name is exactly in the middle of the bar.
                # Total bar length is FASTFETCH_BAR_CONTENT_WIDTH + 2 for corners.
                # Left dashes = (FASTFETCH_BAR_CONTENT_WIDTH - category_name_display_width) / 2
                remaining_space = FASTFETCH_BAR_CONTENT_WIDTH - category_name_display_width
                left_dashes = remaining_space // 2
                right_dashes = remaining_space - left_dashes

                top_border = (
                    f"{BOX_CHARS['top_left']}"
                    f"{BOX_CHARS['horizontal'] * left_dashes}"
                    f"{category_name}"
                    f"{BOX_CHARS['horizontal'] * right_dashes}"
                    f"{BOX_CHARS['top_right']}"
                )
                info_display_lines.append(color_text(top_border, 'bright_black'))

                # Content lines
                for line in current_category_content_lines:
                    display_len = get_display_width(line)
                    # The content lines need to be padded to align with the box width.
                    # The box width is (FASTFETCH_BAR_CONTENT_WIDTH + 2 for corners)
                    # We assume 1 space of padding on each side inside the box, so FASTFETCH_BAR_CONTENT_WIDTH - 2
                    padding_needed = FASTFETCH_BAR_CONTENT_WIDTH - display_len
                    info_display_lines.append(f"{line}{' ' * padding_needed}") 
                
                # Category box bottom border
                bottom_border = f"{BOX_CHARS['bottom_left']}{BOX_CHARS['horizontal'] * FASTFETCH_BAR_CONTENT_WIDTH}{BOX_CHARS['bottom_right']}"
                info_display_lines.append(color_text(bottom_border, 'bright_black'))
                info_display_lines.append("") # Blank line after each segmented box

        # Handle standalone user info (if not N/A) - not in Fastfetch's categories but keeping it.
        # We'll make this match the fastfetch bar styling now.
        user_val = system_info.get('User', 'N/A')
        if user_val != 'N/A':
            # Fastfetch doesn't have a user module in the provided config.
            # We'll put it in its own bar that mimics the style.
            user_key_string = f"󰈡 User"
            user_line_content = f"{user_key_string.ljust(max_key_display_width)}: {user_val}"

            # Calculate content width for the user box.
            # We'll use the same FASTFETCH_BAR_CONTENT_WIDTH.
            user_box_content_width = FASTFETCH_BAR_CONTENT_WIDTH 
            
            # User box doesn't have a category name merged into the top border.
            user_top_border = f"{BOX_CHARS['top_left']}{BOX_CHARS['horizontal'] * user_box_content_width}{BOX_CHARS['top_right']}"
            info_display_lines.append(color_text(user_top_border, 'bright_black'))
            
            # Content line for user info.
            # Pad to the FASTFETCH_BAR_CONTENT_WIDTH.
            padding_needed_user = user_box_content_width - get_display_width(user_line_content)
            info_display_lines.append(f"{user_line_content}{' ' * padding_needed_user}")

            user_bottom_border = f"{BOX_CHARS['bottom_left']}{BOX_CHARS['horizontal'] * user_box_content_width}{BOX_CHARS['bottom_right']}"
            info_display_lines.append(color_text(user_bottom_border, 'bright_black'))
            info_display_lines.append("")

        # Add color splotches (as per Fastfetch's config)
        # Fastfetch uses paddingLeft: 2 and symbol: "circle"
        # We'll stick to our blocks as circles are complex with simple ANSI.
        info_display_lines.append(generate_color_splotches())
    
    # --- Combine ASCII Art and Info Lines for final output ---
    ascii_art_width = max(len(line) for line in ascii_art_content) if ascii_art_content else 0
    total_output_height = max(len(ascii_art_content), len(info_display_lines))

    for i in range(total_output_height):
        art_line = ascii_art_content[i] if i < len(ascii_art_content) else " " * ascii_art_width
        display_info_line = info_display_lines[i] if i < len(info_display_lines) else ""
        
        output_lines.append(f"{ascii_art_color_code}{art_line}{ANSI_COLORS['reset']}   {text_color_code}{display_info_line}{ANSI_COLORS['reset']}")

    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="ArkFetch: A simple system information fetcher.")
    # Theme argument is now optional, with no default, so we can detect if it was *explicitly* provided.
    parser.add_argument('-t', '--theme', type=int, choices=[1, 2],
                        help="Select display theme: 1 (original) or 2 (categorized, with lines and icons). Overrides theme specified in ASCII art file.")
    parser.add_argument('ascii_art_file', nargs='?', help="Optional path to a custom ASCII art file.")
    args = parser.parse_args()

    ascii_art_file = args.ascii_art_file
    
    # Get all information from load_ascii_art, including the new theme choice from file
    ascii_art_color_code, text_color_code, ascii_art_content, footer_message, selected_theme_from_file = load_ascii_art(ascii_art_file)

    # Determine final theme based on precedence
    selected_theme = 1 # Default theme if no other is specified
    if args.theme is not None: # Command line argument takes highest precedence
        selected_theme = args.theme
    elif selected_theme_from_file is not None: # Then check the theme from file
        selected_theme = selected_theme_from_file
    # Else, selected_theme remains 1 (the default)

    print("Gathering system information...")
    system_info = get_system_info()
    
    output_block = generate_arkfetch_output(system_info, ascii_art_color_code, text_color_code, ascii_art_content, selected_theme)
    print("\n" + output_block)
    
    print(f"\n{footer_message}")

if __name__ == "__main__":
    main()