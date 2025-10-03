#!/usr/bin/env python3
"""
arkpkg - A simple Python-based AUR helper with pacman integration
"""

import os
import sys
import subprocess
import shutil
import tempfile
import argparse
from pathlib import Path

# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}", file=sys.stderr)

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{msg}{Colors.RESET}\n")

def run_command(cmd, check=True, capture=False):
    """Run a shell command"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, check=check, 
                                   capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        return False

def check_root():
    """Check if running as root"""
    return os.geteuid() == 0

def confirm_action(prompt):
    """Ask user for confirmation"""
    response = input(f"{Colors.YELLOW}?{Colors.RESET} {prompt} [Y/n]: ").strip().lower()
    return response in ['', 'y', 'yes']

class AURHelper:
    def __init__(self):
        self.aur_base = "https://aur.archlinux.org"
        self.build_dir = Path.home() / ".cache" / "arkpkg"
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def search_aur(self, package):
        """Search for package in AUR"""
        print_info(f"Searching AUR for: {Colors.BOLD}{package}{Colors.RESET}")
        url = f"{self.aur_base}/rpc/?v=5&type=search&arg={package}"
        
        try:
            import urllib.request
            import json
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                
            if data['resultcount'] == 0:
                print_warning("No packages found in AUR")
                return []
            
            results = data['results']
            print_header(f"Found {len(results)} package(s):")
            
            for pkg in results[:10]:  # Show first 10 results
                print(f"{Colors.BOLD}{Colors.GREEN}{pkg['Name']}{Colors.RESET} {Colors.CYAN}{pkg['Version']}{Colors.RESET}")
                print(f"  {pkg.get('Description', 'No description')}")
                print(f"  Votes: {pkg.get('NumVotes', 0)} | Popularity: {pkg.get('Popularity', 0):.2f}")
                print()
            
            return results
        except Exception as e:
            print_error(f"Failed to search AUR: {e}")
            return []

    def install_aur(self, package):
        """Install package from AUR"""
        print_header(f"Installing AUR package: {package}")
        
        # Check if git is installed
        if not shutil.which('git'):
            print_error("git is required to clone AUR packages")
            return False
        
        # Clone the package
        pkg_dir = self.build_dir / package
        if pkg_dir.exists():
            print_info(f"Package directory exists. Updating...")
            if not run_command(f"cd {pkg_dir} && git pull"):
                print_error("Failed to update package")
                return False
        else:
            clone_url = f"{self.aur_base}/{package}.git"
            print_info(f"Cloning from AUR...")
            if not run_command(f"git clone {clone_url} {pkg_dir}"):
                print_error("Failed to clone package")
                return False
        
        # Show PKGBUILD
        pkgbuild = pkg_dir / "PKGBUILD"
        if not pkgbuild.exists():
            print_error("PKGBUILD not found")
            return False
        
        print_info("PKGBUILD contents:")
        print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
        with open(pkgbuild, 'r') as f:
            print(f.read())
        print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
        
        if not confirm_action("Continue with installation?"):
            print_warning("Installation cancelled")
            return False
        
        # Build and install
        print_info("Building package...")
        if not run_command(f"cd {pkg_dir} && makepkg -si"):
            print_error("Failed to build/install package")
            return False
        
        print_success(f"Successfully installed {package}")
        return True

    def remove_aur(self, package):
        """Remove AUR package using pacman"""
        return self.pacman_remove(package)

class PacmanHelper:
    @staticmethod
    def install(packages):
        """Install packages using pacman"""
        if check_root():
            print_error("Do not run as root. Use sudo when prompted.")
            return False
        
        pkg_list = ' '.join(packages)
        print_header(f"Installing packages: {pkg_list}")
        
        if run_command(f"sudo pacman -S {pkg_list}"):
            print_success("Packages installed successfully")
            return True
        else:
            print_error("Failed to install packages")
            return False

    @staticmethod
    def remove(packages):
        """Remove packages using pacman"""
        if check_root():
            print_error("Do not run as root. Use sudo when prompted.")
            return False
        
        pkg_list = ' '.join(packages)
        print_header(f"Removing packages: {pkg_list}")
        
        if run_command(f"sudo pacman -Rns {pkg_list}"):
            print_success("Packages removed successfully")
            return True
        else:
            print_error("Failed to remove packages")
            return False

    @staticmethod
    def update():
        """Update system packages"""
        if check_root():
            print_error("Do not run as root. Use sudo when prompted.")
            return False
        
        print_header("Updating system packages")
        
        if run_command("sudo pacman -Syu"):
            print_success("System updated successfully")
            return True
        else:
            print_error("Failed to update system")
            return False

    @staticmethod
    def search(query):
        """Search for packages using pacman"""
        print_info(f"Searching for: {Colors.BOLD}{query}{Colors.RESET}")
        run_command(f"pacman -Ss {query}", check=False)

    @staticmethod
    def info(package):
        """Show package information"""
        print_info(f"Package information: {Colors.BOLD}{package}{Colors.RESET}")
        run_command(f"pacman -Si {package}", check=False)

    @staticmethod
    def list_installed():
        """List installed packages"""
        print_header("Installed packages")
        run_command("pacman -Q", check=False)

class FlatpakHelper:
    @staticmethod
    def check_flatpak():
        """Check if flatpak is installed"""
        if not shutil.which('flatpak'):
            print_error("Flatpak is not installed")
            print_info("Install it with: sudo pacman -S flatpak")
            return False
        return True

    @staticmethod
    def install(packages):
        """Install flatpak applications"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        pkg_list = ' '.join(packages)
        print_header(f"Installing flatpak: {pkg_list}")
        
        if run_command(f"flatpak install -y flathub {pkg_list}"):
            print_success("Flatpak installed successfully")
            return True
        else:
            print_error("Failed to install flatpak")
            return False

    @staticmethod
    def remove(packages):
        """Remove flatpak applications"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        pkg_list = ' '.join(packages)
        print_header(f"Removing flatpak: {pkg_list}")
        
        if run_command(f"flatpak uninstall -y {pkg_list}"):
            print_success("Flatpak removed successfully")
            return True
        else:
            print_error("Failed to remove flatpak")
            return False

    @staticmethod
    def update():
        """Update all flatpak applications"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        print_header("Updating flatpak applications")
        
        if run_command("flatpak update -y"):
            print_success("Flatpaks updated successfully")
            return True
        else:
            print_error("Failed to update flatpaks")
            return False

    @staticmethod
    def search(query):
        """Search for flatpak applications"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        print_info(f"Searching flatpak for: {Colors.BOLD}{query}{Colors.RESET}")
        run_command(f"flatpak search {query}", check=False)

    @staticmethod
    def list_installed():
        """List installed flatpak applications"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        print_header("Installed flatpak applications")
        run_command("flatpak list", check=False)

    @staticmethod
    def info(package):
        """Show flatpak information"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        print_info(f"Flatpak information: {Colors.BOLD}{package}{Colors.RESET}")
        run_command(f"flatpak info {package}", check=False)

    @staticmethod
    def run_app(app):
        """Run a flatpak application"""
        if not FlatpakHelper.check_flatpak():
            return False
        
        print_info(f"Running flatpak: {Colors.BOLD}{app}{Colors.RESET}")
        run_command(f"flatpak run {app}", check=False)

def print_logo():
    """Print arkpkg logo"""
    logo = f"""
{Colors.RED}    ▄▀█ █▀█ █▄▀ █▀█ █▄▀ █▀▀
    █▀█ █▀▄ █ █ █▀▀ █ █ █▄█{Colors.RESET}
    {Colors.BOLD}Python AUR Helper & Pacman Wrapper{Colors.RESET}
    {Colors.BLUE}A tool by Arc360{Colors.RESET}
    
{Colors.BOLD}<-------------------------------------------------->{Colors.RESET}
    """
    print(logo)
    
def main():
    parser = argparse.ArgumentParser(
        description='arkpkg - A simple AUR helper with a pacman and flatpak integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BOLD}Examples:{Colors.RESET}
  arkpkg install spotify          # Install from AUR
  arkpkg pm install firefox       # Install from official repos
  arkpkg fp install org.gimp.GIMP # Install flatpak
  arkpkg remove spotify           # Remove package
  arkpkg search chrome            # Search AUR
  arkpkg pm search firefox        # Search official repos
  arkpkg fp search blender        # Search flathub
  arkpkg pm update                # Update system
  arkpkg fp update                # Update flatpaks
  arkpkg fp run org.gimp.GIMP     # Run flatpak app
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # AUR install
    install_parser = subparsers.add_parser('install', help='Install package from AUR')
    install_parser.add_argument('package', help='Package name')
    
    # AUR search
    search_parser = subparsers.add_parser('search', help='Search AUR packages')
    search_parser.add_argument('query', help='Search query')
    
    # Remove (works for all package types)
    remove_parser = subparsers.add_parser('remove', help='Remove package')
    remove_parser.add_argument('packages', nargs='+', help='Package name(s)')
    
    # Pacman subcommand
    pm_parser = subparsers.add_parser('pm', help='Pacman operations')
    pm_subparsers = pm_parser.add_subparsers(dest='pm_command', help='Pacman commands')
    
    pm_install = pm_subparsers.add_parser('install', help='Install from official repos')
    pm_install.add_argument('packages', nargs='+', help='Package name(s)')
    
    pm_remove = pm_subparsers.add_parser('remove', help='Remove packages')
    pm_remove.add_argument('packages', nargs='+', help='Package name(s)')
    
    pm_update = pm_subparsers.add_parser('update', help='Update system')
    
    pm_search = pm_subparsers.add_parser('search', help='Search official repos')
    pm_search.add_argument('query', help='Search query')
    
    pm_info = pm_subparsers.add_parser('info', help='Show package info')
    pm_info.add_argument('package', help='Package name')
    
    pm_list = pm_subparsers.add_parser('list', help='List installed packages')
    
    # Flatpak subcommand
    fp_parser = subparsers.add_parser('fp', help='Flatpak operations')
    fp_subparsers = fp_parser.add_subparsers(dest='fp_command', help='Flatpak commands')
    
    fp_install = fp_subparsers.add_parser('install', help='Install flatpak')
    fp_install.add_argument('packages', nargs='+', help='Flatpak name(s)')
    
    fp_remove = fp_subparsers.add_parser('remove', help='Remove flatpak')
    fp_remove.add_argument('packages', nargs='+', help='Flatpak name(s)')
    
    fp_update = fp_subparsers.add_parser('update', help='Update flatpaks')
    
    fp_search = fp_subparsers.add_parser('search', help='Search flathub')
    fp_search.add_argument('query', help='Search query')
    
    fp_list = fp_subparsers.add_parser('list', help='List installed flatpaks')
    
    fp_info = fp_subparsers.add_parser('info', help='Show flatpak info')
    fp_info.add_argument('package', help='Flatpak name')
    
    fp_run = fp_subparsers.add_parser('run', help='Run flatpak application')
    fp_run.add_argument('app', help='Application ID')
    
    args = parser.parse_args()
    
    if not args.command:
        print_logo()
        parser.print_help()
        return
    
    aur = AURHelper()
    pacman = PacmanHelper()
    flatpak = FlatpakHelper()
    
    try:
        if args.command == 'install':
            aur.install_aur(args.package)
        
        elif args.command == 'search':
            aur.search_aur(args.query)
        
        elif args.command == 'remove':
            pacman.remove(args.packages)
        
        elif args.command == 'pm':
            if args.pm_command == 'install':
                pacman.install(args.packages)
            elif args.pm_command == 'remove':
                pacman.remove(args.packages)
            elif args.pm_command == 'update':
                pacman.update()
            elif args.pm_command == 'search':
                pacman.search(args.query)
            elif args.pm_command == 'info':
                pacman.info(args.package)
            elif args.pm_command == 'list':
                pacman.list_installed()
            else:
                pm_parser.print_help()
        
        elif args.command == 'fp':
            if args.fp_command == 'install':
                flatpak.install(args.packages)
            elif args.fp_command == 'remove':
                flatpak.remove(args.packages)
            elif args.fp_command == 'update':
                flatpak.update()
            elif args.fp_command == 'search':
                flatpak.search(args.query)
            elif args.fp_command == 'list':
                flatpak.list_installed()
            elif args.fp_command == 'info':
                flatpak.info(args.package)
            elif args.fp_command == 'run':
                flatpak.run_app(args.app)
            else:
                fp_parser.print_help()
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()